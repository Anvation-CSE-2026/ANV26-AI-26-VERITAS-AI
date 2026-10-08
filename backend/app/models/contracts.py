"""Typed source records and strictly structured model output."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

Category = Literal["liability", "indemnification", "termination", "confidentiality", "payment", "data_protection", "intellectual_property"]
RiskLevel = Literal["low", "medium", "high", "critical"]
FindingStatus = Literal["compliant", "risky", "ambiguous", "conflicting", "missing"]
EvidenceStatus = Literal["verified", "unsupported", "needs_review"]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PageText(Record):
    page_number: int = Field(ge=1)
    text: str


class Clause(Record):
    clause_id: str
    page_number: int = Field(ge=1)
    text: str
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=1)


class Contract(Record):
    contract_id: str
    filename: str
    pages: list[PageText]
    clauses: list[Clause]
    warnings: list[str]


class PolicyRule(Record):
    policy_id: str
    category: Category
    rule: str
    recommended_action: str


class Playbook(Record):
    playbook_id: str
    version: str
    description: str
    rules: list[PolicyRule]


class PolicyMatch(Record):
    clause_id: str
    policy_id: str
    similarity: float = Field(ge=-1, le=1)


class RiskDraft(Record):
    model_config = ConfigDict(extra="forbid", strict=True)
    finding_status: FindingStatus = "risky"
    policy_requirement: str | None = None
    referenced_parties: list[str] = Field(default_factory=list, max_length=20)
    referenced_dates: list[str] = Field(default_factory=list, max_length=20)
    policy_match_reliable: bool = True
    uncertainty: str | None = None
    unsupported_assumptions: list[str] = Field(default_factory=list, max_length=20)
    risk_level: RiskLevel
    clause_category: Category
    explanation: str = Field(min_length=1, max_length=2000)
    evidence_quote: str | None = Field(default=None, min_length=1, max_length=2000)
    page_number: int | None = Field(default=None, ge=1)
    clause_id: str | None = None
    policy_id: str
    recommended_action: str = Field(min_length=1, max_length=2000)


class ObligationDraft(Record):
    model_config = ConfigDict(extra="forbid", strict=True)
    description: str = Field(min_length=1, max_length=2000)
    evidence_quote: str = Field(min_length=1, max_length=2000)
    page_number: int = Field(ge=1)
    clause_id: str
    responsible_party: str | None
    deadline: str | None


class AnalysisDraft(Record):
    _gemini_attempts: int = PrivateAttr(default=1)
    _gemini_model_version: str | None = PrivateAttr(default=None)
    model_config = ConfigDict(extra="forbid", strict=True)
    findings: list[RiskDraft] = Field(max_length=100)
    obligations: list[ObligationDraft] = Field(max_length=100)


class SourceFacts(Record):
    clause_id: str
    page_number: int
    evidence_quote: str
    referenced_parties: list[str]
    referenced_dates: list[str]


class ModelInterpretation(Record):
    finding_status: FindingStatus
    explanation: str
    recommended_action: str
    uncertainty: str | None
    unsupported_assumptions: list[str]


class VerifiedFinding(RiskDraft):
    applicable_policy_rule: PolicyRule
    evidence_verified: bool = True
    evidence_status: EvidenceStatus = "verified"
    source_facts: SourceFacts | None = None
    model_interpretation: ModelInterpretation | None = None
    potential_omission: bool = False
    complete_document_review_required: bool = False
    absence_confirmed: Literal[False] = False


class VerifiedObligation(ObligationDraft):
    evidence_verified: Literal[True] = True
    evidence_status: EvidenceStatus = "verified"
    deadline_type: Literal["fixed_date", "relative", "ambiguous", "unspecified"] = "unspecified"


class RejectedRecord(Record):
    record_type: Literal["finding", "obligation"]
    index: int
    reason: str
    evidence_status: Literal["unsupported"] = "unsupported"


class InstructionAlert(Record):
    source_type: Literal["clause", "policy"]
    source_id: str
    reason: str


class Analysis(Record):
    gemini_attempts: int = Field(default=0, ge=0)
    gemini_response_model: str | None = None
    processing_seconds: float = Field(default=0, ge=0)
    output_origin: Literal["live_gemini", "synthetic_demo"] = "live_gemini"
    requires_human_review: Literal[True] = True
    document_instruction_alerts: list[InstructionAlert] = Field(default_factory=list)
    analysis_id: str
    contract_id: str
    created_at: datetime
    status: Literal["completed", "partial"]
    gemini_model: str
    embedding_model: str
    playbook_id: str
    playbook_version: str
    findings: list[VerifiedFinding]
    obligations: list[VerifiedObligation]
    semantic_matches: list[PolicyMatch]
    unassessed_policy_ids: list[str]
    verification_rejections: list[RejectedRecord]
    warnings: list[str]


class AnalyzeRequest(Record):
    contract_id: str = Field(min_length=1, max_length=100)


class AnalysisFailure(Record):
    analysis_id: str
    contract_id: str
    created_at: datetime
    status: Literal["failed"] = "failed"
    output_origin: Literal["live_gemini"] = "live_gemini"
    failed_stage: str
    error_category: str
    message: str
    http_status: int
    upstream_http_status: int | None = None
    gemini_model: str
    gemini_attempts: int = Field(ge=0)
    retries_occurred: bool
    processing_seconds: float = Field(ge=0)
    verification_rejections: list[RejectedRecord] = Field(default_factory=list)


class DemoArtifact(Record):
    label: Literal["SAMPLE ANALYSIS — DEMO DATA"]
    output_origin: Literal["synthetic_demo"]
    live_ai_used: Literal[False]
    description: str
    contract: Contract
    playbook: Playbook
    analysis: Analysis
