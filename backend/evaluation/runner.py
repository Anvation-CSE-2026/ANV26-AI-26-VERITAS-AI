"""Default OFFLINE fixture evaluation. --live is the only provider-call path."""
import argparse
import ast
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4
from app.config import settings
from .dataset_loader import load_dataset, sha256, FIXTURES
from .evaluator import evaluate

BASE = Path(__file__).resolve().parents[1]

def metadata(dataset, mode):
    module = BASE / "app/services/gemini_analysis.py"
    tree = ast.parse(module.read_text(encoding="utf-8"))
    prompt = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="SYSTEM_INSTRUCTION" for t in n.targets))
    config = dict(gemini_model=settings.gemini_model,embedding_model=settings.ollama_embedding_model,
        gemini_max_attempts=settings.gemini_max_attempts,
        gemini_retry_base_seconds=settings.gemini_retry_base_seconds,
        gemini_timeout_seconds=settings.gemini_timeout_seconds,
        ollama_connect_timeout=settings.ollama_connect_timeout,
        ollama_read_timeout=settings.ollama_read_timeout,
        max_upload_bytes=settings.max_upload_bytes,max_contract_pages=settings.max_contract_pages,
        max_contract_chars=settings.max_contract_chars,max_contract_clauses=settings.max_contract_clauses)
    source_paths = ["services/gemini_analysis.py","services/contract_analysis.py",
                    "services/pdf_extraction.py","services/evidence.py",
                    "services/policy_matching.py","services/ollama_embeddings.py",
                    "services/reasoning_boundaries.py","services/playbook.py",
                    "models/contracts.py","resources/sample_playbook.json"]
    return dict(evaluation_run_id=str(uuid4()),evaluated_at_utc=datetime.now(timezone.utc).isoformat(),
        dataset_id=dataset.dataset_id,dataset_version=dataset.version,mode=mode,
        result_label="FIXTURE EVALUATION — NOT MODEL ACCURACY" if mode=="fixture" else "LIVE MODEL EVALUATION",
        live_services_used=mode=="live",model_identifier=settings.gemini_model if mode=="live" else None,
        configured_models=dict(gemini=settings.gemini_model,embedding=settings.ollama_embedding_model),
        configuration=config,
        configuration_sha256=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest(),
        prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
        engine_source_hashes={p:sha256(BASE / "app" / p) for p in source_paths},
        dataset_manifest_sha256=sha256(FIXTURES / "manifest.json"),
        evaluator_version="1.0.0",
        evaluator_source_hashes={p.name:sha256(p) for p in sorted(Path(__file__).parent.glob("*.py"))},
        production_unsupported_categories=["governing_law"],
        measurement_notes=[
          "Gold labels are synthetic author judgments pending manual review, not legally validated.",
          "Detection uses source-target matching; literal evidence and legal interpretation are separate.",
          "Failed analyses retain all annotated risks as false negatives.",
          "Governing law is a benchmark-only category; the production schema/playbook lacks it.",
          "Live quote metrics cover returned findings; rejected raw quotes are not exposed by the engine.",
          "Token usage and costs are N/A because the current analysis result does not expose usage.",
          "Fixture processing latency is N/A; runner overhead is not model latency."])

def display(value):
    return "N/A" if value is None else f"{value:.6f}" if isinstance(value,float) else str(value)

def write_reports(report, output: Path):
    output.mkdir(parents=True,exist_ok=True)
    stem = report["metadata"]["dataset_id"] + "-" + report["metadata"]["mode"]
    jpath, cpath, mpath = [output / (stem + suffix) for suffix in (".json",".csv",".md")]
    jpath.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    s=report["summary"]
    rows=[("overall_detection",s["detection"])] + [(c,m) for c,m in s["per_category"].items()]
    with cpath.open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["label","scope","tp","fp","fn","precision","recall","f1","metric","value"])
        for scope,m in rows:
            writer.writerow([report["metadata"]["result_label"],scope]+[display(m[k]) for k in ("tp","fp","fn","precision","recall","f1")]+["",""])
        for section, values in [("dataset", {k:s[k] for k in ("dataset_size","annotation_count","annotated_risks","missing_clause_annotations","non_risk_annotations","ambiguous_annotations")}),
                                ("evidence",s["evidence"]),("reliability",s["reliability"]),
                                ("observability",{k:s[k] for k in ("proposed_finding_count","retained_finding_count","proposed_obligation_count","retained_obligation_count","rejection_reason_counts")}),
                                ("classification",{k:s[k] for k in ("micro_f1","macro_f1","category_accuracy_on_matched_risks","severity_accuracy_on_matched_risks")}),
                                ("usage_latency",{k:s[k] for k in ("average_processing_seconds","latency_available_analyses","input_tokens","output_tokens","total_tokens","estimated_cost_usd")})]:
            for metric,value in values.items():
                writer.writerow([report["metadata"]["result_label"],section]+[""]*6+[metric,json.dumps(value,sort_keys=True) if isinstance(value,dict) else display(value)])
        for p in s["unmatched_predictions"]:
            writer.writerow([report["metadata"]["result_label"],"unmatched_prediction"]+[""]*6+[p["contract_id"],p["prediction_id"]])
        for g in s["missed_gold_annotations"]:
            writer.writerow([report["metadata"]["result_label"],"missed_gold"]+[""]*6+[g["contract_id"],g["finding_id"]])
    lines=["# "+report["metadata"]["result_label"],"",
        f"Dataset: {report['metadata']['dataset_id']} v{report['metadata']['dataset_version']}; contracts: {s['dataset_size']}; annotated risks: {s['annotated_risks']}.",
        "","Synthetic labels are pending manual review. Fixture results measure evaluator behavior, not Gemini reliability.",
        "",f"Model actually evaluated: {display(report['metadata']['model_identifier'])}.",
        "", "| Scope | TP | FP | FN | Precision | Recall | F1 |",
        "|---|---:|---:|---:|---:|---:|---:|"]
    lines += ["| "+scope+" | "+" | ".join(display(m[k]) for k in ("tp","fp","fn","precision","recall","f1"))+" |" for scope,m in rows]
    lines += ["",f"Classification micro F1: {display(s['micro_f1'])}; macro F1: {display(s['macro_f1'])}.",
        f"Category accuracy on matched risks: {display(s['category_accuracy_on_matched_risks'])}; severity accuracy: {display(s['severity_accuracy_on_matched_risks'])}.",
        "", "## Deterministic evidence","",
        *[f"- {k}: {display(v)}" for k,v in s["evidence"].items()],
        "",f"Evidence error breakdown: {json.dumps(s['evidence_error_breakdown'],sort_keys=True)}",
        "", "## Processing reliability","",
        *[f"- {k}: {display(v)}" for k,v in s["reliability"].items()],
        f"- Average analysis latency (seconds): {display(s['average_processing_seconds'])}",
        f"- Input / output tokens: {display(s['input_tokens'])} / {display(s['output_tokens'])}",
        f"- Estimated API cost (USD): {display(s['estimated_cost_usd'])}",
        f"- Provider total tokens: {display(s['total_tokens'])}",
        "", "## Observability","",
        *[f"- {k}: {display(s[k])}" for k in ("proposed_finding_count","retained_finding_count","proposed_obligation_count","retained_obligation_count","rejection_reason_counts")],
        "", "## Failures",""]
    for c in s["cases"]:
        if c["status"] != "completed":
            lines.append(f"- {c['contract_id']}: {c['status']}; stage={display(c['failed_stage'])}; category={display(c['error_category'])}; HTTP={display(c['http_status'])}; upstream={display(c['upstream_http_status'])}; attempts={c['attempts']}.")
    lines += ["", "## Unmatched predictions",""]+[f"- {p['contract_id']}: {p['prediction_id']}" for p in s["unmatched_predictions"]]
    lines += ["", "## Missed gold annotations",""]+[f"- {g['contract_id']}: {g['finding_id']}" for g in s["missed_gold_annotations"]]
    lines += ["", "## Limitations",""]+["- "+n for n in report["metadata"]["measurement_notes"]]
    lines += ["", "Source quotes are preserved in fixtures, not repeated in reports. Full per-case evidence reasons, confusion matrices, hashes and matching IDs are in JSON.",""]
    mpath.write_text("\n".join(lines),encoding="utf-8")
    return [jpath,cpath,mpath]

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset",default="synthetic_v1")
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--live",action="store_true",help="Explicitly allow real Gemini/Ollama calls and potential charges. Obtain approval first.")
    group.add_argument("--dry-run",action="store_true",help="Evaluate fixture predictions only (the default).")
    parser.add_argument("--trace",action="store_true",help="Explicitly capture private traces for validated synthetic live benchmark data only.")
    parser.add_argument("--limit",type=int,help="Positive number of contracts; useful for an approved live smoke run.")
    parser.add_argument("--output",type=Path,default=Path(__file__).parent/"reports")
    args=parser.parse_args(argv)
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    if args.trace and not args.live:
        parser.error("--trace requires --live; offline tests exercise tracing with mocked providers.")
    started=perf_counter()
    try:
        dataset=load_dataset(args.dataset)
        if args.limit:
            dataset.cases=dataset.cases[:args.limit]
            selected={c.contract.contract_id for c in dataset.cases}
            dataset.fixture_outcomes=[o for o in dataset.fixture_outcomes if o.contract_id in selected]
        mode="live" if args.live else "fixture"
        meta=metadata(dataset,mode)
        if args.live:
            from .live_adapter import run_live
            outcomes=run_live(dataset,trace_enabled=True,run_id=meta["evaluation_run_id"]) if args.trace else run_live(dataset)
        else:
            outcomes=dataset.fixture_outcomes
        meta["synthetic_trace_enabled"]=args.trace
        summary=evaluate(dataset,outcomes)
        meta["runner_seconds"]=perf_counter()-started
        meta["selected_contract_count"]=len(dataset.cases)
        paths=write_reports(dict(metadata=meta,summary=summary),args.output)
    except Exception as exc:
        # Avoid full source snippets or secret-bearing exception strings in console.
        print(f"Benchmark failed ({type(exc).__name__}); no successful report was fabricated.")
        return 2
    print(meta["result_label"])
    print(f"Contracts={summary['dataset_size']} TP={summary['detection']['tp']} FP={summary['detection']['fp']} FN={summary['detection']['fn']}")
    for path in paths:
        print(path)
    if any(o.trace_observation_failed for o in outcomes):
        print("Synthetic trace capture failed or is incomplete; inspect sanitized trace diagnostics.")
        return 2
    return 1 if args.live and summary["reliability"]["failed"] else 0

if __name__=="__main__":
    raise SystemExit(main())
