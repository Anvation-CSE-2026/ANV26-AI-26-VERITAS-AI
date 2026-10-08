"""Conservative review signals, never compliance decisions or proof of immunity."""
import re
from datetime import datetime

from app.models.contracts import Contract, InstructionAlert, Playbook

PATTERNS = {
    "role_override": r"ignore\s+(?:all\s+)?(?:previous|prior|system)\s+instructions|<\/?system>|\[system\]|(?:^|\n)system\s*:",
    "schema_override": r"(?:override|ignore|replace|change).{0,50}(?:schema|output format|system prompt)",
    "secret_request": r"(?:reveal|print|expose|show).{0,60}(?:secret|credential|api key|system prompt)",
    "forced_verdict": r"(?:mark|report|declare|classify).{0,60}(?:every|all|no risks|compliant)",
}


def detect_document_instructions(contract: Contract, playbook: Playbook) -> list[InstructionAlert]:
    alerts = []
    sources = [("clause", c.clause_id, c.text) for c in contract.clauses]
    sources += [("policy", p.policy_id, p.rule + "\n" + p.recommended_action) for p in playbook.rules]
    for source_type, source_id, text in sources:
        for reason, pattern in PATTERNS.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                alerts.append(InstructionAlert(source_type=source_type, source_id=source_id, reason=reason))
    return alerts


def deadline_type(value: str | None) -> str:
    if value is None:
        return "unspecified"
    if re.search(r"\b(within|after|before|each|every|following|upon|from)\b", value, re.IGNORECASE):
        return "relative"
    for match in re.finditer(r"\b\d{4}-\d{2}-\d{2}\b", value):
        try:
            datetime.strptime(match.group(), "%Y-%m-%d")
            return "fixed_date"
        except ValueError:
            pass
    months = r"January|February|March|April|May|June|July|August|September|October|November|December"
    patterns = [(rf"\b(?:{months}) \d{{1,2}},? \d{{4}}\b", ["%B %d, %Y", "%B %d %Y"]),
                (rf"\b\d{{1,2}} (?:{months}) \d{{4}}\b", ["%d %B %Y"])]
    for pattern, formats in patterns:
        for match in re.finditer(pattern, value, re.IGNORECASE):
            for fmt in formats:
                try:
                    datetime.strptime(match.group(), fmt)
                    return "fixed_date"
                except ValueError:
                    pass
    return "ambiguous"


def explicit_reference(value: str, quote: str) -> bool:
    return bool(value.strip()) and bool(re.search(r"(?<!\w)" + re.escape(value) + r"(?!\w)", quote))
