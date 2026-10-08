"""Rebuild original, hand-authored synthetic PDFs/gold/canned predictions, OFFLINE.
Gold labels below are independent author judgments under the documented playbook,
not predictions from a model. Predictions are a deliberately faulty separate plan.
"""
import hashlib
import json
from pathlib import Path
import pymupdf
from app.services.pdf_extraction import extract_contract

ROOT = Path(__file__).parent / "fixtures"
POLICIES = {
 "liability": "POL-LIAB-001", "indemnification": "POL-INDEM-001",
 "termination": "POL-TERM-001", "payment": "POL-PAY-001",
 "confidentiality": "POL-CONF-001", "data_protection": "POL-DATA-001",
 "intellectual_property": "POL-IP-001", "governing_law": "BENCH-LAW-001"
}
# Each clause: category, state, severity, original contractual text, review rationale.
# Missing annotations have no clause. A tuple of texts is an explicit cross-page clause.
SPECS = [
 ("supplier_red", "Supplier equipment agreement", [
 ("liability","risk","high","Supplier liability is limited to USD 50 in total, including fraud and data breaches.","A nominal cap with no carve-outs conflicts with the fee-based cap policy."),
 ("indemnification","risk","high","Company shall indemnify Supplier for every claim, including claims caused by Supplier negligence. Supplier owes no IP defense.","Allocates supplier misconduct to Company and omits supplier IP defense."),
 ("payment","non_risk","low","Undisputed invoices are payable in 30 days after receipt. Company may withhold disputed sums in good faith. Late interest is 1 percent per month.","Satisfies the stated invoice, dispute and interest assumptions."),
 ("termination","missing","medium",None,"No termination provision appears in this short synthetic agreement; absence requires full-document review.")]),
 ("supplier_green", "Supplier maintenance agreement", [
 ("liability","non_risk","low","Liability is capped at fees paid or payable in the preceding 12 months. Fraud, willful misconduct, confidentiality and data protection breaches are excluded from the cap.","Satisfies the sample liability rule."),
 ("indemnification","non_risk","low","Supplier will defend and indemnify Company against third-party IP infringement claims arising from supplied goods. Company gives no unlimited indemnity for Supplier misconduct.","Meets the supplier IP-defense expectation."),
 ("termination","risk","medium","Company may terminate for convenience only with 120 days notice and payment of all remaining service fees.","Notice and exit fee depart from the company rule."),
 ("governing_law","risk","medium","This agreement is governed by the laws of the fictional Republic of Norland, with disputes heard only in its capital.","Benchmark-only assumption prefers England and Wales; foreign venue needs review.")]),
 ("saas_red", "SaaS analytics subscription", [
 ("data_protection","risk","high","Provider must notify Company of a personal data breach within 9 days and delete retained data within 90 days after termination.","Exceeds the 48-hour notification and 30-day deletion limits."),
 ("intellectual_property","risk","high","Provider owns all bespoke dashboards. Company receives a revocable license that ends when the subscription ends.","Fails ownership or durable modification-license requirements."),
 ("payment","risk","medium","All invoices, including disputed sums, are due within 7 days. Late interest is 4 percent per month.","Short payment term, disputed payment and excessive interest conflict with policy."),
 ("confidentiality","ambiguous",None,"Provider protects Company information using reasonable efforts for an appropriate period.","Duration and reciprocal scope are undefined; context is insufficient.")]),
 ("saas_green", "SaaS records subscription", [
 ("data_protection","non_risk","low","Provider applies access controls and encryption, notifies Company of a breach within 48 hours of discovery, and returns or deletes data within 30 days of termination.","Meets the illustrative notification, security and deletion rule."),
 ("intellectual_property","non_risk","low","Company owns bespoke deliverables. Provider retains only pre-existing modules listed in Schedule A.","Provides bespoke ownership and identifies retained pre-existing material."),
 ("payment","non_risk","low","Company pays undisputed invoices in 45 days after receipt and may withhold disputed sums in good faith. Late interest is 0.5 percent monthly.","Within the company payment rule."),
 ("governing_law","non_risk","low","The law of England and Wales governs this agreement; courts in London hear disputes.","Meets benchmark-only illustrative jurisdiction assumption.")]),
 ("nda_short", "Mutual prototype NDA", [
 ("confidentiality","risk","medium","Each party shall use confidential information only for the project. All confidentiality duties end 6 months after disclosure, including trade secrets.","Mutual use restriction does not cure deficient survival."),
 ("liability","risk","high","Liability for disclosure of confidential information is capped at USD 10.","Nominal confidentiality cap conflicts with the exception requirement."),
 ("intellectual_property","ambiguous",None,"Ownership of ideas shared in workshops will be agreed later by the parties.","No present allocation; NDA context may differ from bespoke work policy.")]),
 ("nda_durable", "Mutual research NDA", [
 ("confidentiality","non_risk","low","Both parties use disclosed information only for this research. Duties survive for 4 years after termination and trade secrets remain protected while secret.","Meets mutual purpose and survival assumptions."),
 ("confidentiality","risk","medium","Despite the preceding clause, Recipient may publish any confidential report after 10 days without consent.","Separate publication override undermines the otherwise protective duty."),
 ("data_protection","missing","medium",None,"Synthetic research involves personal data but includes no breach-notification requirement.")]),
 ("services_exit", "Facilities services agreement", [
 ("termination","risk","medium","Supplier may terminate immediately for any Company breach, without a cure period. Company has no convenience termination right.","No cure or company exit protection."),
 ("indemnification","risk","high","Company shall defend Supplier from claims caused solely by Supplier misconduct, without a financial limit.","Explicitly unlimited protection for supplier misconduct."),
 ("payment","non_risk","low","Company owes undisputed invoices in 30 days after receipt, may withhold disputed sums in good faith, and owes no late interest.","Matches payment assumptions.")]),
 ("services_balanced", "Technical support services", [
 ("termination","non_risk","low","Either party may terminate for material breach after a 20-day cure period. Company may terminate for convenience on 30 days notice without penalty.","Meets cure and exit limits."),
 ("indemnification","non_risk","low","Supplier defends and indemnifies Company for third-party IP claims. Company does not indemnify Supplier for Supplier misconduct.","Opposite allocation from the superficially similar risky indemnity."),
 ("governing_law","ambiguous",None,"Applicable law and forum will be selected by mutual agreement following a dispute.","Jurisdiction remains undecided."),
 ("liability","missing","medium",None,"No fee-based liability allocation is included in this synthetic services contract.")]),
 ("consulting_owned", "Design consulting engagement", [
 ("intellectual_property","non_risk","low","Company owns all custom designs upon creation. Consultant retains the pre-existing toolkit named in Schedule B.","Bespoke ownership is explicit."),
 ("confidentiality","risk","medium","Consultant may use Company confidential information for any client and owes no confidentiality duty after completion.","Purpose and survival protections are absent."),
 ("payment","risk","medium","Company shall pay even disputed invoices in 5 days with late interest of 2 percent per month.","Departs from all three payment expectations.")]),
 ("consulting_retained", "Engineering consulting engagement", [
 ("intellectual_property","risk","high","Consultant retains custom designs and grants Company a temporary, non-transferable license with no right to modify.","Neither ownership nor qualifying perpetual modification license."),
 ("confidentiality","non_risk","low","Both parties use information only for the engagement, preserve secrecy for 3 years after termination, and protect trade secrets while secret.","Meets the company confidentiality rule."),
 ("termination","ambiguous",None,"Company may end the engagement on reasonable notice subject to fair compensation.","Notice duration and whether compensation is a penalty are unclear.")]),
 ("services_split", "Page-spanning hosting services", [
 ("data_protection","risk","high",("Provider shall notify Company of a personal data breach","within 8 days and delete personal data within 60 days after exit."),"One legal clause spans two pages; the second fragment contains the risky deadlines."),
 ("liability","non_risk","low","The cap is fees paid or payable in the preceding 12 months; fraud, willful misconduct, confidentiality and data protection breaches are uncapped.","Meets the sample cap and exclusions."),
 ("payment","risk","medium","Disputed invoices are payable within 10 days; interest accrues at 3 percent monthly.","Dispute handling and terms conflict with policy.")]),
 ("supplier_failure", "Synthetic logistics agreement", [
 ("liability","risk","high","Carrier liability, including fraud and data incidents, is capped at USD 25.","Nominal inclusive cap violates the illustrative liability rule."),
 ("data_protection","risk","high","Carrier will notify Company of a data breach within 12 days.","Notification exceeds 48 hours."),
 ("termination","risk","medium","Company must give 100 days notice and pay a termination penalty of USD 5000.","Excessive notice and penalty conflict with policy."),
 ("governing_law","risk","medium","The laws and exclusive courts of the fictional Kingdom of Eridia govern.","Benchmark-only foreign law departure.")]),
]
# Explicit fixture predictions: source clause index, predicted category, severity, mutation.
# These are evaluator test inputs, NOT the model or gold. Missing and failures explicit.
PLANS = {
 "supplier_red": [(0,"liability","high","ok"),(0,"liability","high","duplicate"),(1,"indemnification","high","ok"),(2,"payment","medium","false_positive")],
 "supplier_green": [(2,"termination","high","ok"),(3,"governing_law","medium","ok")],
 "saas_red": [(0,"data_protection","high","normalized"),(1,"liability","medium","ok"),(2,"payment","medium","wrong_page"),(3,"confidentiality","high","ok")],
 "saas_green": [(0,"data_protection","high","fabricated")],
 "nda_short": [(0,"confidentiality","medium","ok"),(1,"liability","high","unknown_clause")],
 "nda_durable": [(1,"confidentiality","medium","ok"),(-1,"data_protection","medium","missing")],
 "services_exit": [(0,"termination","medium","empty_quote")],
 "services_balanced": [(-1,"liability","medium","missing")],
 "consulting_owned": [(1,"confidentiality","medium","ok"),(2,"payment","medium","ok")],
 "consulting_retained": [(0,"intellectual_property","high","ok")],
 "services_split": [(0,"data_protection","high","second_fragment")],
 "supplier_failure": []
}

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def build():
    entries, outcomes = [], []
    for slug, title, clauses in SPECS:
        cid = "SYN-" + slug
        doc = pymupdf.open()
        # Put one numbered clause on each page. Split clause intentionally spans two.
        for index, (_, state, _, text, _) in enumerate(clauses):
            if state == "missing":
                continue
            chunks = text if isinstance(text, tuple) else (text,)
            for fragment, chunk in enumerate(chunks):
                page = doc.new_page(width=595, height=842)
                heading = f"SYNTHETIC CONTRACT - {title}\n"
                numbered = f"{index + 1}. " if fragment == 0 else ""
                spare = page.insert_textbox(pymupdf.Rect(48,48,547,794),
                    heading + numbered + chunk, fontsize=12, fontname="helv")
                if spare < 0:
                    raise ValueError("Fixture PDF text overflow")
        pdf_path = ROOT / "contracts" / (slug + ".pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        doc.set_metadata({"title": title, "author": "VERITAS synthetic benchmark", "creationDate": "D:20261008000000"})
        doc.save(pdf_path, no_new_id=True, deflate=True)
        doc.close()
        contract = extract_contract(pdf_path.read_bytes(), slug + ".pdf")
        contract.contract_id = cid
        source = contract.model_dump()
        # Original author text establishes gold intent; exact extracted substring
        # accounts for PDF line wrapping without changing the original source.
        page_cursor, gold, source_spans = 1, [], {}
        for index, (cat, state, sev, text, reason) in enumerate(clauses):
            spans = []
            if state != "missing":
                chunks = text if isinstance(text, tuple) else (text,)
                for fragment, chunk in enumerate(chunks):
                    c = [c for c in contract.clauses if c.page_number == page_cursor][-1]
                    quote = c.text
                    spans.append(dict(clause_id=c.clause_id,page_number=c.page_number,quote=quote))
                    page_cursor += 1
                source_spans[index] = spans
            gold.append(dict(contract_id=cid, finding_id=f"{cid}-G{index + 1:02d}",
                risk_category=cat, expected_severity=sev,
                expected_clause_text=spans[0]["quote"] if spans else None,
                expected_page_number=spans[0]["page_number"] if spans else None,
                explanation=reason, risk_present={"risk":True,"non_risk":False,"missing":True,"ambiguous":None}[state],
                annotation_state=state, annotation_confidence="medium" if state in ("missing","ambiguous") else "high",
                reviewer_status="pending_manual_review",policy_id=POLICIES[cat],evidence_spans=spans))
        predictions = []
        for n,(index,cat,sev,mutation) in enumerate(PLANS[slug]):
            p = dict(prediction_id=f"{cid}-P{n + 1:02d}",risk_category=cat,severity=sev,
                     finding_status="missing" if mutation == "missing" else "risky",policy_id=POLICIES[cat])
            if index >= 0:
                s = source_spans[index][-1] if mutation == "second_fragment" else source_spans[index][0]
                p.update(evidence_quote=s["quote"],page_number=s["page_number"],clause_id=s["clause_id"])
                if mutation == "normalized":
                    p["evidence_quote"] = " ".join(s["quote"].split())
                if mutation == "wrong_page":
                    p["page_number"] = 1 if s["page_number"] != 1 else 2
                if mutation == "fabricated":
                    p["evidence_quote"] = "Provider guarantees zero breaches forever."
                if mutation == "unknown_clause":
                    p["clause_id"] = "P999-C999"
                if mutation == "empty_quote":
                    p["evidence_quote"] = ""
            predictions.append(p)
        status = "failed" if slug == "supplier_failure" else "partial" if slug == "services_split" else "completed"
        outcome = dict(contract_id=cid,status=status,predictions=predictions)
        if status == "failed":
            outcome.update(error_category="fixture_provider_transient",failed_stage="gemini_reasoning",
                           http_status=503,upstream_http_status=503,attempts=3,failure_recorded=True)
        if status == "partial":
            outcome.update(rejected_finding_count=1,error_category="fixture_evidence_rejection")
        outcomes.append(outcome)
        dump(ROOT / "contracts" / (slug + ".json"), source)
        dump(ROOT / "annotations" / (slug + ".json"), gold)
        entries.append(dict(contract_id=cid,type=title,pdf=f"contracts/{slug}.pdf",
                            source=f"contracts/{slug}.json",annotations=f"annotations/{slug}.json"))
    dump(ROOT / "predictions.json",outcomes)
    playbook = json.loads((Path(__file__).resolve().parents[1] / "app/resources/sample_playbook.json").read_text(encoding="utf-8"))
    playbook["benchmark_only_rules"] = [dict(policy_id="BENCH-LAW-001", category="governing_law",
        rule="For this synthetic benchmark only, Company prefers England and Wales law with London courts; foreign exclusive law/forum requires negotiation review.")]
    dump(ROOT / "benchmark_playbook.json", playbook)
    files = [e[k] for e in entries for k in ("pdf","source","annotations")] + ["predictions.json", "benchmark_playbook.json"]
    dump(ROOT / "manifest.json",dict(dataset_id="synthetic_v1",version="1.0.0",
        synthetic=True,gold_provenance="Original author labels, not legally validated; pending human review",
        policy_ids=list(POLICIES.values()),production_unsupported_categories=["governing_law"],
        predictions="predictions.json",contracts=entries,
        file_hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}))

if __name__ == "__main__":
    build()
    print("Built 12 synthetic contracts, original annotations and deliberately imperfect fixture predictions; no API calls.")
