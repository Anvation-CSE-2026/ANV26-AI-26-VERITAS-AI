"""Local SQLite store: users, subscriptions, usage records, payment events,
contracts, and verified analyses with account-level isolation and automatic migrations.
"""
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from uuid import uuid4

from app.config import settings
from app.services.analysis_observability import timed
from app.models.auth import UserRecord
from app.models.contracts import Analysis, AnalysisFailure, Contract


def _run_migrations(conn: sqlite3.Connection) -> None:
    """Idempotently ensures all required tables, columns, and indexes exist without losing data."""
    # 1. Base legacy tables
    conn.execute(
        "CREATE TABLE IF NOT EXISTS contracts (id TEXT PRIMARY KEY, source_json TEXT NOT NULL, pdf BLOB NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS analyses (id TEXT PRIMARY KEY, contract_id TEXT NOT NULL, result_json TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS analysis_failures (id TEXT PRIMARY KEY, contract_id TEXT NOT NULL, failure_json TEXT NOT NULL)"
    )

    # 2. Add user_id column if not present in legacy tables
    def ensure_column(table: str, column: str, col_type: str = "TEXT DEFAULT NULL"):
        columns = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")

    ensure_column("contracts", "user_id")
    ensure_column("analyses", "user_id")
    ensure_column("analysis_failures", "user_id")

    # 3. Users Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            trial_used INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")

    # 4. Subscriptions Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan TEXT NOT NULL,
            status TEXT NOT NULL,
            trial_start TEXT,
            trial_end TEXT,
            current_period_start TEXT,
            current_period_end TEXT,
            razorpay_subscription_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_rzp_id ON subscriptions(razorpay_subscription_id)")

    # 5. Payment Events Table (for webhook idempotency)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS payment_events (
            id TEXT PRIMARY KEY,
            provider_event_id TEXT UNIQUE NOT NULL,
            event_type TEXT NOT NULL,
            processed_at TEXT NOT NULL,
            processing_status TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_payment_events_provider_id ON payment_events(provider_event_id)")

    # 6. Usage Records Table (monthly AI analysis tracking)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            analysis_id TEXT NOT NULL,
            billing_period TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_records_user_period ON usage_records(user_id, billing_period)")


@contextmanager
def connection():
    path = settings.storage_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=15)) as conn, conn:
        _run_migrations(conn)
        yield conn


# ==========================================================
# USER STORAGE OPERATIONS
# ==========================================================

def save_user(user: UserRecord) -> None:
    with connection() as conn:
        conn.execute(
            "INSERT INTO users (id, email, password_hash, created_at, trial_used) VALUES (?, ?, ?, ?, ?)",
            (user.id, user.email, user.password_hash, user.created_at, 1 if user.trial_used else 0),
        )


def get_user_by_id(user_id: str) -> UserRecord | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, created_at, trial_used FROM users WHERE id=?",
            (user_id,),
        ).fetchone()
    if not row:
        return None
    return UserRecord(
        id=row[0],
        email=row[1],
        password_hash=row[2],
        created_at=row[3],
        trial_used=bool(row[4]),
    )


def get_user_by_email(email: str) -> UserRecord | None:
    clean_email = email.strip().lower()
    with connection() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, created_at, trial_used FROM users WHERE email=?",
            (clean_email,),
        ).fetchone()
    if not row:
        return None
    return UserRecord(
        id=row[0],
        email=row[1],
        password_hash=row[2],
        created_at=row[3],
        trial_used=bool(row[4]),
    )


def set_user_trial_used(user_id: str) -> None:
    with connection() as conn:
        conn.execute("UPDATE users SET trial_used=1 WHERE id=?", (user_id,))


# ==========================================================
# SUBSCRIPTION STORAGE OPERATIONS
# ==========================================================

def save_subscription(data: dict) -> None:
    with connection() as conn:
        conn.execute(
            """INSERT INTO subscriptions (
                id, user_id, plan, status, trial_start, trial_end,
                current_period_start, current_period_end, razorpay_subscription_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["id"],
                data["user_id"],
                data["plan"],
                data["status"],
                data.get("trial_start"),
                data.get("trial_end"),
                data.get("current_period_start"),
                data.get("current_period_end"),
                data.get("razorpay_subscription_id"),
                data["created_at"],
                data["updated_at"],
            ),
        )


def update_subscription(subscription_id: str, updates: dict) -> None:
    allowed_fields = [
        "plan", "status", "trial_start", "trial_end",
        "current_period_start", "current_period_end",
        "razorpay_subscription_id", "updated_at",
    ]
    set_clauses = []
    values = []
    for k, v in updates.items():
        if k in allowed_fields:
            set_clauses.append(f"{k} = ?")
            values.append(v)
    if not set_clauses:
        return
    values.append(subscription_id)
    query = f"UPDATE subscriptions SET {', '.join(set_clauses)} WHERE id = ?"
    with connection() as conn:
        conn.execute(query, tuple(values))


def get_latest_subscription_by_user_id(user_id: str) -> dict | None:
    with connection() as conn:
        row = conn.execute(
            """SELECT id, user_id, plan, status, trial_start, trial_end,
                      current_period_start, current_period_end, razorpay_subscription_id,
                      created_at, updated_at
               FROM subscriptions
               WHERE user_id = ?
               ORDER BY CASE
                   WHEN status = 'active' THEN 1
                   WHEN status = 'trialing' THEN 2
                   WHEN status = 'past_due' THEN 3
                   ELSE 4
               END, created_at DESC
               LIMIT 1""",
            (user_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "user_id": row[1],
        "plan": row[2],
        "status": row[3],
        "trial_start": row[4],
        "trial_end": row[5],
        "current_period_start": row[6],
        "current_period_end": row[7],
        "razorpay_subscription_id": row[8],
        "created_at": row[9],
        "updated_at": row[10],
    }


def get_subscription_by_razorpay_id(rzp_sub_id: str) -> dict | None:
    with connection() as conn:
        row = conn.execute(
            """SELECT id, user_id, plan, status, trial_start, trial_end,
                      current_period_start, current_period_end, razorpay_subscription_id,
                      created_at, updated_at
               FROM subscriptions
               WHERE razorpay_subscription_id = ?
               ORDER BY created_at DESC
               LIMIT 1""",
            (rzp_sub_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "user_id": row[1],
        "plan": row[2],
        "status": row[3],
        "trial_start": row[4],
        "trial_end": row[5],
        "current_period_start": row[6],
        "current_period_end": row[7],
        "razorpay_subscription_id": row[8],
        "created_at": row[9],
        "updated_at": row[10],
    }


# ==========================================================
# PAYMENT EVENT STORAGE (IDEMPOTENCY)
# ==========================================================

def get_payment_event(provider_event_id: str) -> dict | None:
    with connection() as conn:
        row = conn.execute(
            "SELECT id, provider_event_id, event_type, processed_at, processing_status FROM payment_events WHERE provider_event_id = ?",
            (provider_event_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "provider_event_id": row[1],
        "event_type": row[2],
        "processed_at": row[3],
        "processing_status": row[4],
    }


def record_payment_event(provider_event_id: str, event_type: str, status: str = "processed") -> str:
    event_id = str(uuid4())
    now_utc = datetime.now(timezone.utc).isoformat()
    with connection() as conn:
        conn.execute(
            "INSERT INTO payment_events (id, provider_event_id, event_type, processed_at, processing_status) VALUES (?, ?, ?, ?, ?)",
            (event_id, provider_event_id, event_type, now_utc, status),
        )
    return event_id


# ==========================================================
# USAGE TRACKING & QUOTA ENFORCEMENT
# ==========================================================

def count_analyses_in_period(user_id: str, billing_period: str) -> int:
    with connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM usage_records WHERE user_id = ? AND billing_period = ?",
            (user_id, billing_period),
        ).fetchone()
    return int(row[0]) if row else 0


def record_analysis_usage(user_id: str, analysis_id: str, billing_period: str) -> None:
    record_id = str(uuid4())
    now_utc = datetime.now(timezone.utc).isoformat()
    with connection() as conn:
        conn.execute(
            "INSERT INTO usage_records (id, user_id, analysis_id, billing_period, created_at) VALUES (?, ?, ?, ?, ?)",
            (record_id, user_id, analysis_id, billing_period, now_utc),
        )


# ==========================================================
# CONTRACT & ANALYSIS STORAGE WITH ACCOUNT-LEVEL ISOLATION
# ==========================================================

@timed("persistence_contract")
def save_contract(contract: Contract, pdf_bytes: bytes, user_id: str | None = None) -> None:
    with connection() as conn:
        conn.execute(
            "INSERT INTO contracts (id, source_json, pdf, user_id) VALUES (?, ?, ?, ?)",
            (contract.contract_id, contract.model_dump_json(), pdf_bytes, user_id),
        )


def get_contract(contract_id: str, user_id: str | None = None) -> Contract | None:
    with connection() as conn:
        if user_id is not None:
            # Enforce account-level data isolation
            row = conn.execute(
                "SELECT source_json FROM contracts WHERE id=? AND (user_id=? OR user_id IS NULL)",
                (contract_id, user_id),
            ).fetchone()
        else:
            row = conn.execute("SELECT source_json FROM contracts WHERE id=?", (contract_id,)).fetchone()
    return Contract.model_validate_json(row[0]) if row else None


@timed("persistence_analysis")
def save_analysis(analysis: Analysis, user_id: str | None = None) -> None:
    with connection() as conn:
        conn.execute(
            "INSERT INTO analyses (id, contract_id, result_json, user_id) VALUES (?, ?, ?, ?)",
            (analysis.analysis_id, analysis.contract_id, analysis.model_dump_json(), user_id),
        )


@timed("persistence_retrieval")
def get_analysis(analysis_id: str, user_id: str | None = None) -> Analysis | None:
    with connection() as conn:
        if user_id is not None:
            row = conn.execute(
                "SELECT result_json FROM analyses WHERE id=? AND (user_id=? OR user_id IS NULL)",
                (analysis_id, user_id),
            ).fetchone()
        else:
            row = conn.execute("SELECT result_json FROM analyses WHERE id=?", (analysis_id,)).fetchone()
    return Analysis.model_validate_json(row[0]) if row else None


def get_user_analyses_history(user_id: str, limit: int = 30) -> list[Analysis]:
    with connection() as conn:
        rows = conn.execute(
            "SELECT result_json FROM analyses WHERE user_id=? ORDER BY rowid DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return [Analysis.model_validate_json(row[0]) for row in rows]


@timed("persistence_failure")
def save_failure(failure: AnalysisFailure, user_id: str | None = None) -> None:
    with connection() as conn:
        conn.execute(
            "INSERT INTO analysis_failures (id, contract_id, failure_json, user_id) VALUES (?, ?, ?, ?)",
            (failure.analysis_id, failure.contract_id, failure.model_dump_json(), user_id),
        )


@timed("persistence_failure_retrieval")
def get_failure(analysis_id: str, user_id: str | None = None) -> AnalysisFailure | None:
    with connection() as conn:
        if user_id is not None:
            row = conn.execute(
                "SELECT failure_json FROM analysis_failures WHERE id=? AND (user_id=? OR user_id IS NULL)",
                (analysis_id, user_id),
            ).fetchone()
        else:
            row = conn.execute("SELECT failure_json FROM analysis_failures WHERE id=?", (analysis_id,)).fetchone()
    return AnalysisFailure.model_validate_json(row[0]) if row else None
