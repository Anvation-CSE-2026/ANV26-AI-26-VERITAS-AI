"""Independent benchmark schema; governing_law does not extend production schemas."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.contracts import Contract

Category = Literal["liability", "indemnification", "termination", "payment", "confidentiality",
                   "data_protection", "intellectual_property", "governing_law"]
CATEGORIES = list(Category.__args__)
Severity = Literal["low", "medium", "high", "critical"]

class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

class EvidenceSpan(Record):
    clause_id: str
    page_number: int = Field(ge=1)
    quote: str = Field(min_length=1)

class Annotation(Record):
    contract_id: str
    finding_id: str
    risk_category: Category
    expected_severity: Severity | None
    expected_clause_text: str | None
    expected_page_number: int | None = Field(default=None, ge=1)
    explanation: str = Field(min_length=1)
    risk_present: bool | None
    annotation_state: Literal["risk", "non_risk", "missing", "ambiguous"]
    annotation_confidence: Literal["high", "medium", "low"]
    reviewer_status: Literal["pending_manual_review", "reviewed_synthetic"]
    policy_id: str
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)

    @model_validator(mode="after")
    def coherent(self):
        expected = {"risk": True, "non_risk": False, "missing": True, "ambiguous": None}
        if self.risk_present is not expected[self.annotation_state]:
            raise ValueError("risk_present conflicts with annotation_state")
        if self.annotation_state == "missing":
            if self.evidence_spans or self.expected_clause_text is not None or self.expected_page_number is not None:
                raise ValueError("Missing clauses must not fabricate evidence")
        else:
            if not self.evidence_spans:
                raise ValueError("Present clauses require source spans")
            first = self.evidence_spans[0]
            if self.expected_clause_text != first.quote or self.expected_page_number != first.page_number:
                raise ValueError("Primary evidence must match first source span")
        if self.annotation_state in ("risk", "missing") and self.expected_severity is None:
            raise ValueError("Definite risks require severity")
        return self

class Prediction(Record):
    prediction_id: str
    risk_category: Category
    severity: Severity | None = None
    finding_status: Literal["risky", "conflicting", "compliant", "ambiguous", "missing"] = "risky"
    evidence_quote: str | None = None
    page_number: int | None = None  # Invalid citations intentionally allowed for evaluation.
    clause_id: str | None = None
    policy_id: str | None = None

class Outcome(Record):
    contract_id: str
    status: Literal["completed", "partial", "failed"]
    predictions: list[Prediction] = Field(default_factory=list)
    processing_seconds: float | None = Field(default=None, ge=0)
    error_category: str | None = None
    failed_stage: str | None = None
    http_status: int | None = None
    upstream_http_status: int | None = None
    attempts: int = Field(default=0, ge=0)
    failure_recorded: bool | None = None
    rejected_finding_count: int = Field(default=0, ge=0)
    rejected_obligation_count: int = Field(default=0, ge=0)
    response_model: str | None = None
    analysis_id: str | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    proposed_finding_count: int | None = Field(default=None, ge=0)
    retained_finding_count: int | None = Field(default=None, ge=0)
    proposed_obligation_count: int | None = Field(default=None, ge=0)
    retained_obligation_count: int | None = Field(default=None, ge=0)
    trace_id: str | None = None
    trace_file: str | None = None
    trace_observation_failed: bool | None = None
    rejection_reason_counts: dict[str, int] = Field(default_factory=dict)
    estimated_cost_usd: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def valid_outcome(self):
        if self.status == "failed" and self.predictions:
            raise ValueError("Failed analysis cannot substitute successful findings")
        ids = [p.prediction_id for p in self.predictions]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate prediction IDs")
        return self

class Case(Record):
    contract: Contract
    annotations: list[Annotation]
    pdf_path: str

class Dataset(Record):
    dataset_id: str
    version: str
    cases: list[Case]
    policy_ids: list[str]
    fixture_outcomes: list[Outcome]
