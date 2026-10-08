"""Explicitly opted-in live adapter. Not imported by the offline runner path."""
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from uuid import uuid4
import sys

from app.config import settings
from app.services.pdf_extraction import extract_contract
from app.services.contract_analysis import analyze_contract
from app.services.storage import save_contract, get_analysis, get_failure
from app.services.analysis_observability import observation_scope, stage, emit
from .schema import Dataset, Outcome, Prediction

def _case(case, outcomes, collector):
    started, stage_name = perf_counter(), "pdf_extraction"
    try:
        pdf = Path(case.pdf_path).read_bytes()
        contract = extract_contract(pdf, case.contract.filename)
        contract.contract_id = case.contract.contract_id
        stage_name = "sqlite_contract_persistence"
        save_contract(contract, pdf)
        stage_name = "analysis"
        result = analyze_contract(contract)
        stage_name = "sqlite_analysis_retrieval"
        stored = get_analysis(result.analysis_id)
        if stored != result:
            raise ValueError("Persisted analysis mismatch")
        predictions = [Prediction(
            prediction_id=f"{contract.contract_id}-LIVE-{i+1:03d}",
            risk_category=f.clause_category,severity=f.risk_level,
            finding_status=f.finding_status,evidence_quote=f.evidence_quote,
            page_number=f.page_number,clause_id=f.clause_id,policy_id=f.policy_id)
            for i,f in enumerate(stored.findings)]
        rejected_findings=sum(r.record_type=="finding" for r in stored.verification_rejections)
        rejected_obligations=sum(r.record_type=="obligation" for r in stored.verification_rejections)
        outcomes.append(Outcome(contract_id=contract.contract_id,status=stored.status,
            predictions=predictions,processing_seconds=perf_counter()-started,
            attempts=stored.gemini_attempts,response_model=stored.gemini_response_model,
            analysis_id=stored.analysis_id,proposed_finding_count=len(stored.findings)+rejected_findings,
            retained_finding_count=len(stored.findings),proposed_obligation_count=len(stored.obligations)+rejected_obligations,
            retained_obligation_count=len(stored.obligations),
            rejected_finding_count=rejected_findings,rejected_obligation_count=rejected_obligations))
    except Exception as exc:
        # Never stringify exceptions: provider URLs could contain a key.
        aid=getattr(exc,"analysis_id",None)
        try:
            failure=get_failure(aid) if aid else None
        except Exception:
            failure=None
        if collector and collector.status != "failed":
            emit("analysis_failure",stage=failure.failed_stage if failure else stage_name,
                 category=failure.error_category if failure else "evaluation_adapter_failure",analysis_id=aid)
        outcomes.append(Outcome(contract_id=case.contract.contract_id,status="failed",
            processing_seconds=perf_counter()-started,analysis_id=aid,
            failed_stage=failure.failed_stage if failure else stage_name,
            error_category=failure.error_category if failure else "evaluation_adapter_failure",
            http_status=failure.http_status if failure else None,
            upstream_http_status=failure.upstream_http_status if failure else None,
            attempts=failure.gemini_attempts if failure else 0,failure_recorded=failure is not None,
            rejected_finding_count=sum(r.record_type=="finding" for r in failure.verification_rejections) if failure else 0,
            rejected_obligation_count=sum(r.record_type=="obligation" for r in failure.verification_rejections) if failure else 0))

def _save_trace(collector, outcome, interrupted):
    try:
        retained=[r for r in collector.items if r["item_type"]=="finding" and r["retained"] is True]
        if outcome:
            for item,prediction in zip(retained,outcome.predictions):
                item["evaluation_prediction_id"]=prediction.prediction_id
        payload,path=collector.write("interrupted" if interrupted else None)
        if outcome:
            outcome.trace_id=collector.trace_id
            outcome.trace_file=str(path)
            outcome.trace_observation_failed=collector.observation_failed
            for field in ("input_tokens","output_tokens","total_tokens"):
                setattr(outcome,field,payload["token_usage"][field])
            outcome.rejection_reason_counts=dict(Counter(i["rejection_reason_code"]
                for i in payload["items"] if i["final_status"]=="rejected"))
            for kind in ("finding","obligation"):
                counts=payload["counts"][kind+"s"]
                setattr(outcome,"proposed_"+kind+"_count",counts["proposed"])
                setattr(outcome,"retained_"+kind+"_count",counts["retained"])
    except Exception:
        # Observability failure is explicit, never a fabricated successful trace.
        if outcome:
            outcome.trace_observation_failed=True

def run_live(dataset: Dataset, *, trace_enabled: bool = False, run_id: str | None = None) -> list[Outcome]:
    """Sequential standalone process, unchanged analysis engine, isolated SQLite."""
    previous, outcomes = settings.storage_path, []
    run_id=run_id or str(uuid4())
    with TemporaryDirectory(prefix="veritas-evaluation-") as temp:
        settings.storage_path=Path(temp)/"benchmark.sqlite3"
        try:
            for case in dataset.cases:
                collector=None
                if trace_enabled:
                    from .tracing import TraceCollector
                    collector=TraceCollector(case,run_id)
                try:
                    with observation_scope(collector),stage("total_analysis"):
                        _case(case,outcomes,collector)
                finally:
                    if collector:
                        outcome=outcomes[-1] if outcomes and outcomes[-1].contract_id==case.contract.contract_id else None
                        _save_trace(collector,outcome,sys.exc_info()[0] is not None)
        finally:
            settings.storage_path=previous
    return outcomes
