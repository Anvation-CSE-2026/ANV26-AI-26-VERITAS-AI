"""Private, explicitly enabled traces for the frozen repository synthetic dataset only."""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from app.config import settings
from .dataset_loader import FIXTURES, load_dataset

REASONS = {
 "unknown_clause_id": ("INVALID_REFERENCE", "Clause ID does not identify an extracted source clause."),
 "wrong_page_number": ("PAGE_MISMATCH", "Cited page differs from the referenced clause page."),
 "source_offset_mismatch": ("SOURCE_INTEGRITY_FAILURE", "Source offsets do not reproduce the extracted clause."),
 "quote_not_in_original_clause": ("QUOTE_NOT_FOUND", "Supplied quotation is not an exact substring of the original cited clause/page."),
 "unknown_policy_id": ("INVALID_REFERENCE", "Policy ID does not identify a supplied playbook rule."),
 "policy_category_mismatch": ("POLICY_MISMATCH", "Finding category differs from the referenced policy category."),
 "policy_requirement_mismatch": ("POLICY_MISMATCH", "Supplied policy wording differs from the trusted playbook rule."),
 "referenced_party_not_in_evidence": ("INVALID_REFERENCE", "Referenced party is not explicit in the evidence quotation."),
 "referenced_date_not_in_evidence": ("INVALID_REFERENCE", "Referenced date is not explicit in the evidence quotation."),
 "party_not_explicit_in_evidence": ("INVALID_REFERENCE", "Obligation party is not explicit in the evidence quotation."),
 "deadline_not_explicit_in_evidence": ("INVALID_REFERENCE", "Obligation deadline is not explicit in the evidence quotation."),
 "missing_finding_has_contract_evidence": ("INVALID_OMISSION_REFERENCE", "Potential omission carries forbidden contract evidence references."),
 "missing_finding_has_source_references": ("INVALID_OMISSION_REFERENCE", "Potential omission carries forbidden party/date references."),
}

def reason_details(reason, proposed):
    # Disambiguate absent fields only when the actual first verifier reason permits.
    if (reason == "unknown_clause_id" and proposed.get("clause_id") is None or
        reason == "wrong_page_number" and proposed.get("page_number") is None or
        reason == "quote_not_in_original_clause" and not (proposed.get("evidence_quote") or "").strip()):
        return "MISSING_EVIDENCE", "Required source evidence/reference is absent or blank; no fabricated quotation is established."
    return REASONS.get(reason, ("UNKNOWN_REJECTION", "Verifier supplied an unrecognized rejection reason; cause is not inferred."))

def redact(value):
    """Prevent known credentials and common PII/token formats entering artifacts."""
    secrets = [getattr(settings,name) for name,field in type(settings).model_fields.items()
               if field.repr is False and isinstance(getattr(settings,name),str) and getattr(settings,name)]
    def clean(v):
        if isinstance(v,dict):
            return {k:clean(x) for k,x in v.items()}
        if isinstance(v,list):
            return [clean(x) for x in v]
        if not isinstance(v,str):
            return v
        for secret in sorted(secrets,key=len,reverse=True):
            v=v.replace(secret,"[REDACTED_CREDENTIAL]")
        v=re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b","[REDACTED_EMAIL]",v,flags=re.I)
        v=re.sub(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b","[REDACTED_TOKEN]",v)
        v=re.sub(r"(?i)\b(?:Bearer\s+|AIza)[A-Za-z0-9._-]+","[REDACTED_TOKEN]",v)
        v=re.sub(r"(?<!\w)(?:\+\d{1,3}[ -]?)?(?:\(\d{3}\)[ -]?|\d{3}[ -])\d{3}[ -]\d{4}(?!\w)","[REDACTED_PHONE]",v)
        v=re.sub(r"\b\d{3}-\d{2}-\d{4}\b","[REDACTED_ID]",v)
        v=re.sub(r"(?i)\b(api[_ -]?key|access[_ -]?token|authorization|password|payment[_ -]?secret)\s*[:=]\s*[^\s,;]+",r"\1=[REDACTED_CREDENTIAL]",v)
        return v
    return clean(value)

def secure_directory(path: Path):
    path.mkdir(mode=0o700,parents=True,exist_ok=False)
    if os.name == "nt":
        identity=subprocess.run(["whoami","/user","/fo","csv","/nh"],capture_output=True,text=True,check=True)
        sid=re.search(r"S-1-\d+(?:-\d+)+",identity.stdout)
        if sid is None:
            raise RuntimeError("Cannot establish private trace owner")
        # Fail closed before any content write if ACL cannot be established.
        subprocess.run(["icacls",str(path),"/inheritance:r","/grant:r","*"+sid.group()+":(OI)(CI)F"],
                       capture_output=True,text=True,check=True)
    else:
        path.chmod(0o700)

def canonical(contract):
    return contract.model_dump(exclude={"contract_id"})

def validate_synthetic_case(case):
    # Never accept a caller's synthetic=true or ID prefix as proof.
    trusted=load_dataset("synthetic_v1")
    approved=next((c for c in trusted.cases if c.contract.contract_id==case.contract.contract_id),None)
    if approved is None or canonical(approved.contract)!=canonical(case.contract):
        raise ValueError("Tracing requires an unchanged repository synthetic fixture")
    if Path(case.pdf_path).resolve()!=Path(approved.pdf_path).resolve():
        raise ValueError("Tracing requires the approved fixture PDF path")
    return approved

class TraceCollector:
    def __init__(self,case,run_id,*,output_root=None):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",run_id):
            raise ValueError("Invalid evaluation run ID")
        self.case=validate_synthetic_case(case)
        self.run_id=run_id
        self.contract_id=case.contract.contract_id
        self.trace_id=str(uuid4())
        self.directory=(output_root or Path(__file__).parent/"private_traces")/run_id/self.trace_id
        # Secure the actual per-contract artifact directory, using a new directory.
        secure_directory(self.directory)
        self.items=[]
        self.spans=[]
        self.stack=[]
        self.events=[]
        self.observation_failed=False
        self.started=perf_counter()
        self.status="unverified"
        self.analysis_id=None
        self.response_model=None
        self.usage=dict(input_tokens=None,output_tokens=None,total_tokens=None,scope="last_reported_response")
        self.draft_seen=False

    def begin_stage(self,name,started):
        sid=f"span-{len(self.spans)+1:04d}"
        self.spans.append(dict(span_id=sid,stage=name,parent_span_id=self.stack[-1] if self.stack else None,
                              seconds=None,status="running"))
        self.stack.append(sid)
        return sid

    def evidence(self,item,retained=None,rejection=None):
        quote=item.get("evidence_quote")
        supplied=any(item.get(k) is not None for k in ("clause_id","page_number","evidence_quote"))
        quoted=isinstance(quote,str) and bool(quote.strip())
        pages={p.page_number:p.text for p in self.case.contract.pages}
        clause=next((c for c in self.case.contract.clauses if c.clause_id==item.get("clause_id")),None)
        missing=item.get("finding_status")=="missing"
        applicable=not (missing and not supplied)
        exact=any(quote in text for text in pages.values()) if quoted else None
        cited=quote in pages.get(item.get("page_number"),"") if quoted else None
        in_clause=quote in clause.text if quoted and clause else False if quoted else None
        if not applicable and not rejection:
            state="not_applicable"
        elif retained is None:
            state="unverified"
        elif rejection:
            state="missing" if reason_details(rejection,item)[0]=="MISSING_EVIDENCE" else "invalid"
        else:
            state="verified"
        return dict(evidence_supplied=supplied,quotation_supplied=quoted,
            quotation_matches_extracted_text=exact,cited_page_matches=cited,
            quotation_matches_cited_clause=in_clause,evidence_state=state,
            evidence_verification_succeeded=retained is True and not missing,
            evidence_verification_not_applicable=not applicable,
            absence_confirmed=False)

    def event(self,event,**data):
        if event=="stage_finished":
            row=next(s for s in self.spans if s["span_id"]==data["span_id"])
            row.update(seconds=data["seconds"],status=data["status"])
            if self.stack and self.stack[-1]==data["span_id"]:
                self.stack.pop()
        elif event=="usage":
            meta=getattr(data["response"],"usage_metadata",None)
            for target,source in (("input_tokens","prompt_token_count"),("output_tokens","candidates_token_count"),("total_tokens","total_token_count")):
                value=getattr(meta,source,None) if meta else None
                self.usage[target]=value if isinstance(value,int) and not isinstance(value,bool) and value>=0 else None
            self.response_model=getattr(data["response"],"model_version",None)
        elif event=="proposed":
            if canonical(data["contract"]) != canonical(self.case.contract) or data["contract"].contract_id != self.contract_id:
                raise ValueError("Observed source differs from approved synthetic fixture")
            self.draft_seen=True
            draft=data["draft"]
            for kind,values in (("finding",draft.findings),("obligation",draft.obligations)):
                for index,item in enumerate(values):
                    proposed=item.model_dump()
                    self.items.append(dict(item_type=kind,item_id=f"{self.trace_id}:{kind}:{index+1:03d}",
                        proposed_index=index,pipeline_stage="evidence_verification",final_status="unverified",
                        retained=None,rejection_stage=None,rejection_reason_code=None,
                        original_verifier_reason=None,diagnostic=None,
                        evidence_validation=self.evidence(proposed),proposed=proposed,final=None))
        elif event=="verified":
            rejected={(r.record_type,r.index):r.reason for r in data["rejections"]}
            accepted={"finding":iter(data["findings"]),"obligation":iter(data["obligations"])}
            for row in self.items:
                reason=rejected.get((row["item_type"],row["proposed_index"]))
                if reason:
                    code,diagnostic=reason_details(reason,row["proposed"])
                    row.update(final_status="rejected",retained=False,rejection_stage="evidence_verification",
                        rejection_reason_code=code,original_verifier_reason=reason,diagnostic=diagnostic,
                        evidence_validation=self.evidence(row["proposed"],False,reason))
                else:
                    final=next(accepted[row["item_type"]])
                    row.update(final_status="retained",retained=True,final=final.model_dump(mode="json"),
                               evidence_validation=self.evidence(row["proposed"],True))
        elif event=="structured_failure":
            self.events.append(dict(pipeline_stage="structured_output_validation",
                reason_code="INVALID_SCHEMA",diagnostic="Structured output failed schema validation; item attribution unavailable."))
        elif event=="analysis_result":
            result=data["result"]
            self.status=result.status
            self.analysis_id=result.analysis_id
        elif event=="analysis_failure":
            self.status="failed"
            self.analysis_id=data.get("analysis_id")
            self.events.append(dict(pipeline_stage=data["stage"],reason_code=data["category"],
                diagnostic="Pipeline failed; raw provider exception and source contents are not logged."))
        else:
            self.observation_failed=True

    def finish(self,status=None):
        if status:
            self.status=status
        counts={}
        for kind in ("finding","obligation"):
            rows=[r for r in self.items if r["item_type"]==kind]
            counts[kind+"s"]=dict(proposed=len(rows) if self.draft_seen else None,
                retained=sum(r["retained"] is True for r in rows) if self.draft_seen else None,
                rejected=sum(r["retained"] is False for r in rows) if self.draft_seen else None,
                unverified=sum(r["retained"] is None for r in rows) if self.draft_seen else None)
        return redact(dict(schema_version="1.0",evaluation_run_id=self.run_id,trace_id=self.trace_id,
            contract_id=self.contract_id,synthetic_source_only=True,
            model_identifier=settings.gemini_model,response_model=self.response_model,
            analysis_id=self.analysis_id,status=self.status,created_at_utc=datetime.now(timezone.utc).isoformat(),
            pipeline_stage=self.spans[-1]["stage"] if self.spans else None,counts=counts,
            items=self.items,stages=self.spans,token_usage=self.usage,
            trace_collection_seconds=max(0.0,perf_counter()-self.started),
            diagnostics=self.events,observation_failed=self.observation_failed,
            timing_notes=["Nested stages overlap; do not add total, retrieval, embedding or Gemini parsing durations.",
                          "Embedding spans include the HTTP round trip and vector validation.",
                          "Total analysis scope includes selected extraction and persistence/retrieval.",
                          "Trace write and prior whole-dataset validation are outside total analysis timing."]))

    def write(self,status=None):
        payload=self.finish(status)
        path=self.directory/"trace.json"
        # New private file, no console output or sensitive exception strings.
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            json.dump(payload,handle,indent=2,ensure_ascii=False)
            handle.write("\n")
        return payload,path
