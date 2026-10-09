# Priority 1 gold dataset preliminary adjudication

Date: 2026-10-09. Dataset: synthetic_v1 v1.0.0. Branch: feature/ai-reliability.

**These are AI-generated preliminary recommendations. No gold labels have been changed or human-approved.**

## Executive summary

Reviewed all 27 items marked Priority 1 in the human pack (24 definite risk/missing gold labels and 3 unmatched model rows). Added the five other supplier_red worksheet items required by this task: its payment gold label and four missing-category prompts. Total: 32 mapped recommendations. Overlapping coverage/model rows are separate worksheet items, not independent new gold risks.

Priority 1 dispositions: NEEDS_EXPERT_REVIEW=11, PROPOSE_APPROVE=13, PROPOSE_REVISE=3. All 32 dispositions: NEEDS_EXPERT_REVIEW=14, PROPOSE_APPROVE=15, PROPOSE_REVISE=3.

Recommendations assess deviations from the supplied synthetic playbook, not legal enforceability, regulatory duties or real-world liability. All 12 canonical contracts and gold files were inspected and revalidated against their PDFs. The audit, worksheet, human pack, first-live forensic report, observability report and retained synthetic trace supplied context. The old first-live discarded proposals remain unavailable; their wording is not reconstructed. Model critical liability severity does not establish that gold high is wrong.

The strongest questionable definite labels concern NDA personal-data processing, carrier personal-data applicability and adverse inference from absence of a supplier liability cap. Most explicit policy violations are source-supported; severity is much less calibrated. No definitive false-positive/hallucination determination follows simply from unmatched scores.

## Scope, worksheet mapping and recommendation semantics

[Recommendations CSV](../backend/evaluation/reviews/priority1_recommendations.csv) is separate from [the unchanged human worksheet](../backend/evaluation/reviews/gold_review_v1.csv). worksheet_row is a CSV record ordinal excluding its header, not a physical line number. PROPOSE_APPROVE supports the existing synthetic label or candidate provisionally; it is not a human decision. PROPOSE_REVISE specifies an ambiguity/state change for a future reviewed version. PROPOSE_REJECT would require established incorrectness; none was forced solely from missing context. NEEDS_EXPERT_REVIEW defers disposition or severity. Blank proposed severity means unresolved, not zero/low. CSV confidence is confidence in the whole preliminary recommendation, not statistical accuracy; classification confidence can exceed severity confidence. requires_expert_review flags blocked decisions/revisions, not legal certification of other rows.

## SYN-supplier_red — complete-document review

Contract type: supplier equipment agreement. All three pages were inspected. No schedules, fee table, duration, incorporated terms, processing description, bespoke scope or separate confidentiality/termination/IP ownership/law clause is supplied. No contradiction between the three visible clauses was identified. Page 1 liability data-breach wording supplies no personal-data role; page 2 IP defense wording concerns indemnification, not deliverables ownership.

**Exact page 1 text:**

> SYNTHETIC CONTRACT - Supplier equipment agreement
> 1. Supplier liability is limited to USD 50 in total, including fraud and data breaches.

**Exact page 2 text:**

> SYNTHETIC CONTRACT - Supplier equipment agreement
> 2. Company shall indemnify Supplier for every claim, including claims caused by Supplier
> negligence. Supplier owes no IP defense.

**Exact page 3 text:**

> SYNTHETIC CONTRACT - Supplier equipment agreement
> 3. Undisputed invoices are payable in 30 days after receipt. Company may withhold disputed
> sums in good faith. Late interest is 1 percent per month.

### SYN-supplier_red-G01 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_red / 1 / 1.

**Current classification:** risk; category liability; severity high.

**Applicable synthetic policy:** POL-LIAB-001 — Aggregate supplier liability must be at least the fees paid or payable in the preceding 12 months. Fraud, willful misconduct, confidentiality breaches, and data protection breaches must be excluded from the cap.

**Evidence reference:** page 1 P001-C002; POL-LIAB-001.

**Original gold explanation:** A nominal cap with no carve-outs conflicts with the fee-based cap policy.

**Exact evidence — page 1, P001-C002:**

> 1. Supplier liability is limited to USD 50 in total, including fraud and data breaches.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category liability, severity high.

**Supporting reasoning / applicability / impact:** Explicit fraud and data-breach inclusion contradicts required carve-outs; a fixed USD 50 cap is not a fee-linked formula. High is a provisional structural-impact label, not a quantified loss estimate.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** What are the fees, insured limits and foreseeable losses? The source does not prove fees exceed USD 50.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-supplier_red-G02 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_red / 2 / 1.

**Current classification:** risk; category indemnification; severity high.

**Applicable synthetic policy:** POL-INDEM-001 — The supplier must defend and indemnify the company against third-party intellectual property infringement claims arising from supplier deliverables. The company must not give an unlimited indemnity for supplier misconduct.

**Evidence reference:** page 2 P002-C002; POL-INDEM-001.

**Original gold explanation:** Allocates supplier misconduct to Company and omits supplier IP defense.

**Exact evidence — page 2, P002-C002:**

> 2. Company shall indemnify Supplier for every claim, including claims caused by Supplier
> negligence. Supplier owes no IP defense.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category indemnification, severity high.

**Supporting reasoning / applicability / impact:** Every-claim company indemnity includes supplier negligence and expressly removes supplier IP defense. The misconduct transfer and missing defense directly contradict POL-INDEM-001. No financial limit is stated; legal unlimitedness is not established merely by that silence.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Are any external indemnity limits or insurance terms incorporated? What supplier goods create IP exposure?

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-supplier_red-G03 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_red / 3 / additional supplier review.

**Current classification:** non_risk; category payment; severity low.

**Applicable synthetic policy:** POL-PAY-001 — Undisputed invoices must be payable no earlier than 30 days after receipt. The company must be allowed to withhold disputed amounts in good faith and late charges must not exceed 1 percent per month.

**Evidence reference:** page 3 P003-C002; POL-PAY-001.

**Original gold explanation:** Satisfies the stated invoice, dispute and interest assumptions.

**Exact evidence — page 3, P003-C002:**

> 3. Undisputed invoices are payable in 30 days after receipt. Company may withhold disputed
> sums in good faith. Late interest is 1 percent per month.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state non_risk, category payment, severity low.

**Supporting reasoning / applicability / impact:** Thirty days after receipt, good-faith disputed-sum withholding and one percent monthly interest match all three payment criteria. Low is the existing non-risk sentinel, not an assertion of residual risk.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Confirm local compliance is the intended target, rather than whole-contract compliance.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-supplier_red-G04 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_red / 4 / 1.

**Current classification:** missing; category termination; severity medium.

**Applicable synthetic policy:** POL-TERM-001 — The company must be able to terminate for material breach after a cure period of no more than 30 days and terminate for convenience on no more than 30 days notice without a penalty.

**Evidence reference:** Complete PDF pages 1–3; no supporting quotation for absence; POL-TERM-001.

**Original gold explanation:** No termination provision appears in this short synthetic agreement; absence requires full-document review.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state missing, category termination, severity medium.

**Supporting reasoning / applicability / impact:** Complete pages 1–3 contain no express breach-cure or company convenience termination provision. The procurement policy expressly requires those protections. Approve the synthetic omission target provisionally; do not infer absence of all legal termination remedies.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Are these three pages the complete agreement? What term, exit cost and incorporated terms affect medium severity?

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### REVIEW-SYN-supplier_red-confidentiality — POTENTIAL MISSING LABEL

**Contract / worksheet record / priority:** SYN-supplier_red / 5 / additional supplier review.

**Current classification:** unannotated; category confidentiality; severity unassigned.

**Applicable synthetic policy:** POL-CONF-001 — Both parties must protect confidential information, restrict use to contract performance, and preserve confidentiality for at least three years after termination, with trade secrets protected while they remain trade secrets.

**Evidence reference:** Complete PDF pages 1–3; no supporting quotation for absence; POL-CONF-001.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state missing, category confidentiality, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** Pages 1–3 contain no mutual confidentiality, purpose restriction, survival or trade-secret protection. POL-CONF-001 states an unconditional synthetic requirement. Potentially valid missing protection (A); provision absence is source-supported, not human-approved or a verified real-world legal risk.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Confirm this is the complete agreement and that the playbook applies. Impact, information sensitivity and severity are unestablished; do not adopt the model medium automatically.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### REVIEW-SYN-supplier_red-data_protection — POTENTIAL MISSING LABEL

**Contract / worksheet record / priority:** SYN-supplier_red / 6 / additional supplier review.

**Current classification:** unannotated; category data_protection; severity unassigned.

**Applicable synthetic policy:** POL-DATA-001 — The supplier must notify the company of a personal data breach within 48 hours of discovery, implement appropriate security measures, and delete or return company personal data within 30 days after termination.

**Evidence reference:** Complete PDF pages 1–3; no supporting quotation for absence; POL-DATA-001.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state ambiguous, category data_protection, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** Pages 1–3 contain no notification, security or personal-data return/deletion duties. Page 1 mentions data breaches only as liability events; it does not establish personal-data processing. Applicability is ambiguous (D); treating processing as fact would be an unsupported assumption (B).

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Does equipment supply involve company personal data? What supplier processing role and data types exist?

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### REVIEW-SYN-supplier_red-intellectual_property — POTENTIAL MISSING LABEL

**Contract / worksheet record / priority:** SYN-supplier_red / 7 / additional supplier review.

**Current classification:** unannotated; category intellectual_property; severity unassigned.

**Applicable synthetic policy:** POL-IP-001 — The company must own bespoke deliverables paid for under the agreement or receive a perpetual, irrevocable, worldwide license sufficient to use and modify them. Pre-existing supplier IP must be identified separately.

**Evidence reference:** Complete PDF pages 1–3; no supporting quotation for absence; POL-IP-001.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state ambiguous, category intellectual_property, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** No ownership or durable deliverables licence appears on pages 1–3. Page 2 says Supplier owes no IP defense, an indemnification provision, not ownership evidence. Bespoke deliverables or licence needs are unestablished. Applicability is ambiguous (D), with insufficient supporting context (E).

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Does the equipment include paid bespoke designs/software/deliverables, and what ongoing licence does company need?

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### REVIEW-SYN-supplier_red-governing_law — POTENTIAL MISSING LABEL

**Contract / worksheet record / priority:** SYN-supplier_red / 8 / additional supplier review.

**Current classification:** unannotated; category governing_law; severity unassigned.

**Applicable synthetic policy:** BENCH-LAW-001 — For this synthetic benchmark only, Company prefers England and Wales law with London courts; foreign exclusive law/forum requires negotiation review.

**Evidence reference:** Complete PDF pages 1–3; no supporting quotation for absence; BENCH-LAW-001.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state ambiguous, category governing_law, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** No law/forum provision appears on pages 1–3. BENCH-LAW-001 prefers a specified forum and foreign-exclusive terms trigger review; silence is not an express foreign-law departure. Unsupported by production taxonomy.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Does benchmark policy require an affirmative law/forum clause? Do not infer governing law or legal outcome from silence.

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### REVIEW-LIVE-SYN-supplier_red-LIVE-005 — MODEL-GENERATED FINDING

**Contract / worksheet record / priority:** SYN-supplier_red / 98 / 1.

**Current classification:** missing; category confidentiality; severity medium.

**Applicable synthetic policy:** POL-CONF-001 — Both parties must protect confidential information, restrict use to contract performance, and preserve confidentiality for at least three years after termination, with trade secrets protected while they remain trade secrets.

**Evidence reference:** Complete PDF pages 1–3; no supporting quotation for absence; POL-CONF-001.

**Original model explanation, not an established conclusion:** POTENTIAL OMISSION: The contract lacks confidentiality obligations. Full-document coverage and human review are required before confirming absence.

**Existing trace outcome:** retained; evidence_status=needs_review; quote/page/clause ID absent; absence_confirmed=false. Trace run 1a9c514b-3b7b-4f60-839a-8d14558f60de.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state missing, category confidentiality, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** Pages 1–3 contain no mutual confidentiality, purpose restriction, survival or trade-secret protection. POL-CONF-001 states an unconditional synthetic requirement. Potentially valid missing protection (A); provision absence is source-supported, not human-approved or a verified real-world legal risk.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Confirm this is the complete agreement and that the playbook applies. Impact, information sensitivity and severity are unestablished; do not adopt the model medium automatically.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### REVIEW-LIVE-SYN-supplier_red-LIVE-006 — MODEL-GENERATED FINDING

**Contract / worksheet record / priority:** SYN-supplier_red / 99 / 1.

**Current classification:** missing; category data_protection; severity medium.

**Applicable synthetic policy:** POL-DATA-001 — The supplier must notify the company of a personal data breach within 48 hours of discovery, implement appropriate security measures, and delete or return company personal data within 30 days after termination.

**Evidence reference:** Complete PDF pages 1–3; no supporting quotation for absence; POL-DATA-001.

**Original model explanation, not an established conclusion:** POTENTIAL OMISSION: The contract does not contain data protection or breach notification obligations. Full-document coverage and human review are required before confirming absence.

**Existing trace outcome:** retained; evidence_status=needs_review; quote/page/clause ID absent; absence_confirmed=false. Trace run 1a9c514b-3b7b-4f60-839a-8d14558f60de.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state ambiguous, category data_protection, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** Pages 1–3 contain no notification, security or personal-data return/deletion duties. Page 1 mentions data breaches only as liability events; it does not establish personal-data processing. Applicability is ambiguous (D); treating processing as fact would be an unsupported assumption (B).

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Does equipment supply involve company personal data? What supplier processing role and data types exist?

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### REVIEW-LIVE-SYN-supplier_red-LIVE-007 — MODEL-GENERATED FINDING

**Contract / worksheet record / priority:** SYN-supplier_red / 100 / 1.

**Current classification:** missing; category intellectual_property; severity medium.

**Applicable synthetic policy:** POL-IP-001 — The company must own bespoke deliverables paid for under the agreement or receive a perpetual, irrevocable, worldwide license sufficient to use and modify them. Pre-existing supplier IP must be identified separately.

**Evidence reference:** Complete PDF pages 1–3; no supporting quotation for absence; POL-IP-001.

**Original model explanation, not an established conclusion:** POTENTIAL OMISSION: The contract does not address intellectual property ownership or licensing of deliverables. Full-document coverage and human review are required before confirming absence.

**Existing trace outcome:** retained; evidence_status=needs_review; quote/page/clause ID absent; absence_confirmed=false. Trace run 1a9c514b-3b7b-4f60-839a-8d14558f60de.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state ambiguous, category intellectual_property, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** No ownership or durable deliverables licence appears on pages 1–3. Page 2 says Supplier owes no IP defense, an indemnification provision, not ownership evidence. Bespoke deliverables or licence needs are unestablished. Applicability is ambiguous (D), with insufficient supporting context (E).

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Does the equipment include paid bespoke designs/software/deliverables, and what ongoing licence does company need?

**Expert review required to resolve this item:** true. No reviewer decision is entered.

## Three unmatched Gemini findings: classification summary

| Finding | Absence in pages 1–3 | Applicability / A–E assessment | Preliminary result |
|---|---|---|---|
| LIVE-005 confidentiality | No confidentiality provision | A: potentially valid missing protection under an unconditional playbook rule; impact context still missing | PROPOSE_APPROVE omission candidate; severity deferred |
| LIVE-006 data protection | No notification/security/return duties | D: ambiguous processing applicability; B if processing is assumed as fact | NEEDS_EXPERT_REVIEW, not confirmed hallucination |
| LIVE-007 IP | No deliverables ownership/licence clause | D: ambiguous bespoke/licence scope; E: insufficient context; no-IP-defense is a different issue | NEEDS_EXPERT_REVIEW, not confirmed hallucination |

No C (demonstrably incorrect interpretation) is established merely from absence of gold. No model severity is adopted automatically. These three corresponding missing-label rows overlap the model rows and must be adjudicated once per underlying issue, then reflected consistently in both review records.

## Remaining Priority 1 reviews

### SYN-supplier_green-G03 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_green / 11 / 1.

**Current classification:** risk; category termination; severity medium.

**Applicable synthetic policy:** POL-TERM-001 — The company must be able to terminate for material breach after a cure period of no more than 30 days and terminate for convenience on no more than 30 days notice without a penalty.

**Evidence reference:** page 3 P003-C002; POL-TERM-001.

**Original gold explanation:** Notice and exit fee depart from the company rule.

**Exact evidence — page 3, P003-C002:**

> 3. Company may terminate for convenience only with 120 days notice and payment of all
> remaining service fees.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state risk, category termination, severity medium.

**Supporting reasoning / applicability / impact:** 120 days exceeds the 30-day convenience threshold; all remaining fees create express exit exposure. Risk classification is clear, but medium may understate a long or expensive remaining term.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Remaining term and fees are absent; retain risk category but adjudicate medium versus high.

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-supplier_green-G04 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_green / 12 / 1.

**Current classification:** risk; category governing_law; severity medium.

**Applicable synthetic policy:** BENCH-LAW-001 — For this synthetic benchmark only, Company prefers England and Wales law with London courts; foreign exclusive law/forum requires negotiation review.

**Evidence reference:** page 4 P004-C002; BENCH-LAW-001.

**Original gold explanation:** Benchmark-only assumption prefers England and Wales; foreign venue needs review.

**Exact evidence — page 4, P004-C002:**

> 4. This agreement is governed by the laws of the fictional Republic of Norland, with disputes
> heard only in its capital.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state risk, category governing_law, severity medium.

**Supporting reasoning / applicability / impact:** Fictional foreign exclusive law/forum departs from BENCH-LAW-001. This is a benchmark preference deviation, not demonstrated legal harm; medium lacks cost/enforcement context.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Confirm benchmark-only scope and review forum burden without inventing fictional jurisdiction law.

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-saas_red-G01 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-saas_red / 17 / 1.

**Current classification:** risk; category data_protection; severity high.

**Applicable synthetic policy:** POL-DATA-001 — The supplier must notify the company of a personal data breach within 48 hours of discovery, implement appropriate security measures, and delete or return company personal data within 30 days after termination.

**Evidence reference:** page 1 P001-C002; POL-DATA-001.

**Original gold explanation:** Exceeds the 48-hour notification and 30-day deletion limits.

**Exact evidence — page 1, P001-C002:**

> 1. Provider must notify Company of a personal data breach within 9 days and delete retained
> data within 90 days after termination.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category data_protection, severity high.

**Supporting reasoning / applicability / impact:** Personal data is explicit. Nine-day breach notification and ninety-day deletion exceed both stated policy limits. High is provisionally consistent with multiple prolonged protection deviations.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Data sensitivity/volume and notification trigger are unspecified; no regulatory violation or incident likelihood is inferred.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-saas_red-G02 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-saas_red / 18 / 1.

**Current classification:** risk; category intellectual_property; severity high.

**Applicable synthetic policy:** POL-IP-001 — The company must own bespoke deliverables paid for under the agreement or receive a perpetual, irrevocable, worldwide license sufficient to use and modify them. Pre-existing supplier IP must be identified separately.

**Evidence reference:** page 2 P002-C002; POL-IP-001.

**Original gold explanation:** Fails ownership or durable modification-license requirements.

**Exact evidence — page 2, P002-C002:**

> 2. Provider owns all bespoke dashboards. Company receives a revocable license that ends
> when the subscription ends.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category intellectual_property, severity high.

**Supporting reasoning / applicability / impact:** Bespoke dashboards are explicit; a revocable licence ending with subscription provides neither ownership nor the required durable licence. High provisionally reflects loss of continued access, not quantified loss.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Payment for bespoke work and operational dependence are unspecified; confirm scope and impact.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-saas_red-G03 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-saas_red / 19 / 1.

**Current classification:** risk; category payment; severity medium.

**Applicable synthetic policy:** POL-PAY-001 — Undisputed invoices must be payable no earlier than 30 days after receipt. The company must be allowed to withhold disputed amounts in good faith and late charges must not exceed 1 percent per month.

**Evidence reference:** page 3 P003-C002; POL-PAY-001.

**Original gold explanation:** Short payment term, disputed payment and excessive interest conflict with policy.

**Exact evidence — page 3, P003-C002:**

> 3. All invoices, including disputed sums, are due within 7 days. Late interest is 4 percent per
> month.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category payment, severity medium.

**Supporting reasoning / applicability / impact:** Seven-day payment including disputes and four percent monthly interest contradict payment/dispute/interest criteria. Medium is a provisional commercial-severity convention.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Invoice amounts and duration determine impact; a fee-sensitive case could warrant higher severity.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-nda_short-G01 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-nda_short / 33 / 1.

**Current classification:** risk; category confidentiality; severity medium.

**Applicable synthetic policy:** POL-CONF-001 — Both parties must protect confidential information, restrict use to contract performance, and preserve confidentiality for at least three years after termination, with trade secrets protected while they remain trade secrets.

**Evidence reference:** page 1 P001-C002; POL-CONF-001.

**Original gold explanation:** Mutual use restriction does not cure deficient survival.

**Exact evidence — page 1, P001-C002:**

> 1. Each party shall use confidential information only for the project. All confidentiality duties
> end 6 months after disclosure, including trade secrets.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state risk, category confidentiality, severity medium.

**Supporting reasoning / applicability / impact:** Ending all duties after six months including trade secrets conflicts with three-year survival and ongoing trade-secret protection. Risk is clear; medium may understate release of valuable secrets.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** What information is covered and how valuable or enduring is it? Approve risk only after severity adjudication.

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-nda_short-G02 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-nda_short / 34 / 1.

**Current classification:** risk; category liability; severity high.

**Applicable synthetic policy:** POL-LIAB-001 — Aggregate supplier liability must be at least the fees paid or payable in the preceding 12 months. Fraud, willful misconduct, confidentiality breaches, and data protection breaches must be excluded from the cap.

**Evidence reference:** page 2 P002-C002; POL-LIAB-001.

**Original gold explanation:** Nominal confidentiality cap conflicts with the exception requirement.

**Exact evidence — page 2, P002-C002:**

> 2. Liability for disclosure of confidential information is capped at USD 10.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state risk, category liability, severity high.

**Supporting reasoning / applicability / impact:** A USD 10 disclosure cap conflicts with the confidentiality carve-out if the supplier-liability policy applies. This mutual NDA does not identify a supplier liability role; policy scope and nominal-cap high severity need review.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Which party is protected, and should supplier-specific liability rules apply to a mutual NDA?

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-nda_durable-G02 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-nda_durable / 42 / 1.

**Current classification:** risk; category confidentiality; severity medium.

**Applicable synthetic policy:** POL-CONF-001 — Both parties must protect confidential information, restrict use to contract performance, and preserve confidentiality for at least three years after termination, with trade secrets protected while they remain trade secrets.

**Evidence reference:** page 2 P002-C002; POL-CONF-001.

**Original gold explanation:** Separate publication override undermines the otherwise protective duty.

**Exact evidence — page 2, P002-C002:**

> 2. Despite the preceding clause, Recipient may publish any confidential report after 10 days
> without consent.

**Full-document context / contradictions:** Page 2 expressly overrides page 1 protective confidentiality duties; for the data omission, neither page establishes personal-data processing. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state risk, category confidentiality, severity medium.

**Supporting reasoning / applicability / impact:** Despite the preceding clause expressly overrides otherwise protective confidentiality duties and allows publication after ten days. The risk is clear, but medium may understate irreversible disclosure exposure.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Which reports/secrets can be published? Review medium versus high and whole-contract effect on the preceding non-risk annotation.

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-nda_durable-G03 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-nda_durable / 43 / 1.

**Current classification:** missing; category data_protection; severity medium.

**Applicable synthetic policy:** POL-DATA-001 — The supplier must notify the company of a personal data breach within 48 hours of discovery, implement appropriate security measures, and delete or return company personal data within 30 days after termination.

**Evidence reference:** Complete PDF pages 1–2; no supporting quotation for absence; POL-DATA-001.

**Original gold explanation:** Synthetic research involves personal data but includes no breach-notification requirement.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** Page 2 expressly overrides page 1 protective confidentiality duties; for the data omission, neither page establishes personal-data processing. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_REVISE → state ambiguous, category data_protection, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** No breach-notification provision appears on complete pages 1–2, but the PDF does not establish personal-data research. Replace definite missing-risk treatment with applicability-ambiguous review pending context; do not invent data processing.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Does the research actually process company personal data? Require source context before confirming a personal-data omission or severity.

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-services_exit-G01 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-services_exit / 50 / 1.

**Current classification:** risk; category termination; severity medium.

**Applicable synthetic policy:** POL-TERM-001 — The company must be able to terminate for material breach after a cure period of no more than 30 days and terminate for convenience on no more than 30 days notice without a penalty.

**Evidence reference:** page 1 P001-C002; POL-TERM-001.

**Original gold explanation:** No cure or company exit protection.

**Exact evidence — page 1, P001-C002:**

> 1. Supplier may terminate immediately for any Company breach, without a cure period.
> Company has no convenience termination right.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state risk, category termination, severity medium.

**Supporting reasoning / applicability / impact:** Company has no convenience right, a direct policy deviation. Immediate supplier termination for company breach is visible, but POL-TERM-001 specifies company breach/cure rights, not a mandatory supplier cure period. Refine explanation and assess severity.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** What company material-breach exit rights exist? Are service continuity and term sufficient to justify medium or high?

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-services_exit-G02 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-services_exit / 51 / 1.

**Current classification:** risk; category indemnification; severity high.

**Applicable synthetic policy:** POL-INDEM-001 — The supplier must defend and indemnify the company against third-party intellectual property infringement claims arising from supplier deliverables. The company must not give an unlimited indemnity for supplier misconduct.

**Evidence reference:** page 2 P002-C002; POL-INDEM-001.

**Original gold explanation:** Explicitly unlimited protection for supplier misconduct.

**Exact evidence — page 2, P002-C002:**

> 2. Company shall defend Supplier from claims caused solely by Supplier misconduct, without
> a financial limit.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category indemnification, severity high.

**Supporting reasoning / applicability / impact:** Company defends solely supplier misconduct without a financial limit, an express unlimited allocation prohibited by policy. High is provisionally consistent with supplier_red indemnity exposure.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Claim magnitude, insurance and incorporated limitations remain unknown; no enforceability claim is made.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-services_balanced-G04 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-services_balanced / 61 / 1.

**Current classification:** missing; category liability; severity medium.

**Applicable synthetic policy:** POL-LIAB-001 — Aggregate supplier liability must be at least the fees paid or payable in the preceding 12 months. Fraud, willful misconduct, confidentiality breaches, and data protection breaches must be excluded from the cap.

**Evidence reference:** Complete PDF pages 1–3; no supporting quotation for absence; POL-LIAB-001.

**Original gold explanation:** No fee-based liability allocation is included in this synthetic services contract.

No quotation is offered as proof of absence. Complete page range above was inspected; provision absence is an AI source observation separate from policy applicability and human adjudication.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_REVISE → state ambiguous, category liability, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** No fee-based liability term appears on pages 1–3, but a minimum supplier-liability protection does not require imposing a supplier cap. Uncapped liability may favor the company. Definite adverse missing risk is not established; use ambiguous scope/state pending adjudication.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Does the policy require an express allocation even if no contractual supplier limit exists? What background allocation applies?

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-consulting_owned-G02 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-consulting_owned / 67 / 1.

**Current classification:** risk; category confidentiality; severity medium.

**Applicable synthetic policy:** POL-CONF-001 — Both parties must protect confidential information, restrict use to contract performance, and preserve confidentiality for at least three years after termination, with trade secrets protected while they remain trade secrets.

**Evidence reference:** page 2 P002-C002; POL-CONF-001.

**Original gold explanation:** Purpose and survival protections are absent.

**Exact evidence — page 2, P002-C002:**

> 2. Consultant may use Company confidential information for any client and owes no
> confidentiality duty after completion.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state risk, category confidentiality, severity medium.

**Supporting reasoning / applicability / impact:** Use for any client and no duty after completion contradict purpose limitation and survival. Risk is explicit; medium may understate broad onward use of valuable confidential material.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Information sensitivity and irreversible disclosure exposure determine medium versus high.

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-consulting_owned-G03 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-consulting_owned / 68 / 1.

**Current classification:** risk; category payment; severity medium.

**Applicable synthetic policy:** POL-PAY-001 — Undisputed invoices must be payable no earlier than 30 days after receipt. The company must be allowed to withhold disputed amounts in good faith and late charges must not exceed 1 percent per month.

**Evidence reference:** page 3 P003-C002; POL-PAY-001.

**Original gold explanation:** Departs from all three payment expectations.

**Exact evidence — page 3, P003-C002:**

> 3. Company shall pay even disputed invoices in 5 days with late interest of 2 percent per
> month.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category payment, severity medium.

**Supporting reasoning / applicability / impact:** Mandatory disputed invoices, five-day payment and two percent monthly interest all depart from policy. Medium is consistent with analogous synthetic payment labels.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Invoice values, credit exposure and time period are absent; severity is not quantitatively calibrated.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-consulting_retained-G01 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-consulting_retained / 74 / 1.

**Current classification:** risk; category intellectual_property; severity high.

**Applicable synthetic policy:** POL-IP-001 — The company must own bespoke deliverables paid for under the agreement or receive a perpetual, irrevocable, worldwide license sufficient to use and modify them. Pre-existing supplier IP must be identified separately.

**Evidence reference:** page 1 P001-C002; POL-IP-001.

**Original gold explanation:** Neither ownership nor qualifying perpetual modification license.

**Exact evidence — page 1, P001-C002:**

> 1. Consultant retains custom designs and grants Company a temporary, non-transferable
> license with no right to modify.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category intellectual_property, severity high.

**Supporting reasoning / applicability / impact:** Custom designs with temporary licence and no modification right cannot satisfy ownership or a perpetual sufficient modification licence. High provisionally reflects explicit continued-use/modification limitations.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Confirm paid bespoke scope and business dependence; non-transferability alone is not a named policy violation.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-services_split-G01 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-services_split / 82 / 1.

**Current classification:** risk; category data_protection; severity high.

**Applicable synthetic policy:** POL-DATA-001 — The supplier must notify the company of a personal data breach within 48 hours of discovery, implement appropriate security measures, and delete or return company personal data within 30 days after termination.

**Evidence reference:** page 1 P001-C002; page 2 P002-C001; POL-DATA-001.

**Original gold explanation:** One legal clause spans two pages; the second fragment contains the risky deadlines.

**Exact evidence — page 1, P001-C002:**

> 1. Provider shall notify Company of a personal data breach

**Exact evidence — page 2, P002-C001:**

> SYNTHETIC CONTRACT - Page-spanning hosting services
> within 8 days and delete personal data within 60 days after exit.

**Full-document context / contradictions:** The notification sentence continues on page 2; both spans are required to understand the deadline. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category data_protection, severity high.

**Supporting reasoning / applicability / impact:** Read both exact spans together: explicit personal-data breach followed on page 2 by eight-day notification and sixty-day deletion terms, exceeding 48 hours/30 days. High is structurally consistent with SaaS red.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Notification trigger and data impact remain unspecified; the primary page-1 fragment alone cannot establish the risky deadlines.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-services_split-G03 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-services_split / 84 / 1.

**Current classification:** risk; category payment; severity medium.

**Applicable synthetic policy:** POL-PAY-001 — Undisputed invoices must be payable no earlier than 30 days after receipt. The company must be allowed to withhold disputed amounts in good faith and late charges must not exceed 1 percent per month.

**Evidence reference:** page 4 P004-C002; POL-PAY-001.

**Original gold explanation:** Dispute handling and terms conflict with policy.

**Exact evidence — page 4, P004-C002:**

> 3. Disputed invoices are payable within 10 days; interest accrues at 3 percent monthly.

**Full-document context / contradictions:** The notification sentence continues on page 2; both spans are required to understand the deadline. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category payment, severity medium.

**Supporting reasoning / applicability / impact:** Disputed invoices payable within ten days contradict good-faith withholding and three percent monthly interest exceeds the limit. The clause does not specify undisputed invoice timing; do not invent that third deviation.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Are separate undisputed-payment terms incorporated? Invoice magnitude may alter medium severity.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-supplier_failure-G01 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_failure / 90 / 1.

**Current classification:** risk; category liability; severity high.

**Applicable synthetic policy:** POL-LIAB-001 — Aggregate supplier liability must be at least the fees paid or payable in the preceding 12 months. Fraud, willful misconduct, confidentiality breaches, and data protection breaches must be excluded from the cap.

**Evidence reference:** page 1 P001-C002; POL-LIAB-001.

**Original gold explanation:** Nominal inclusive cap violates the illustrative liability rule.

**Exact evidence — page 1, P001-C002:**

> 1. Carrier liability, including fraud and data incidents, is capped at USD 25.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_APPROVE → state risk, category liability, severity high.

**Supporting reasoning / applicability / impact:** USD 25 cap expressly includes fraud and data incidents instead of required carve-outs. High is structurally consistent with supplier_red, while the unknown fee amount prevents proving the fee-floor shortfall.

**Confidence:** medium in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Fees, carrier-specific scope and insured loss exposure are unspecified.

**Expert review required to resolve this item:** false. No reviewer decision is entered.

### SYN-supplier_failure-G02 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_failure / 91 / 1.

**Current classification:** risk; category data_protection; severity high.

**Applicable synthetic policy:** POL-DATA-001 — The supplier must notify the company of a personal data breach within 48 hours of discovery, implement appropriate security measures, and delete or return company personal data within 30 days after termination.

**Evidence reference:** page 2 P002-C002; POL-DATA-001.

**Original gold explanation:** Notification exceeds 48 hours.

**Exact evidence — page 2, P002-C002:**

> 2. Carrier will notify Company of a data breach within 12 days.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** PROPOSE_REVISE → state ambiguous, category data_protection, severity unassigned pending context.

**Supporting reasoning / applicability / impact:** Twelve-day data-breach notification is explicit, but data breach is not necessarily personal data. A definite personal-data high-risk label needs a processing premise; propose ambiguous applicability with severity unassigned.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Does this carrier process personal data? What event starts the deadline?

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-supplier_failure-G03 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_failure / 92 / 1.

**Current classification:** risk; category termination; severity medium.

**Applicable synthetic policy:** POL-TERM-001 — The company must be able to terminate for material breach after a cure period of no more than 30 days and terminate for convenience on no more than 30 days notice without a penalty.

**Evidence reference:** page 3 P003-C002; POL-TERM-001.

**Original gold explanation:** Excessive notice and penalty conflict with policy.

**Exact evidence — page 3, P003-C002:**

> 3. Company must give 100 days notice and pay a termination penalty of USD 5000.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state risk, category termination, severity medium.

**Supporting reasoning / applicability / impact:** 100-day notice and USD 5000 penalty conflict with no-more-than-30-day/no-penalty policy. Medium may overstate or understate impact depending on term and value.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Which termination rights are restricted and what is USD 5000 relative to contract value?

**Expert review required to resolve this item:** true. No reviewer decision is entered.

### SYN-supplier_failure-G04 — EXISTING GOLD LABEL

**Contract / worksheet record / priority:** SYN-supplier_failure / 93 / 1.

**Current classification:** risk; category governing_law; severity medium.

**Applicable synthetic policy:** BENCH-LAW-001 — For this synthetic benchmark only, Company prefers England and Wales law with London courts; foreign exclusive law/forum requires negotiation review.

**Evidence reference:** page 4 P004-C002; BENCH-LAW-001.

**Original gold explanation:** Benchmark-only foreign law departure.

**Exact evidence — page 4, P004-C002:**

> 4. The laws and exclusive courts of the fictional Kingdom of Eridia govern.

**Full-document context / contradictions:** No contrary protection was identified in the complete supplied PDF. Other-category protections do not automatically cure this policy deviation.

**Preliminary recommendation:** NEEDS_EXPERT_REVIEW → state risk, category governing_law, severity medium.

**Supporting reasoning / applicability / impact:** Fictional law and exclusive courts depart from BENCH-LAW-001; severity is a preference convention, not evidenced jurisdiction risk.

**Confidence:** low in the overall recommendation; exact quotation/absence observation is more certain than business impact.

**Unresolved questions / missing context:** Review benchmark scope and forum burden; no foreign-law enforceability facts are supplied.

**Expert review required to resolve this item:** true. No reviewer decision is entered.

## Potentially incorrect or incomplete gold labels

- NDA durable G03: explanation treats personal-data research as fact without source support. Proposed revision to ambiguous applicability; source absence alone is not the defect.
- Supplier failure G02: generic data breach does not establish a personal-data breach. Proposed ambiguous applicability, pending processing context.
- Services balanced G04: missing fee-cap language is not proof of harmful unlimited supplier exposure; minimum supplier liability and a cap are different protections. Proposed ambiguity pending policy intent.
- Services exit G01: no company convenience right is a clear deviation; supplier immediate termination without cure is not itself the company-cure requirement specified by policy. Explanation and severity need expert clarification.
- NDA short G02: supplier-specific liability policy applied to a mutual NDA requires party/scope adjudication.
- Supplier red G01 and supplier failure G01: missing carve-outs are explicit, but fee amounts are absent; do not claim a proven numeric floor shortfall. Supplier red G02 should distinguish no stated limit from a definitive legal unlimitedness conclusion.

## Potential missing gold annotations

Supplier_red confidentiality is a source-supported omission candidate under POL-CONF-001; it remains unapproved and severity unassigned. Data protection and bespoke-IP omissions require processing/deliverables context. Governing law is absent but BENCH-LAW-001 does not clearly turn silence into an adverse foreign-law departure; production taxonomy does not support it. Its review must be separate. Termination is already gold G04, not a new target. No additional candidate was silently inserted into gold.

## Severity consistency findings

No exact duplicated risk with conflicting severity was found. USD 10/25/50 liability caps are all high, but mutual-NDA scope differs and fees/losses are absent. Nine-/eight-day explicit personal-data cases are both high; twelve-day carrier notification is also high despite unestablished personal-data scope. IP temporary/revocable licence cases are both high, while paid scope and impact remain partly unstated. Payments at 2/3/4 percent and short terms are all medium, without exposure amounts. Termination notice/penalty, confidentiality release and governing-law deviations are medium, despite substantially different possible impacts.

All annotations have risk explanations, but those explanations generally justify policy deviation rather than why high versus medium. Confidentiality publication after ten days, trade-secret duty expiry and unrestricted other-client use may be more serious than medium if valuable irreversible disclosure is established. Exit fees for all remaining term or USD 5000 can be medium/high depending on value and continuity. These are severity-review candidates, not established mislabels. The 14 non-risk labels carry low; low is a schema convention, not proof of a risky clause. The three definite missing labels use medium without a calibrated impact basis. No source supports escalating supplier_red to critical solely because Gemini did so.

## Proposed severity rubric — not implemented

First determine applicability and risk state. Uncertain applicability stays ambiguous/needs review with no severity recommendation; missing protection requires complete-document evidence and applicable policy. Preserve uncertainty separately from impact: missing facts should not become assumed high likelihood or silently reduce severity.

| Band | Proposed impact criteria | Required support |
|---|---|---|
| Non-risk / not applicable | No established adverse policy deviation, or policy out of scope | Explicit compliant protection or supported applicability decision; no positive risk severity |
| Low | Narrow, readily remediable applicable deviation with demonstrably limited exposure and substantial retained protection | Scope/value evidence and protective carve-outs; not merely absence of incident history |
| Medium | Material applicable deviation affecting payment, exit or limited obligations, with bounded/manageable consequences | Relative monetary/operational impact, affected obligations and available mitigations |
| High | Broad misconduct indemnity, loss of essential IP rights, serious confidentiality/data exposure, or costly lock-in with important protection removed | Explicit allocation plus supported scope/value/dependency; serious likelihood or applicability justified rather than presumed |
| Critical | Exceptional exposure plausibly threatening core operations or causing catastrophic irreversible loss, with insufficient mitigation | Strong contract/business evidence of magnitude, applicability and protective failures; a small numeric cap alone is insufficient |

Record six dimensions independently: potential impact; exposure magnitude relative to agreement/business value; applicability and supported likelihood (do not invent probabilities); affected obligation scope/duration; protective carve-outs/mitigation; missing context and uncertainty. Use one documented protected-party perspective. Have qualified reviewers approve thresholds and anchor examples before applying a future rubric consistently.

## Qualified review and next steps

Expert-review flags identify uncertain policy applicability, severity or revisions; consult qualified contract/privacy/IP expertise where those questions require it. Recommendations not flagged remain preliminary synthetic-policy assessments, not enforceability opinions. Adjudicate the supplier confidentiality candidate and conditional omissions first; verify NDA/carrier processing scope; clarify minimum-liability versus cap intent; then calibrate severity and review remaining labels independently. Freeze a separately versioned gold set only after recorded human decisions and adjudication. Do not infer that the benchmark is legally validated from structural tests. No full live evaluation or production change is recommended as part of this task.

## Validation

All 27 Priority 1 IDs parsed from the existing pack are covered; all 32 CSV IDs and record ordinals match the unchanged worksheet. All original evidence quotations were rechecked against the exact cited source clause/page. Dataset loader re-extracted all 12 PDFs, verified manifest hashes and validated all gold. CSV was round-trip read, with exact requested columns, unique IDs and no reviewer identity/date columns. Human decision cells in the official worksheet remained blank and its hash unchanged. Gold, worksheet, scoring and production Python hashes remained unchanged. Only synthetic material was read; no database, provider, authentication or billing call occurred. Private trace content was summarized only for the synthetic findings; raw traces remain private and untracked.

Full offline regression command from backend: `.\.venv\Scripts\python.exe -m evaluation.run_offline_tests`. **144 passed, 3 live-service tests skipped, 0 failures/errors** (147 total), 10.165 seconds. Outbound network was blocked by the runner. Existing fixture scores remained TP=17, FP=3, FN=7; these are fixture results, not model accuracy. Final source/scoring hash comparison and blank-human-field checks passed. A pre-existing Starlette/httpx deprecation warning remains; no functionality failed.

Seventeen of 32 recommendation rows require expert review, including 14 of the 27 Priority 1 items (three proposed revisions plus eleven deferred decisions). The additional three expert flags are supplier data/IP/governing-law coverage prompts. No proposed rejection was manufactured to force a binary outcome. The confidentiality candidate and model observation overlap the same potential missing gold target.

Files created: docs/AI_PRIORITY_1_ADJUDICATION_REPORT.md and backend/evaluation/reviews/priority1_recommendations.csv.

**These are AI-generated preliminary recommendations. No gold labels have been changed or human-approved.**
