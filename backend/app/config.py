from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VERITAS AI"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    gemini_api_key: str = Field(default="", repr=False)
    gemini_model: str = "gemini-3.5-flash"
    gemini_max_attempts: int = Field(default=3, ge=1, le=5)
    gemini_retry_base_seconds: float = Field(default=1.0, ge=0, le=10)
    gemini_timeout_seconds: float = Field(default=180.0, gt=0)
    storage_path: Path = Path(__file__).resolve().parents[2] / "data" / "contracts" / "veritas.sqlite3"
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    max_contract_pages: int = Field(default=30, gt=0)
    max_contract_chars: int = Field(default=60000, gt=0)
    max_contract_clauses: int = Field(default=100, gt=0)
    ollama_base_url: str = "http://localhost:11434"
    ollama_embedding_model: str = Field(
        default="qwen3-embedding:0.6b",
        validation_alias=AliasChoices("OLLAMA_EMBED_MODEL", "OLLAMA_EMBEDDING_MODEL"),
    )
    ollama_connect_timeout: float = Field(default=5.0, gt=0)
    ollama_read_timeout: float = Field(default=120.0, gt=0)
    embedding_provider: Literal["ollama", "gemini"] = "ollama"
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_embedding_dimensions: int = Field(default=768, ge=128, le=3072)
    gemini_embedding_timeout_seconds: float = Field(default=60.0, gt=0)

    # Authentication & Security
    jwt_secret_key: str = Field(default="veritas-ai-secret-key-change-in-production-2026", repr=False)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=60 * 24, gt=0)
    auth_required: bool = True
    allow_legacy_unauthenticated_access: bool = False

    # Razorpay Test Mode Subscriptions
    razorpay_key_id: str = Field(default="", repr=False)
    razorpay_key_secret: str = Field(default="", repr=False)
    razorpay_webhook_secret: str = Field(default="", repr=False)
    razorpay_standard_plan_id: str = Field(default="", repr=False)
    razorpay_pro_plan_id: str = Field(default="", repr=False)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
