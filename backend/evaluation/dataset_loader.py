"""Validate identifiers, original PDF extraction, source offsets, gold and fixture coverage."""
import hashlib
import json
from pathlib import Path
from .schema import Dataset, Case, Annotation, Outcome
from app.models.contracts import Contract
from app.services.pdf_extraction import extract_contract

FIXTURES = Path(__file__).parent / "fixtures"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_case(case: Case, policy_ids: set[str]) -> None:
    contract = case.contract
    numbers = [p.page_number for p in contract.pages]
    if not numbers or numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("Missing, duplicate or nonconsecutive PDF pages")
    pages = {p.page_number: p.text for p in contract.pages}
    clauses = {c.clause_id: c for c in contract.clauses}
    if len(clauses) != len(contract.clauses):
        raise ValueError("Duplicate clause IDs")
    for c in contract.clauses:
        if (c.page_number not in pages or c.end_offset <= c.start_offset
            or pages[c.page_number][c.start_offset:c.end_offset] != c.text):
            raise ValueError("Clause offsets do not reproduce original page text")
    ids = [g.finding_id for g in case.annotations]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate gold finding IDs")
    for g in case.annotations:
        if g.contract_id != contract.contract_id or g.policy_id not in policy_ids:
            raise ValueError("Invalid annotation contract or policy reference")
        for span in g.evidence_spans:
            c = clauses.get(span.clause_id)
            if c is None or c.page_number != span.page_number or span.quote not in c.text:
                raise ValueError("Gold quote not present in referenced source clause")

def safe_file(base: Path, name: str) -> Path:
    result = (base / name).resolve()
    if not result.is_relative_to(base.resolve()) or not result.is_file():
        raise ValueError("Dataset file missing or outside dataset directory")
    return result

def load_dataset(name: str = "synthetic_v1", *, fixtures_root: Path = FIXTURES) -> Dataset:
    if name != "synthetic_v1":
        raise ValueError("Unknown dataset; supported: synthetic_v1")
    manifest = json.loads((fixtures_root / "manifest.json").read_text(encoding="utf-8"))
    if manifest["dataset_id"] != name or manifest.get("synthetic") is not True:
        raise ValueError("Dataset identity mismatch")
    for path, digest in manifest["file_hashes"].items():
        if sha256(safe_file(fixtures_root, path)) != digest:
            raise ValueError("Dataset integrity hash mismatch")
    playbook = json.loads(safe_file(fixtures_root, "benchmark_playbook.json").read_text(encoding="utf-8"))
    rules = playbook["rules"] + playbook["benchmark_only_rules"]
    rule_ids = [r["policy_id"] for r in rules]
    if len(rule_ids) != len(set(rule_ids)) or set(rule_ids) != set(manifest["policy_ids"]):
        raise ValueError("Benchmark policy IDs do not match playbook")
    cases = []
    for item in manifest["contracts"]:
        source = Contract.model_validate_json(safe_file(fixtures_root, item["source"]).read_text(encoding="utf-8"))
        if source.contract_id != item["contract_id"]:
            raise ValueError("Manifest contract ID differs from source")
        gold = [Annotation.model_validate(g) for g in json.loads(
            safe_file(fixtures_root, item["annotations"]).read_text(encoding="utf-8"))]
        pdf = safe_file(fixtures_root, item["pdf"])
        extracted = extract_contract(pdf.read_bytes(), source.filename)
        extracted.contract_id = source.contract_id
        if extracted != source:
            raise ValueError("Stored source differs from current production PDF extraction")
        case = Case(contract=source, annotations=gold, pdf_path=str(pdf))
        validate_case(case, set(manifest["policy_ids"]))
        cases.append(case)
    predictions = [Outcome.model_validate(o) for o in json.loads(
        safe_file(fixtures_root, manifest["predictions"]).read_text(encoding="utf-8"))]
    case_ids = [c.contract.contract_id for c in cases]
    outcome_ids = [o.contract_id for o in predictions]
    if not cases:
        raise ValueError("Synthetic fixture dataset must not be empty")
    if len(case_ids) != len(set(case_ids)) or len(outcome_ids) != len(set(outcome_ids)):
        raise ValueError("Duplicate contract/outcome IDs")
    if set(case_ids) != set(outcome_ids):
        raise ValueError("Fixture outcomes must cover each contract exactly once")
    all_gold = [g.finding_id for c in cases for g in c.annotations]
    if len(all_gold) != len(set(all_gold)):
        raise ValueError("Gold IDs must be globally unique")
    return Dataset(dataset_id=name, version=manifest["version"], cases=cases,
                   policy_ids=manifest["policy_ids"], fixture_outcomes=predictions)
