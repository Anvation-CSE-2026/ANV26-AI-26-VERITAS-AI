"""Offline review preparation only; never changes fixtures or scoring."""
import csv, hashlib, json
from collections import Counter
from pathlib import Path
from evaluation.dataset_loader import load_dataset, FIXTURES
from evaluation.schema import CATEGORIES

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
PROTECTED = list((ROOT / 'backend/app').rglob('*.py')) + list(FIXTURES.rglob('*')) + [ROOT/'backend/evaluation'/n for n in ('evaluator.py','risk_metrics.py','evidence_metrics.py','schema.py','dataset_loader.py')]
def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in PROTECTED if p.is_file()}
before = hashes()
dataset = load_dataset()
rows = []
issues = {
 'SYN-nda_durable': 'G03 assumes personal-data research although the PDF does not state personal-data processing. G01 is a local non-risk provision overridden by G02; do not infer whole-contract compliance.',
 'SYN-services_split': 'Data protection has two source spans across pages 1 and 2; primary span alone does not contain the risky deadline. Review both spans.',
 'SYN-saas_green': 'IP clause references Schedule A, which is not included; ownership language exists but schedule completeness is unverified.',
 'SYN-consulting_owned': 'IP clause references Schedule B, which is not included; pre-existing toolkit boundaries need review.',
 'SYN-supplier_failure': 'Data-breach language does not explicitly establish personal-data processing; review policy applicability.',
 'SYN-saas_red': 'Confidentiality ambiguity should be adjudicated against the explicit mutuality and survival requirements.',
 'SYN-services_balanced': 'Missing liability allocation requires protected-party and default allocation review; absence is not automatically adverse.'
}
matrix = {}
for case in dataset.cases:
    cid = case.contract.contract_id
    matrix[cid] = {}
    for g in case.annotations:
        state = 'D' if g.risk_category == 'governing_law' else ('B' if g.annotation_state == 'ambiguous' else 'C')
        matrix[cid][g.risk_category] = state
        rows.append(dict(contract_id=cid, annotation_id=g.finding_id, risk_category=g.risk_category,
            severity=g.expected_severity or '', evidence_page=g.expected_page_number or '',
            evidence_status='exact_all_spans_verified' if g.evidence_spans else 'absence_requires_human_review',
            coverage_status=state, row_type='existing_annotation', annotation_state=g.annotation_state,
            annotation_confidence=g.annotation_confidence, existing_reviewer_status=g.reviewer_status,
            evidence_quote=g.expected_clause_text or '', evidence_spans=json.dumps([s.model_dump() for s in g.evidence_spans],ensure_ascii=False),
            source_reference='fixtures/manifest.json:'+cid, policy_id=g.policy_id,
            audit_context=g.explanation + ' ' + issues.get(cid,'')))
    for cat in CATEGORIES:
        if cat in matrix[cid]: continue
        state = 'D' if cat == 'governing_law' else ('A' if cid == 'SYN-supplier_red' and cat == 'confidentiality' else 'B')
        matrix[cid][cat] = state
        reason = 'No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label.'
        if state == 'D': reason = 'Governing law is benchmark-only, outside production taxonomy; report separately.'
        if state == 'A': reason = 'Absent confidentiality obligations are a clear review candidate under the mutual confidentiality playbook; not an approved risk label or confirmed absence.'
        if cat == 'data_protection': reason += ' Personal-data processing is not established solely by silence.'
        if cat == 'intellectual_property': reason += ' Bespoke deliverables or an applicable licence interest must be established.'
        rows.append(dict(contract_id=cid,annotation_id='REVIEW-'+cid+'-'+cat,risk_category=cat,severity='',evidence_page='',evidence_status='no_quote_for_absence',coverage_status=state,row_type='coverage_gap_candidate',source_reference='fixtures/manifest.json:'+cid,audit_context=reason))
for number,cat,assessment in [(5,'confidentiality','Potentially valid unannotated omission; requires full-document human confirmation.'),(6,'data_protection','Ambiguous/context-dependent: personal-data applicability is not established by the source.'),(7,'intellectual_property','Ambiguous/context-dependent: bespoke-deliverable or licensing applicability is not established by the source.')]:
    rows.append(dict(contract_id='SYN-supplier_red',annotation_id='REVIEW-LIVE-SYN-supplier_red-LIVE-'+str(number).zfill(3),risk_category=cat,severity='medium',evidence_page='',evidence_status='needs_review_no_quote_absence_unconfirmed',coverage_status='A' if number==5 else 'B',row_type='unmatched_live_prediction',source_reference='synthetic_v1-live; run 1a9c514b-3b7b-4f60-839a-8d14558f60de; LIVE-'+str(number).zfill(3),audit_context=assessment+' No quotation, page or clause ID was provided. Correct policy category; retained missing finding is not evidence-verified absence.'))
headers=['contract_id','annotation_id','risk_category','severity','evidence_page','evidence_status','coverage_status','reviewer_decision','reviewer_notes','reviewer_id','reviewed_at','row_type','annotation_state','annotation_confidence','existing_reviewer_status','evidence_quote','evidence_spans','source_reference','policy_id','audit_context']
path=OUT/'gold_review_v1.csv'
if path.exists(): raise SystemExit('Refusing to overwrite a potentially reviewed worksheet')
with path.open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,headers); w.writeheader(); w.writerows(rows)
with path.open(newline='',encoding='utf-8-sig') as f: saved=list(csv.DictReader(f))
assert len(saved)==100 and len({r['annotation_id'] for r in saved})==100
assert all(not r[k] for r in saved for k in ['reviewer_decision','reviewer_notes','reviewer_id','reviewed_at'])
assert hashes()==before
annotations=[g for c in dataset.cases for g in c.annotations]
identities=[(g.contract_id,g.risk_category,g.annotation_state,tuple((s.clause_id,s.page_number,s.quote) for s in g.evidence_spans)) for g in annotations]
summary=dict(contracts=len(dataset.cases),annotations=len(annotations),evidence_spans=sum(len(g.evidence_spans) for g in annotations),states=dict(Counter(g.annotation_state for g in annotations)),confidence=dict(Counter(g.annotation_confidence for g in annotations)),reviewer_status=dict(Counter(g.reviewer_status for g in annotations)),severity=dict(Counter(str(g.expected_severity) for g in annotations)),categories=dict(Counter(g.risk_category for g in annotations)),duplicate_annotation_identities=len(identities)-len(set(identities)),worksheet_rows=len(rows),row_types=dict(Counter(r['row_type'] for r in rows)),coverage_matrix=matrix,protected_hashes_before=before,protected_files_unchanged=True)
(OUT/'gold_quality_audit_v1.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='protected_hashes_before'},indent=2))
