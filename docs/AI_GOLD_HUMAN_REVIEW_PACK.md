# Human gold-annotation review pack

Synthetic dataset v1.0.0 • prepared 2026-10-09 • feature/ai-reliability

This pack is a review aid, not a legal opinion or human approval. It represents all 12 synthetic contracts, 42 existing gold labels, 40 original evidence spans and 100 worksheet rows. Gold and scoring remain unchanged. Model output is segregated below; review source and gold before reading it to reduce anchoring.

## Reviewer instructions

Use [the worksheet](../backend/evaluation/reviews/gold_review_v1.csv) as the decision record. Every item below names its exact annotation_id and CSV record ordinal (header excluded; quoted multiline cells mean this is not a text-file line number). The existing gold IDs and REVIEW-* candidate IDs are distinct. All REVIEWER DECISION fields remain blank.

- **APPROVE**: agree with the existing label, or approve a clearly evidenced candidate for a future gold version. This does not itself edit current gold. Confirm applicability, state, category, severity and all spans.
- **REJECT**: reject the annotation/candidate with a source-based reason; distinguish not applicable from incorrect interpretation.
- **REVISE**: record the proposed state/category/severity/quote/page change precisely; retain the original ID and explain why.
- **NEEDS_EXPERT_REVIEW**: record unresolved legal, business or contextual questions; do not force a binary decision.

In reviewer_notes cite contract ID, page number, clause ID and an exact quotation. For omissions, identify the complete document reviewed and page range; do not manufacture a quote proving absence. Explain policy applicability (personal-data processing, deliverables, procurement context), protected party, conflicting terms and any missing schedules. Record reviewer_id and reviewed_at in ISO-8601 format. Evidence-page and source columns describe the original label; put proposed corrections in notes rather than overwrite original source facts. Obtain independent review/adjudication and an explicit versioned gold update later. No such approval or update is made here.

## Priority schedule

| Priority | Scope | Purpose |
|---|---|---|
| 1 | Three unmatched model findings; NDA durable G03 and supplier failure G02 personal-data applicability; all definite risk/missing severity labels | Resolve unsupported assumptions and potentially incorrect impact labels. High/medium alone is not proof of incorrect severity. |
| 2 | 55 potential missing-label rows; existing ambiguous labels and unconfirmed omissions | Establish applicability and complete-document absence; do not infer risk from silence. |
| 3 | Remaining structurally valid non-risk annotations | Confirm local compliance, schedule context and whole-contract interactions. |

Items can have overlapping concerns; the item priority is the highest applicable priority. Governing law is benchmark-only and must be reviewed separately from production capability. The category policy text below is the synthetic playbook, not an external legal standard.

## Policy reference

- **POL-LIAB-001**: Aggregate supplier liability must be at least the fees paid or payable in the preceding 12 months. Fraud, willful misconduct, confidentiality breaches, and data protection breaches must be excluded from the cap.
- **POL-INDEM-001**: The supplier must defend and indemnify the company against third-party intellectual property infringement claims arising from supplier deliverables. The company must not give an unlimited indemnity for supplier misconduct.
- **POL-TERM-001**: The company must be able to terminate for material breach after a cure period of no more than 30 days and terminate for convenience on no more than 30 days notice without a penalty.
- **POL-CONF-001**: Both parties must protect confidential information, restrict use to contract performance, and preserve confidentiality for at least three years after termination, with trade secrets protected while they remain trade secrets.
- **POL-PAY-001**: Undisputed invoices must be payable no earlier than 30 days after receipt. The company must be allowed to withhold disputed amounts in good faith and late charges must not exceed 1 percent per month.
- **POL-DATA-001**: The supplier must notify the company of a personal data breach within 48 hours of discovery, implement appropriate security measures, and delete or return company personal data within 30 days after termination.
- **POL-IP-001**: The company must own bespoke deliverables paid for under the agreement or receive a perpetual, irrevocable, worldwide license sufficient to use and modify them. Pre-existing supplier IP must be identified separately.
- **BENCH-LAW-001**: For this synthetic benchmark only, Company prefers England and Wales law with London courts; foreign exclusive law/forum requires negotiation review.

## Contract review

### SYN-supplier_red — Supplier equipment agreement

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/supplier_red.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/supplier_red.json) · [original gold](../backend/evaluation/fixtures/annotations/supplier_red.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Supplier equipment agreement
> 1. Supplier liability is limited to USD 50 in total, including fraud and data breaches.

**Page 2**

> SYNTHETIC CONTRACT - Supplier equipment agreement
> 2. Company shall indemnify Supplier for every claim, including claims caused by Supplier
> negligence. Supplier owes no IP defense.

**Page 3**

> SYNTHETIC CONTRACT - Supplier equipment agreement
> 3. Undisputed invoices are payable in 30 days after receipt. Company may withhold disputed
> sums in good faith. Late interest is 1 percent per month.

#### EXISTING GOLD LABEL — SYN-supplier_red-G01

**Worksheet row:** 1; **priority:** 1.

**Original label:** category liability; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-LIAB-001.

**Original explanation / why the clause may be risky:** A nominal cap with no carve-outs conflicts with the fee-based cap policy.

**Relevant clause — page 1, P001-C002:**

> 1. Supplier liability is limited to USD 50 in total, including fraud and data breaches.

**Original evidence quotation:**

> 1. Supplier liability is limited to USD 50 in total, including fraud and data breaches.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. 

**Question for reviewer:** Is this risk assessment justified under POL-LIAB-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the cap protect the intended party, meet the twelve-month fee floor and preserve fraud, misconduct, confidentiality and data carve-outs?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-supplier_red-G02

**Worksheet row:** 2; **priority:** 1.

**Original label:** category indemnification; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-INDEM-001.

**Original explanation / why the clause may be risky:** Allocates supplier misconduct to Company and omits supplier IP defense.

**Relevant clause — page 2, P002-C002:**

> 2. Company shall indemnify Supplier for every claim, including claims caused by Supplier
> negligence. Supplier owes no IP defense.

**Original evidence quotation:**

> 2. Company shall indemnify Supplier for every claim, including claims caused by Supplier
> negligence. Supplier owes no IP defense.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. 

**Question for reviewer:** Is this risk assessment justified under POL-INDEM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Who indemnifies whom, are supplier IP claims covered, and does the company assume unlimited supplier-misconduct exposure?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-supplier_red-G03

**Worksheet row:** 3; **priority:** 3.

**Original label:** category payment; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-PAY-001.

**Original explanation / why the clause may be risky:** Satisfies the stated invoice, dispute and interest assumptions.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 3, P003-C002:**

> 3. Undisputed invoices are payable in 30 days after receipt. Company may withhold disputed
> sums in good faith. Late interest is 1 percent per month.

**Original evidence quotation:**

> 3. Undisputed invoices are payable in 30 days after receipt. Company may withhold disputed
> sums in good faith. Late interest is 1 percent per month.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. 

**Question for reviewer:** Is this non_risk assessment justified under POL-PAY-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Can the company withhold disputed sums, are undisputed invoices due no earlier than thirty days, and are late charges at most one percent monthly?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-supplier_red-G04

**Worksheet row:** 4; **priority:** 1.

**Original label:** category termination; severity medium; state missing; risk_present True; confidence medium; reviewer status pending_manual_review; policy POL-TERM-001.

**Original explanation / why the clause may be risky:** No termination provision appears in this short synthetic agreement; absence requires full-document review.

**Relevant clause / evidence quotation:** none. This is an absence label, not a quoted provision. Review all 3 pages above; no positive quotation establishes absence.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Absence and its impact require complete-document review. 

**Question for reviewer:** Is this missing assessment justified under POL-TERM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are breach cure and company convenience notice within thirty days, and is there a penalty?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_red-confidentiality

**Worksheet row:** 5; **priority:** 2; **suggested category:** confidentiality; **coverage classification:** A; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** Absent confidentiality obligations are a clear review candidate under the mutual confidentiality playbook; not an approved risk label or confirmed absence. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does confidentiality apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_red-data_protection

**Worksheet row:** 6; **priority:** 2; **suggested category:** data_protection; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Personal-data processing is not established solely by silence. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does data_protection apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_red-intellectual_property

**Worksheet row:** 7; **priority:** 2; **suggested category:** intellectual_property; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Bespoke deliverables or an applicable licence interest must be established. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does intellectual_property apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_red-governing_law

**Worksheet row:** 8; **priority:** 2; **suggested category:** governing_law; **coverage classification:** D; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** Governing law is benchmark-only, outside production taxonomy; report separately. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does governing_law apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### MODEL-GENERATED FINDING — REVIEW-LIVE-SYN-supplier_red-LIVE-005

**Worksheet row:** 98; **priority:** 1; **prediction ID:** SYN-supplier_red-LIVE-005; **model:** gemini-3.5-flash; **existing run:** 1a9c514b-3b7b-4f60-839a-8d14558f60de.

**Generated category / severity:** confidentiality / medium; **policy:** POL-CONF-001.

**Generated explanation (not an established legal conclusion):** POTENTIAL OMISSION: The contract lacks confidentiality obligations. Full-document coverage and human review are required before confirming absence.

**Relevant clause / evidence quotation / page:** none supplied; alleged omission across the full synthetic document. Retained with evidence_status=needs_review; absence_confirmed=false; quote verification not applicable, not successful.

**Comparison with existing gold:** no annotation for this category; matching scored it as an unmatched prediction, not proof of hallucination.

**Reasons for and against adding a label:** Potentially valid unannotated omission; requires full-document human confirmation. No quotation, page or clause ID was provided. Correct policy category; retained missing finding is not evidence-verified absence.

**Question for reviewer:** Is this an applicable, genuinely absent protection after full-document review, or an unsupported/context-dependent premise? Decide independently of the model wording and medium severity.

**REVIEWER DECISION:**

#### MODEL-GENERATED FINDING — REVIEW-LIVE-SYN-supplier_red-LIVE-006

**Worksheet row:** 99; **priority:** 1; **prediction ID:** SYN-supplier_red-LIVE-006; **model:** gemini-3.5-flash; **existing run:** 1a9c514b-3b7b-4f60-839a-8d14558f60de.

**Generated category / severity:** data_protection / medium; **policy:** POL-DATA-001.

**Generated explanation (not an established legal conclusion):** POTENTIAL OMISSION: The contract does not contain data protection or breach notification obligations. Full-document coverage and human review are required before confirming absence.

**Relevant clause / evidence quotation / page:** none supplied; alleged omission across the full synthetic document. Retained with evidence_status=needs_review; absence_confirmed=false; quote verification not applicable, not successful.

**Comparison with existing gold:** no annotation for this category; matching scored it as an unmatched prediction, not proof of hallucination.

**Reasons for and against adding a label:** Ambiguous/context-dependent: personal-data applicability is not established by the source. No quotation, page or clause ID was provided. Correct policy category; retained missing finding is not evidence-verified absence.

**Question for reviewer:** Is this an applicable, genuinely absent protection after full-document review, or an unsupported/context-dependent premise? Decide independently of the model wording and medium severity.

**REVIEWER DECISION:**

#### MODEL-GENERATED FINDING — REVIEW-LIVE-SYN-supplier_red-LIVE-007

**Worksheet row:** 100; **priority:** 1; **prediction ID:** SYN-supplier_red-LIVE-007; **model:** gemini-3.5-flash; **existing run:** 1a9c514b-3b7b-4f60-839a-8d14558f60de.

**Generated category / severity:** intellectual_property / medium; **policy:** POL-IP-001.

**Generated explanation (not an established legal conclusion):** POTENTIAL OMISSION: The contract does not address intellectual property ownership or licensing of deliverables. Full-document coverage and human review are required before confirming absence.

**Relevant clause / evidence quotation / page:** none supplied; alleged omission across the full synthetic document. Retained with evidence_status=needs_review; absence_confirmed=false; quote verification not applicable, not successful.

**Comparison with existing gold:** no annotation for this category; matching scored it as an unmatched prediction, not proof of hallucination.

**Reasons for and against adding a label:** Ambiguous/context-dependent: bespoke-deliverable or licensing applicability is not established by the source. No quotation, page or clause ID was provided. Correct policy category; retained missing finding is not evidence-verified absence.

**Question for reviewer:** Is this an applicable, genuinely absent protection after full-document review, or an unsupported/context-dependent premise? Decide independently of the model wording and medium severity.

**REVIEWER DECISION:**

### SYN-supplier_green — Supplier maintenance agreement

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/supplier_green.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/supplier_green.json) · [original gold](../backend/evaluation/fixtures/annotations/supplier_green.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Supplier maintenance agreement
> 1. Liability is capped at fees paid or payable in the preceding 12 months. Fraud, willful
> misconduct, confidentiality and data protection breaches are excluded from the cap.

**Page 2**

> SYNTHETIC CONTRACT - Supplier maintenance agreement
> 2. Supplier will defend and indemnify Company against third-party IP infringement claims
> arising from supplied goods. Company gives no unlimited indemnity for Supplier misconduct.

**Page 3**

> SYNTHETIC CONTRACT - Supplier maintenance agreement
> 3. Company may terminate for convenience only with 120 days notice and payment of all
> remaining service fees.

**Page 4**

> SYNTHETIC CONTRACT - Supplier maintenance agreement
> 4. This agreement is governed by the laws of the fictional Republic of Norland, with disputes
> heard only in its capital.

#### EXISTING GOLD LABEL — SYN-supplier_green-G01

**Worksheet row:** 9; **priority:** 3.

**Original label:** category liability; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-LIAB-001.

**Original explanation / why the clause may be risky:** Satisfies the sample liability rule.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 1, P001-C002:**

> 1. Liability is capped at fees paid or payable in the preceding 12 months. Fraud, willful
> misconduct, confidentiality and data protection breaches are excluded from the cap.

**Original evidence quotation:**

> 1. Liability is capped at fees paid or payable in the preceding 12 months. Fraud, willful
> misconduct, confidentiality and data protection breaches are excluded from the cap.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. 

**Question for reviewer:** Is this non_risk assessment justified under POL-LIAB-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the cap protect the intended party, meet the twelve-month fee floor and preserve fraud, misconduct, confidentiality and data carve-outs?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-supplier_green-G02

**Worksheet row:** 10; **priority:** 3.

**Original label:** category indemnification; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-INDEM-001.

**Original explanation / why the clause may be risky:** Meets the supplier IP-defense expectation.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 2, P002-C002:**

> 2. Supplier will defend and indemnify Company against third-party IP infringement claims
> arising from supplied goods. Company gives no unlimited indemnity for Supplier misconduct.

**Original evidence quotation:**

> 2. Supplier will defend and indemnify Company against third-party IP infringement claims
> arising from supplied goods. Company gives no unlimited indemnity for Supplier misconduct.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. 

**Question for reviewer:** Is this non_risk assessment justified under POL-INDEM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Who indemnifies whom, are supplier IP claims covered, and does the company assume unlimited supplier-misconduct exposure?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-supplier_green-G03

**Worksheet row:** 11; **priority:** 1.

**Original label:** category termination; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-TERM-001.

**Original explanation / why the clause may be risky:** Notice and exit fee depart from the company rule.

**Relevant clause — page 3, P003-C002:**

> 3. Company may terminate for convenience only with 120 days notice and payment of all
> remaining service fees.

**Original evidence quotation:**

> 3. Company may terminate for convenience only with 120 days notice and payment of all
> remaining service fees.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. 

**Question for reviewer:** Is this risk assessment justified under POL-TERM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are breach cure and company convenience notice within thirty days, and is there a penalty?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-supplier_green-G04

**Worksheet row:** 12; **priority:** 1.

**Original label:** category governing_law; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy BENCH-LAW-001.

**Original explanation / why the clause may be risky:** Benchmark-only assumption prefers England and Wales; foreign venue needs review.

**Relevant clause — page 4, P004-C002:**

> 4. This agreement is governed by the laws of the fictional Republic of Norland, with disputes
> heard only in its capital.

**Original evidence quotation:**

> 4. This agreement is governed by the laws of the fictional Republic of Norland, with disputes
> heard only in its capital.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. This category and BENCH-LAW-001 are benchmark-only, unsupported by production taxonomy. 

**Question for reviewer:** Is this risk assessment justified under BENCH-LAW-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Against the benchmark-only preference, is the stated law/forum a definite deviation, compliant selection or unresolved agreement?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_green-payment

**Worksheet row:** 13; **priority:** 2; **suggested category:** payment; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does payment apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_green-confidentiality

**Worksheet row:** 14; **priority:** 2; **suggested category:** confidentiality; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does confidentiality apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_green-data_protection

**Worksheet row:** 15; **priority:** 2; **suggested category:** data_protection; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Personal-data processing is not established solely by silence. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does data_protection apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_green-intellectual_property

**Worksheet row:** 16; **priority:** 2; **suggested category:** intellectual_property; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Bespoke deliverables or an applicable licence interest must be established. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does intellectual_property apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-saas_red — SaaS analytics subscription

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/saas_red.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/saas_red.json) · [original gold](../backend/evaluation/fixtures/annotations/saas_red.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - SaaS analytics subscription
> 1. Provider must notify Company of a personal data breach within 9 days and delete retained
> data within 90 days after termination.

**Page 2**

> SYNTHETIC CONTRACT - SaaS analytics subscription
> 2. Provider owns all bespoke dashboards. Company receives a revocable license that ends
> when the subscription ends.

**Page 3**

> SYNTHETIC CONTRACT - SaaS analytics subscription
> 3. All invoices, including disputed sums, are due within 7 days. Late interest is 4 percent per
> month.

**Page 4**

> SYNTHETIC CONTRACT - SaaS analytics subscription
> 4. Provider protects Company information using reasonable efforts for an appropriate period.

#### EXISTING GOLD LABEL — SYN-saas_red-G01

**Worksheet row:** 17; **priority:** 1.

**Original label:** category data_protection; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-DATA-001.

**Original explanation / why the clause may be risky:** Exceeds the 48-hour notification and 30-day deletion limits.

**Relevant clause — page 1, P001-C002:**

> 1. Provider must notify Company of a personal data breach within 9 days and delete retained
> data within 90 days after termination.

**Original evidence quotation:**

> 1. Provider must notify Company of a personal data breach within 9 days and delete retained
> data within 90 days after termination.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Confidentiality ambiguity should be adjudicated against the explicit mutuality and survival requirements.

**Question for reviewer:** Is this risk assessment justified under POL-DATA-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the source establish personal-data processing? If applicable, are notification within forty-eight hours, security duties and deletion/return within thirty days explicit?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-saas_red-G02

**Worksheet row:** 18; **priority:** 1.

**Original label:** category intellectual_property; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-IP-001.

**Original explanation / why the clause may be risky:** Fails ownership or durable modification-license requirements.

**Relevant clause — page 2, P002-C002:**

> 2. Provider owns all bespoke dashboards. Company receives a revocable license that ends
> when the subscription ends.

**Original evidence quotation:**

> 2. Provider owns all bespoke dashboards. Company receives a revocable license that ends
> when the subscription ends.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Confidentiality ambiguity should be adjudicated against the explicit mutuality and survival requirements.

**Question for reviewer:** Is this risk assessment justified under POL-IP-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are bespoke deliverables or licensing interests established, and does ownership or a perpetual sufficient licence cover them? Are referenced pre-existing-IP schedules supplied?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-saas_red-G03

**Worksheet row:** 19; **priority:** 1.

**Original label:** category payment; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-PAY-001.

**Original explanation / why the clause may be risky:** Short payment term, disputed payment and excessive interest conflict with policy.

**Relevant clause — page 3, P003-C002:**

> 3. All invoices, including disputed sums, are due within 7 days. Late interest is 4 percent per
> month.

**Original evidence quotation:**

> 3. All invoices, including disputed sums, are due within 7 days. Late interest is 4 percent per
> month.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Confidentiality ambiguity should be adjudicated against the explicit mutuality and survival requirements.

**Question for reviewer:** Is this risk assessment justified under POL-PAY-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Can the company withhold disputed sums, are undisputed invoices due no earlier than thirty days, and are late charges at most one percent monthly?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-saas_red-G04

**Worksheet row:** 20; **priority:** 2.

**Original label:** category confidentiality; severity unspecified (ambiguous); state ambiguous; risk_present None; confidence medium; reviewer status pending_manual_review; policy POL-CONF-001.

**Original explanation / why the clause may be risky:** Duration and reciprocal scope are undefined; context is insufficient.

**Relevant clause — page 4, P004-C002:**

> 4. Provider protects Company information using reasonable efforts for an appropriate period.

**Original evidence quotation:**

> 4. Provider protects Company information using reasonable efforts for an appropriate period.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. The gold label intentionally leaves risk/severity unresolved. Confidentiality ambiguity should be adjudicated against the explicit mutuality and survival requirements.

**Question for reviewer:** Is this ambiguous assessment justified under POL-CONF-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are obligations mutual and purpose-limited, do they survive at least three years, and are trade secrets protected? Does an overriding provision defeat them?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-saas_red-liability

**Worksheet row:** 21; **priority:** 2; **suggested category:** liability; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does liability apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-saas_red-indemnification

**Worksheet row:** 22; **priority:** 2; **suggested category:** indemnification; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does indemnification apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-saas_red-termination

**Worksheet row:** 23; **priority:** 2; **suggested category:** termination; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does termination apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-saas_red-governing_law

**Worksheet row:** 24; **priority:** 2; **suggested category:** governing_law; **coverage classification:** D; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** Governing law is benchmark-only, outside production taxonomy; report separately. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does governing_law apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-saas_green — SaaS records subscription

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/saas_green.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/saas_green.json) · [original gold](../backend/evaluation/fixtures/annotations/saas_green.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - SaaS records subscription
> 1. Provider applies access controls and encryption, notifies Company of a breach within 48
> hours of discovery, and returns or deletes data within 30 days of termination.

**Page 2**

> SYNTHETIC CONTRACT - SaaS records subscription
> 2. Company owns bespoke deliverables. Provider retains only pre-existing modules listed in
> Schedule A.

**Page 3**

> SYNTHETIC CONTRACT - SaaS records subscription
> 3. Company pays undisputed invoices in 45 days after receipt and may withhold disputed
> sums in good faith. Late interest is 0.5 percent monthly.

**Page 4**

> SYNTHETIC CONTRACT - SaaS records subscription
> 4. The law of England and Wales governs this agreement; courts in London hear disputes.

#### EXISTING GOLD LABEL — SYN-saas_green-G01

**Worksheet row:** 25; **priority:** 3.

**Original label:** category data_protection; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-DATA-001.

**Original explanation / why the clause may be risky:** Meets the illustrative notification, security and deletion rule.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 1, P001-C002:**

> 1. Provider applies access controls and encryption, notifies Company of a breach within 48
> hours of discovery, and returns or deletes data within 30 days of termination.

**Original evidence quotation:**

> 1. Provider applies access controls and encryption, notifies Company of a breach within 48
> hours of discovery, and returns or deletes data within 30 days of termination.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. IP clause references Schedule A, which is not included; ownership language exists but schedule completeness is unverified.

**Question for reviewer:** Is this non_risk assessment justified under POL-DATA-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the source establish personal-data processing? If applicable, are notification within forty-eight hours, security duties and deletion/return within thirty days explicit?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-saas_green-G02

**Worksheet row:** 26; **priority:** 3.

**Original label:** category intellectual_property; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-IP-001.

**Original explanation / why the clause may be risky:** Provides bespoke ownership and identifies retained pre-existing material.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 2, P002-C002:**

> 2. Company owns bespoke deliverables. Provider retains only pre-existing modules listed in
> Schedule A.

**Original evidence quotation:**

> 2. Company owns bespoke deliverables. Provider retains only pre-existing modules listed in
> Schedule A.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. IP clause references Schedule A, which is not included; ownership language exists but schedule completeness is unverified.

**Question for reviewer:** Is this non_risk assessment justified under POL-IP-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are bespoke deliverables or licensing interests established, and does ownership or a perpetual sufficient licence cover them? Are referenced pre-existing-IP schedules supplied?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-saas_green-G03

**Worksheet row:** 27; **priority:** 3.

**Original label:** category payment; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-PAY-001.

**Original explanation / why the clause may be risky:** Within the company payment rule.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 3, P003-C002:**

> 3. Company pays undisputed invoices in 45 days after receipt and may withhold disputed
> sums in good faith. Late interest is 0.5 percent monthly.

**Original evidence quotation:**

> 3. Company pays undisputed invoices in 45 days after receipt and may withhold disputed
> sums in good faith. Late interest is 0.5 percent monthly.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. IP clause references Schedule A, which is not included; ownership language exists but schedule completeness is unverified.

**Question for reviewer:** Is this non_risk assessment justified under POL-PAY-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Can the company withhold disputed sums, are undisputed invoices due no earlier than thirty days, and are late charges at most one percent monthly?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-saas_green-G04

**Worksheet row:** 28; **priority:** 3.

**Original label:** category governing_law; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy BENCH-LAW-001.

**Original explanation / why the clause may be risky:** Meets benchmark-only illustrative jurisdiction assumption.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 4, P004-C002:**

> 4. The law of England and Wales governs this agreement; courts in London hear disputes.

**Original evidence quotation:**

> 4. The law of England and Wales governs this agreement; courts in London hear disputes.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. This category and BENCH-LAW-001 are benchmark-only, unsupported by production taxonomy. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. IP clause references Schedule A, which is not included; ownership language exists but schedule completeness is unverified.

**Question for reviewer:** Is this non_risk assessment justified under BENCH-LAW-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Against the benchmark-only preference, is the stated law/forum a definite deviation, compliant selection or unresolved agreement?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-saas_green-liability

**Worksheet row:** 29; **priority:** 2; **suggested category:** liability; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does liability apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-saas_green-indemnification

**Worksheet row:** 30; **priority:** 2; **suggested category:** indemnification; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does indemnification apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-saas_green-termination

**Worksheet row:** 31; **priority:** 2; **suggested category:** termination; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does termination apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-saas_green-confidentiality

**Worksheet row:** 32; **priority:** 2; **suggested category:** confidentiality; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does confidentiality apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-nda_short — Mutual prototype NDA

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/nda_short.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/nda_short.json) · [original gold](../backend/evaluation/fixtures/annotations/nda_short.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Mutual prototype NDA
> 1. Each party shall use confidential information only for the project. All confidentiality duties
> end 6 months after disclosure, including trade secrets.

**Page 2**

> SYNTHETIC CONTRACT - Mutual prototype NDA
> 2. Liability for disclosure of confidential information is capped at USD 10.

**Page 3**

> SYNTHETIC CONTRACT - Mutual prototype NDA
> 3. Ownership of ideas shared in workshops will be agreed later by the parties.

#### EXISTING GOLD LABEL — SYN-nda_short-G01

**Worksheet row:** 33; **priority:** 1.

**Original label:** category confidentiality; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-CONF-001.

**Original explanation / why the clause may be risky:** Mutual use restriction does not cure deficient survival.

**Relevant clause — page 1, P001-C002:**

> 1. Each party shall use confidential information only for the project. All confidentiality duties
> end 6 months after disclosure, including trade secrets.

**Original evidence quotation:**

> 1. Each party shall use confidential information only for the project. All confidentiality duties
> end 6 months after disclosure, including trade secrets.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. 

**Question for reviewer:** Is this risk assessment justified under POL-CONF-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are obligations mutual and purpose-limited, do they survive at least three years, and are trade secrets protected? Does an overriding provision defeat them?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-nda_short-G02

**Worksheet row:** 34; **priority:** 1.

**Original label:** category liability; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-LIAB-001.

**Original explanation / why the clause may be risky:** Nominal confidentiality cap conflicts with the exception requirement.

**Relevant clause — page 2, P002-C002:**

> 2. Liability for disclosure of confidential information is capped at USD 10.

**Original evidence quotation:**

> 2. Liability for disclosure of confidential information is capped at USD 10.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. 

**Question for reviewer:** Is this risk assessment justified under POL-LIAB-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the cap protect the intended party, meet the twelve-month fee floor and preserve fraud, misconduct, confidentiality and data carve-outs?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-nda_short-G03

**Worksheet row:** 35; **priority:** 2.

**Original label:** category intellectual_property; severity unspecified (ambiguous); state ambiguous; risk_present None; confidence medium; reviewer status pending_manual_review; policy POL-IP-001.

**Original explanation / why the clause may be risky:** No present allocation; NDA context may differ from bespoke work policy.

**Relevant clause — page 3, P003-C002:**

> 3. Ownership of ideas shared in workshops will be agreed later by the parties.

**Original evidence quotation:**

> 3. Ownership of ideas shared in workshops will be agreed later by the parties.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. The gold label intentionally leaves risk/severity unresolved. 

**Question for reviewer:** Is this ambiguous assessment justified under POL-IP-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are bespoke deliverables or licensing interests established, and does ownership or a perpetual sufficient licence cover them? Are referenced pre-existing-IP schedules supplied?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_short-indemnification

**Worksheet row:** 36; **priority:** 2; **suggested category:** indemnification; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does indemnification apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_short-termination

**Worksheet row:** 37; **priority:** 2; **suggested category:** termination; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does termination apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_short-payment

**Worksheet row:** 38; **priority:** 2; **suggested category:** payment; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does payment apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_short-data_protection

**Worksheet row:** 39; **priority:** 2; **suggested category:** data_protection; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Personal-data processing is not established solely by silence. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does data_protection apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_short-governing_law

**Worksheet row:** 40; **priority:** 2; **suggested category:** governing_law; **coverage classification:** D; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** Governing law is benchmark-only, outside production taxonomy; report separately. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does governing_law apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-nda_durable — Mutual research NDA

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/nda_durable.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/nda_durable.json) · [original gold](../backend/evaluation/fixtures/annotations/nda_durable.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Mutual research NDA
> 1. Both parties use disclosed information only for this research. Duties survive for 4 years
> after termination and trade secrets remain protected while secret.

**Page 2**

> SYNTHETIC CONTRACT - Mutual research NDA
> 2. Despite the preceding clause, Recipient may publish any confidential report after 10 days
> without consent.

#### EXISTING GOLD LABEL — SYN-nda_durable-G01

**Worksheet row:** 41; **priority:** 3.

**Original label:** category confidentiality; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-CONF-001.

**Original explanation / why the clause may be risky:** Meets mutual purpose and survival assumptions.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 1, P001-C002:**

> 1. Both parties use disclosed information only for this research. Duties survive for 4 years
> after termination and trade secrets remain protected while secret.

**Original evidence quotation:**

> 1. Both parties use disclosed information only for this research. Duties survive for 4 years
> after termination and trade secrets remain protected while secret.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. G03 assumes personal-data research although the PDF does not state personal-data processing. G01 is a local non-risk provision overridden by G02; do not infer whole-contract compliance.

**Question for reviewer:** Is this non_risk assessment justified under POL-CONF-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are obligations mutual and purpose-limited, do they survive at least three years, and are trade secrets protected? Does an overriding provision defeat them?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-nda_durable-G02

**Worksheet row:** 42; **priority:** 1.

**Original label:** category confidentiality; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-CONF-001.

**Original explanation / why the clause may be risky:** Separate publication override undermines the otherwise protective duty.

**Relevant clause — page 2, P002-C002:**

> 2. Despite the preceding clause, Recipient may publish any confidential report after 10 days
> without consent.

**Original evidence quotation:**

> 2. Despite the preceding clause, Recipient may publish any confidential report after 10 days
> without consent.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. G03 assumes personal-data research although the PDF does not state personal-data processing. G01 is a local non-risk provision overridden by G02; do not infer whole-contract compliance.

**Question for reviewer:** Is this risk assessment justified under POL-CONF-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are obligations mutual and purpose-limited, do they survive at least three years, and are trade secrets protected? Does an overriding provision defeat them?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-nda_durable-G03

**Worksheet row:** 43; **priority:** 1.

**Original label:** category data_protection; severity medium; state missing; risk_present True; confidence medium; reviewer status pending_manual_review; policy POL-DATA-001.

**Original explanation / why the clause may be risky:** Synthetic research involves personal data but includes no breach-notification requirement.

**Relevant clause / evidence quotation:** none. This is an absence label, not a quoted provision. Review all 2 pages above; no positive quotation establishes absence.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Absence and its impact require complete-document review. G03 assumes personal-data research although the PDF does not state personal-data processing. G01 is a local non-risk provision overridden by G02; do not infer whole-contract compliance.

**Question for reviewer:** Is this missing assessment justified under POL-DATA-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the source establish personal-data processing? If applicable, are notification within forty-eight hours, security duties and deletion/return within thirty days explicit?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_durable-liability

**Worksheet row:** 44; **priority:** 2; **suggested category:** liability; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does liability apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_durable-indemnification

**Worksheet row:** 45; **priority:** 2; **suggested category:** indemnification; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does indemnification apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_durable-termination

**Worksheet row:** 46; **priority:** 2; **suggested category:** termination; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does termination apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_durable-payment

**Worksheet row:** 47; **priority:** 2; **suggested category:** payment; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does payment apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_durable-intellectual_property

**Worksheet row:** 48; **priority:** 2; **suggested category:** intellectual_property; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Bespoke deliverables or an applicable licence interest must be established. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does intellectual_property apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-nda_durable-governing_law

**Worksheet row:** 49; **priority:** 2; **suggested category:** governing_law; **coverage classification:** D; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** Governing law is benchmark-only, outside production taxonomy; report separately. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does governing_law apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-services_exit — Facilities services agreement

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/services_exit.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/services_exit.json) · [original gold](../backend/evaluation/fixtures/annotations/services_exit.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Facilities services agreement
> 1. Supplier may terminate immediately for any Company breach, without a cure period.
> Company has no convenience termination right.

**Page 2**

> SYNTHETIC CONTRACT - Facilities services agreement
> 2. Company shall defend Supplier from claims caused solely by Supplier misconduct, without
> a financial limit.

**Page 3**

> SYNTHETIC CONTRACT - Facilities services agreement
> 3. Company owes undisputed invoices in 30 days after receipt, may withhold disputed sums
> in good faith, and owes no late interest.

#### EXISTING GOLD LABEL — SYN-services_exit-G01

**Worksheet row:** 50; **priority:** 1.

**Original label:** category termination; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-TERM-001.

**Original explanation / why the clause may be risky:** No cure or company exit protection.

**Relevant clause — page 1, P001-C002:**

> 1. Supplier may terminate immediately for any Company breach, without a cure period.
> Company has no convenience termination right.

**Original evidence quotation:**

> 1. Supplier may terminate immediately for any Company breach, without a cure period.
> Company has no convenience termination right.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. 

**Question for reviewer:** Is this risk assessment justified under POL-TERM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are breach cure and company convenience notice within thirty days, and is there a penalty?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-services_exit-G02

**Worksheet row:** 51; **priority:** 1.

**Original label:** category indemnification; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-INDEM-001.

**Original explanation / why the clause may be risky:** Explicitly unlimited protection for supplier misconduct.

**Relevant clause — page 2, P002-C002:**

> 2. Company shall defend Supplier from claims caused solely by Supplier misconduct, without
> a financial limit.

**Original evidence quotation:**

> 2. Company shall defend Supplier from claims caused solely by Supplier misconduct, without
> a financial limit.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. 

**Question for reviewer:** Is this risk assessment justified under POL-INDEM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Who indemnifies whom, are supplier IP claims covered, and does the company assume unlimited supplier-misconduct exposure?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-services_exit-G03

**Worksheet row:** 52; **priority:** 3.

**Original label:** category payment; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-PAY-001.

**Original explanation / why the clause may be risky:** Matches payment assumptions.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 3, P003-C002:**

> 3. Company owes undisputed invoices in 30 days after receipt, may withhold disputed sums
> in good faith, and owes no late interest.

**Original evidence quotation:**

> 3. Company owes undisputed invoices in 30 days after receipt, may withhold disputed sums
> in good faith, and owes no late interest.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. 

**Question for reviewer:** Is this non_risk assessment justified under POL-PAY-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Can the company withhold disputed sums, are undisputed invoices due no earlier than thirty days, and are late charges at most one percent monthly?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_exit-liability

**Worksheet row:** 53; **priority:** 2; **suggested category:** liability; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does liability apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_exit-confidentiality

**Worksheet row:** 54; **priority:** 2; **suggested category:** confidentiality; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does confidentiality apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_exit-data_protection

**Worksheet row:** 55; **priority:** 2; **suggested category:** data_protection; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Personal-data processing is not established solely by silence. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does data_protection apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_exit-intellectual_property

**Worksheet row:** 56; **priority:** 2; **suggested category:** intellectual_property; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Bespoke deliverables or an applicable licence interest must be established. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does intellectual_property apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_exit-governing_law

**Worksheet row:** 57; **priority:** 2; **suggested category:** governing_law; **coverage classification:** D; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** Governing law is benchmark-only, outside production taxonomy; report separately. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does governing_law apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-services_balanced — Technical support services

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/services_balanced.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/services_balanced.json) · [original gold](../backend/evaluation/fixtures/annotations/services_balanced.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Technical support services
> 1. Either party may terminate for material breach after a 20-day cure period. Company may
> terminate for convenience on 30 days notice without penalty.

**Page 2**

> SYNTHETIC CONTRACT - Technical support services
> 2. Supplier defends and indemnifies Company for third-party IP claims. Company does not
> indemnify Supplier for Supplier misconduct.

**Page 3**

> SYNTHETIC CONTRACT - Technical support services
> 3. Applicable law and forum will be selected by mutual agreement following a dispute.

#### EXISTING GOLD LABEL — SYN-services_balanced-G01

**Worksheet row:** 58; **priority:** 3.

**Original label:** category termination; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-TERM-001.

**Original explanation / why the clause may be risky:** Meets cure and exit limits.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 1, P001-C002:**

> 1. Either party may terminate for material breach after a 20-day cure period. Company may
> terminate for convenience on 30 days notice without penalty.

**Original evidence quotation:**

> 1. Either party may terminate for material breach after a 20-day cure period. Company may
> terminate for convenience on 30 days notice without penalty.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. Missing liability allocation requires protected-party and default allocation review; absence is not automatically adverse.

**Question for reviewer:** Is this non_risk assessment justified under POL-TERM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are breach cure and company convenience notice within thirty days, and is there a penalty?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-services_balanced-G02

**Worksheet row:** 59; **priority:** 3.

**Original label:** category indemnification; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-INDEM-001.

**Original explanation / why the clause may be risky:** Opposite allocation from the superficially similar risky indemnity.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 2, P002-C002:**

> 2. Supplier defends and indemnifies Company for third-party IP claims. Company does not
> indemnify Supplier for Supplier misconduct.

**Original evidence quotation:**

> 2. Supplier defends and indemnifies Company for third-party IP claims. Company does not
> indemnify Supplier for Supplier misconduct.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. Missing liability allocation requires protected-party and default allocation review; absence is not automatically adverse.

**Question for reviewer:** Is this non_risk assessment justified under POL-INDEM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Who indemnifies whom, are supplier IP claims covered, and does the company assume unlimited supplier-misconduct exposure?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-services_balanced-G03

**Worksheet row:** 60; **priority:** 2.

**Original label:** category governing_law; severity unspecified (ambiguous); state ambiguous; risk_present None; confidence medium; reviewer status pending_manual_review; policy BENCH-LAW-001.

**Original explanation / why the clause may be risky:** Jurisdiction remains undecided.

**Relevant clause — page 3, P003-C002:**

> 3. Applicable law and forum will be selected by mutual agreement following a dispute.

**Original evidence quotation:**

> 3. Applicable law and forum will be selected by mutual agreement following a dispute.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. This category and BENCH-LAW-001 are benchmark-only, unsupported by production taxonomy. The gold label intentionally leaves risk/severity unresolved. Missing liability allocation requires protected-party and default allocation review; absence is not automatically adverse.

**Question for reviewer:** Is this ambiguous assessment justified under BENCH-LAW-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Against the benchmark-only preference, is the stated law/forum a definite deviation, compliant selection or unresolved agreement?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-services_balanced-G04

**Worksheet row:** 61; **priority:** 1.

**Original label:** category liability; severity medium; state missing; risk_present True; confidence medium; reviewer status pending_manual_review; policy POL-LIAB-001.

**Original explanation / why the clause may be risky:** No fee-based liability allocation is included in this synthetic services contract.

**Relevant clause / evidence quotation:** none. This is an absence label, not a quoted provision. Review all 3 pages above; no positive quotation establishes absence.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Absence and its impact require complete-document review. Missing liability allocation requires protected-party and default allocation review; absence is not automatically adverse.

**Question for reviewer:** Is this missing assessment justified under POL-LIAB-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the cap protect the intended party, meet the twelve-month fee floor and preserve fraud, misconduct, confidentiality and data carve-outs?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_balanced-payment

**Worksheet row:** 62; **priority:** 2; **suggested category:** payment; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does payment apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_balanced-confidentiality

**Worksheet row:** 63; **priority:** 2; **suggested category:** confidentiality; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does confidentiality apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_balanced-data_protection

**Worksheet row:** 64; **priority:** 2; **suggested category:** data_protection; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Personal-data processing is not established solely by silence. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does data_protection apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_balanced-intellectual_property

**Worksheet row:** 65; **priority:** 2; **suggested category:** intellectual_property; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Bespoke deliverables or an applicable licence interest must be established. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does intellectual_property apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-consulting_owned — Design consulting engagement

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/consulting_owned.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/consulting_owned.json) · [original gold](../backend/evaluation/fixtures/annotations/consulting_owned.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Design consulting engagement
> 1. Company owns all custom designs upon creation. Consultant retains the pre-existing toolkit
> named in Schedule B.

**Page 2**

> SYNTHETIC CONTRACT - Design consulting engagement
> 2. Consultant may use Company confidential information for any client and owes no
> confidentiality duty after completion.

**Page 3**

> SYNTHETIC CONTRACT - Design consulting engagement
> 3. Company shall pay even disputed invoices in 5 days with late interest of 2 percent per
> month.

#### EXISTING GOLD LABEL — SYN-consulting_owned-G01

**Worksheet row:** 66; **priority:** 3.

**Original label:** category intellectual_property; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-IP-001.

**Original explanation / why the clause may be risky:** Bespoke ownership is explicit.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 1, P001-C002:**

> 1. Company owns all custom designs upon creation. Consultant retains the pre-existing toolkit
> named in Schedule B.

**Original evidence quotation:**

> 1. Company owns all custom designs upon creation. Consultant retains the pre-existing toolkit
> named in Schedule B.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. IP clause references Schedule B, which is not included; pre-existing toolkit boundaries need review.

**Question for reviewer:** Is this non_risk assessment justified under POL-IP-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are bespoke deliverables or licensing interests established, and does ownership or a perpetual sufficient licence cover them? Are referenced pre-existing-IP schedules supplied?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-consulting_owned-G02

**Worksheet row:** 67; **priority:** 1.

**Original label:** category confidentiality; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-CONF-001.

**Original explanation / why the clause may be risky:** Purpose and survival protections are absent.

**Relevant clause — page 2, P002-C002:**

> 2. Consultant may use Company confidential information for any client and owes no
> confidentiality duty after completion.

**Original evidence quotation:**

> 2. Consultant may use Company confidential information for any client and owes no
> confidentiality duty after completion.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. IP clause references Schedule B, which is not included; pre-existing toolkit boundaries need review.

**Question for reviewer:** Is this risk assessment justified under POL-CONF-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are obligations mutual and purpose-limited, do they survive at least three years, and are trade secrets protected? Does an overriding provision defeat them?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-consulting_owned-G03

**Worksheet row:** 68; **priority:** 1.

**Original label:** category payment; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-PAY-001.

**Original explanation / why the clause may be risky:** Departs from all three payment expectations.

**Relevant clause — page 3, P003-C002:**

> 3. Company shall pay even disputed invoices in 5 days with late interest of 2 percent per
> month.

**Original evidence quotation:**

> 3. Company shall pay even disputed invoices in 5 days with late interest of 2 percent per
> month.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. IP clause references Schedule B, which is not included; pre-existing toolkit boundaries need review.

**Question for reviewer:** Is this risk assessment justified under POL-PAY-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Can the company withhold disputed sums, are undisputed invoices due no earlier than thirty days, and are late charges at most one percent monthly?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_owned-liability

**Worksheet row:** 69; **priority:** 2; **suggested category:** liability; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does liability apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_owned-indemnification

**Worksheet row:** 70; **priority:** 2; **suggested category:** indemnification; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does indemnification apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_owned-termination

**Worksheet row:** 71; **priority:** 2; **suggested category:** termination; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does termination apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_owned-data_protection

**Worksheet row:** 72; **priority:** 2; **suggested category:** data_protection; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Personal-data processing is not established solely by silence. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does data_protection apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_owned-governing_law

**Worksheet row:** 73; **priority:** 2; **suggested category:** governing_law; **coverage classification:** D; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** Governing law is benchmark-only, outside production taxonomy; report separately. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does governing_law apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-consulting_retained — Engineering consulting engagement

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/consulting_retained.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/consulting_retained.json) · [original gold](../backend/evaluation/fixtures/annotations/consulting_retained.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Engineering consulting engagement
> 1. Consultant retains custom designs and grants Company a temporary, non-transferable
> license with no right to modify.

**Page 2**

> SYNTHETIC CONTRACT - Engineering consulting engagement
> 2. Both parties use information only for the engagement, preserve secrecy for 3 years after
> termination, and protect trade secrets while secret.

**Page 3**

> SYNTHETIC CONTRACT - Engineering consulting engagement
> 3. Company may end the engagement on reasonable notice subject to fair compensation.

#### EXISTING GOLD LABEL — SYN-consulting_retained-G01

**Worksheet row:** 74; **priority:** 1.

**Original label:** category intellectual_property; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-IP-001.

**Original explanation / why the clause may be risky:** Neither ownership nor qualifying perpetual modification license.

**Relevant clause — page 1, P001-C002:**

> 1. Consultant retains custom designs and grants Company a temporary, non-transferable
> license with no right to modify.

**Original evidence quotation:**

> 1. Consultant retains custom designs and grants Company a temporary, non-transferable
> license with no right to modify.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. 

**Question for reviewer:** Is this risk assessment justified under POL-IP-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are bespoke deliverables or licensing interests established, and does ownership or a perpetual sufficient licence cover them? Are referenced pre-existing-IP schedules supplied?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-consulting_retained-G02

**Worksheet row:** 75; **priority:** 3.

**Original label:** category confidentiality; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-CONF-001.

**Original explanation / why the clause may be risky:** Meets the company confidentiality rule.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 2, P002-C002:**

> 2. Both parties use information only for the engagement, preserve secrecy for 3 years after
> termination, and protect trade secrets while secret.

**Original evidence quotation:**

> 2. Both parties use information only for the engagement, preserve secrecy for 3 years after
> termination, and protect trade secrets while secret.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. 

**Question for reviewer:** Is this non_risk assessment justified under POL-CONF-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are obligations mutual and purpose-limited, do they survive at least three years, and are trade secrets protected? Does an overriding provision defeat them?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-consulting_retained-G03

**Worksheet row:** 76; **priority:** 2.

**Original label:** category termination; severity unspecified (ambiguous); state ambiguous; risk_present None; confidence medium; reviewer status pending_manual_review; policy POL-TERM-001.

**Original explanation / why the clause may be risky:** Notice duration and whether compensation is a penalty are unclear.

**Relevant clause — page 3, P003-C002:**

> 3. Company may end the engagement on reasonable notice subject to fair compensation.

**Original evidence quotation:**

> 3. Company may end the engagement on reasonable notice subject to fair compensation.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. The gold label intentionally leaves risk/severity unresolved. 

**Question for reviewer:** Is this ambiguous assessment justified under POL-TERM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are breach cure and company convenience notice within thirty days, and is there a penalty?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_retained-liability

**Worksheet row:** 77; **priority:** 2; **suggested category:** liability; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does liability apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_retained-indemnification

**Worksheet row:** 78; **priority:** 2; **suggested category:** indemnification; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does indemnification apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_retained-payment

**Worksheet row:** 79; **priority:** 2; **suggested category:** payment; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does payment apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_retained-data_protection

**Worksheet row:** 80; **priority:** 2; **suggested category:** data_protection; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Personal-data processing is not established solely by silence. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does data_protection apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-consulting_retained-governing_law

**Worksheet row:** 81; **priority:** 2; **suggested category:** governing_law; **coverage classification:** D; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** Governing law is benchmark-only, outside production taxonomy; report separately. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does governing_law apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-services_split — Page-spanning hosting services

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/services_split.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/services_split.json) · [original gold](../backend/evaluation/fixtures/annotations/services_split.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Page-spanning hosting services
> 1. Provider shall notify Company of a personal data breach

**Page 2**

> SYNTHETIC CONTRACT - Page-spanning hosting services
> within 8 days and delete personal data within 60 days after exit.

**Page 3**

> SYNTHETIC CONTRACT - Page-spanning hosting services
> 2. The cap is fees paid or payable in the preceding 12 months; fraud, willful misconduct,
> confidentiality and data protection breaches are uncapped.

**Page 4**

> SYNTHETIC CONTRACT - Page-spanning hosting services
> 3. Disputed invoices are payable within 10 days; interest accrues at 3 percent monthly.

#### EXISTING GOLD LABEL — SYN-services_split-G01

**Worksheet row:** 82; **priority:** 1.

**Original label:** category data_protection; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-DATA-001.

**Original explanation / why the clause may be risky:** One legal clause spans two pages; the second fragment contains the risky deadlines.

**Relevant clause — page 1, P001-C002:**

> 1. Provider shall notify Company of a personal data breach

**Original evidence quotation:**

> 1. Provider shall notify Company of a personal data breach

**Relevant clause — page 2, P002-C001:**

> SYNTHETIC CONTRACT - Page-spanning hosting services
> within 8 days and delete personal data within 60 days after exit.

**Original evidence quotation:**

> SYNTHETIC CONTRACT - Page-spanning hosting services
> within 8 days and delete personal data within 60 days after exit.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Data protection has two source spans across pages 1 and 2; primary span alone does not contain the risky deadline. Review both spans.

**Question for reviewer:** Is this risk assessment justified under POL-DATA-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the source establish personal-data processing? If applicable, are notification within forty-eight hours, security duties and deletion/return within thirty days explicit?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-services_split-G02

**Worksheet row:** 83; **priority:** 3.

**Original label:** category liability; severity low; state non_risk; risk_present False; confidence high; reviewer status pending_manual_review; policy POL-LIAB-001.

**Original explanation / why the clause may be risky:** Meets the sample cap and exclusions.

This gold label asserts local non-risk/compliance, not a risky finding. Confirm the explanation against the complete policy and surrounding terms.

**Relevant clause — page 3, P003-C002:**

> 2. The cap is fees paid or payable in the preceding 12 months; fraud, willful misconduct,
> confidentiality and data protection breaches are uncapped.

**Original evidence quotation:**

> 2. The cap is fees paid or payable in the preceding 12 months; fraud, willful misconduct,
> confidentiality and data protection breaches are uncapped.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Low here accompanies a non-risk label; confirm that this does not imply a positive low-risk finding. Data protection has two source spans across pages 1 and 2; primary span alone does not contain the risky deadline. Review both spans.

**Question for reviewer:** Is this non_risk assessment justified under POL-LIAB-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the cap protect the intended party, meet the twelve-month fee floor and preserve fraud, misconduct, confidentiality and data carve-outs?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-services_split-G03

**Worksheet row:** 84; **priority:** 1.

**Original label:** category payment; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-PAY-001.

**Original explanation / why the clause may be risky:** Dispute handling and terms conflict with policy.

**Relevant clause — page 4, P004-C002:**

> 3. Disputed invoices are payable within 10 days; interest accrues at 3 percent monthly.

**Original evidence quotation:**

> 3. Disputed invoices are payable within 10 days; interest accrues at 3 percent monthly.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Data protection has two source spans across pages 1 and 2; primary span alone does not contain the risky deadline. Review both spans.

**Question for reviewer:** Is this risk assessment justified under POL-PAY-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Can the company withhold disputed sums, are undisputed invoices due no earlier than thirty days, and are late charges at most one percent monthly?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_split-indemnification

**Worksheet row:** 85; **priority:** 2; **suggested category:** indemnification; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does indemnification apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_split-termination

**Worksheet row:** 86; **priority:** 2; **suggested category:** termination; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does termination apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_split-confidentiality

**Worksheet row:** 87; **priority:** 2; **suggested category:** confidentiality; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does confidentiality apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_split-intellectual_property

**Worksheet row:** 88; **priority:** 2; **suggested category:** intellectual_property; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Bespoke deliverables or an applicable licence interest must be established. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does intellectual_property apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-services_split-governing_law

**Worksheet row:** 89; **priority:** 2; **suggested category:** governing_law; **coverage classification:** D; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** Governing law is benchmark-only, outside production taxonomy; report separately. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does governing_law apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

### SYN-supplier_failure — Synthetic logistics agreement

**Source:** [synthetic PDF](../backend/evaluation/fixtures/contracts/supplier_failure.pdf) · [canonical extracted text](../backend/evaluation/fixtures/contracts/supplier_failure.json) · [original gold](../backend/evaluation/fixtures/annotations/supplier_failure.json)

#### Original extracted contract text

The following page text is copied verbatim from the validated canonical extraction. It supplies context for every coverage/absence candidate; synthetic headers are retained.

**Page 1**

> SYNTHETIC CONTRACT - Synthetic logistics agreement
> 1. Carrier liability, including fraud and data incidents, is capped at USD 25.

**Page 2**

> SYNTHETIC CONTRACT - Synthetic logistics agreement
> 2. Carrier will notify Company of a data breach within 12 days.

**Page 3**

> SYNTHETIC CONTRACT - Synthetic logistics agreement
> 3. Company must give 100 days notice and pay a termination penalty of USD 5000.

**Page 4**

> SYNTHETIC CONTRACT - Synthetic logistics agreement
> 4. The laws and exclusive courts of the fictional Kingdom of Eridia govern.

#### EXISTING GOLD LABEL — SYN-supplier_failure-G01

**Worksheet row:** 90; **priority:** 1.

**Original label:** category liability; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-LIAB-001.

**Original explanation / why the clause may be risky:** Nominal inclusive cap violates the illustrative liability rule.

**Relevant clause — page 1, P001-C002:**

> 1. Carrier liability, including fraud and data incidents, is capped at USD 25.

**Original evidence quotation:**

> 1. Carrier liability, including fraud and data incidents, is capped at USD 25.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Data-breach language does not explicitly establish personal-data processing; review policy applicability.

**Question for reviewer:** Is this risk assessment justified under POL-LIAB-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the cap protect the intended party, meet the twelve-month fee floor and preserve fraud, misconduct, confidentiality and data carve-outs?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-supplier_failure-G02

**Worksheet row:** 91; **priority:** 1.

**Original label:** category data_protection; severity high; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-DATA-001.

**Original explanation / why the clause may be risky:** Notification exceeds 48 hours.

**Relevant clause — page 2, P002-C002:**

> 2. Carrier will notify Company of a data breach within 12 days.

**Original evidence quotation:**

> 2. Carrier will notify Company of a data breach within 12 days.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Data-breach language does not explicitly establish personal-data processing; review policy applicability.

**Question for reviewer:** Is this risk assessment justified under POL-DATA-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Does the source establish personal-data processing? If applicable, are notification within forty-eight hours, security duties and deletion/return within thirty days explicit?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-supplier_failure-G03

**Worksheet row:** 92; **priority:** 1.

**Original label:** category termination; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy POL-TERM-001.

**Original explanation / why the clause may be risky:** Excessive notice and penalty conflict with policy.

**Relevant clause — page 3, P003-C002:**

> 3. Company must give 100 days notice and pay a termination penalty of USD 5000.

**Original evidence quotation:**

> 3. Company must give 100 days notice and pay a termination penalty of USD 5000.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. Data-breach language does not explicitly establish personal-data processing; review policy applicability.

**Question for reviewer:** Is this risk assessment justified under POL-TERM-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Are breach cure and company convenience notice within thirty days, and is there a penalty?

**REVIEWER DECISION:**

#### EXISTING GOLD LABEL — SYN-supplier_failure-G04

**Worksheet row:** 93; **priority:** 1.

**Original label:** category governing_law; severity medium; state risk; risk_present True; confidence high; reviewer status pending_manual_review; policy BENCH-LAW-001.

**Original explanation / why the clause may be risky:** Benchmark-only foreign law departure.

**Relevant clause — page 4, P004-C002:**

> 4. The laws and exclusive courts of the fictional Kingdom of Eridia govern.

**Original evidence quotation:**

> 4. The laws and exclusive courts of the fictional Kingdom of Eridia govern.

**Reasons the annotation may be questionable:** Confirm policy applicability and the protected party; exact citation validity does not prove the interpretation or severity. This category and BENCH-LAW-001 are benchmark-only, unsupported by production taxonomy. Data-breach language does not explicitly establish personal-data processing; review policy applicability.

**Question for reviewer:** Is this risk assessment justified under BENCH-LAW-001 in this contract, and is the original category/severity appropriate? Identify any contextual assumptions or required revisions. Against the benchmark-only preference, is the stated law/forum a definite deviation, compliant selection or unresolved agreement?

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_failure-indemnification

**Worksheet row:** 94; **priority:** 2; **suggested category:** indemnification; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does indemnification apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_failure-payment

**Worksheet row:** 95; **priority:** 2; **suggested category:** payment; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does payment apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_failure-confidentiality

**Worksheet row:** 96; **priority:** 2; **suggested category:** confidentiality; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does confidentiality apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

#### POTENTIAL MISSING LABEL — REVIEW-SYN-supplier_failure-intellectual_property

**Worksheet row:** 97; **priority:** 2; **suggested category:** intellectual_property; **coverage classification:** B; **suggested severity:** not assigned.

**Exact supporting clause:** none identified for this alleged category gap. This is an absence/applicability prompt, not a present-clause finding. Use the exact complete page text above; do not substitute a different provision or create a quotation.

**Reason it may deserve an annotation:** the category has no gold target in this contract; if the synthetic policy applies and a required protection is absent, a reviewed omission label may improve coverage.

**Reasons it may not be a risk:** No gold target for this category; no unannotated substantive numbered clause was found. Review applicability before creating an omission label. Bespoke deliverables or an applicable licence interest must be established. An existing related provision may satisfy a requirement under a different category, or the contract type may not require it.

**Question for reviewer:** Does intellectual_property apply to this contract? If yes, identify an exact supporting provision or document full-page absence review; otherwise record not applicable or insufficient context. Governing-law candidates remain benchmark-only.

**REVIEWER DECISION:**

## Unresolved review issues and validation

Four supplier_red omissions require review: termination (existing G04 / LIVE-004), confidentiality (LIVE-005), data protection (LIVE-006), and IP (LIVE-007). Data-processing and deliverables assumptions are not established by silence. NDA durable G03 has a separate unsupported personal-data premise. Multi-page data evidence, absent IP schedules, overriding confidentiality terms, ambiguous notice/law/ownership provisions and the severity rubric remain unresolved.

All 42 gold annotations and all 40 spans are represented. Every one of the 100 worksheet IDs appears exactly once as a review item; the 55 coverage prompts and three model rows remain distinct. All quote blocks are source clause/page text or original gold quotations; absence prompts have no invented supporting clause. All reviewer decisions remain blank. Existing gold/worksheet/scoring/production file hashes were checked unchanged. Only synthetic sources and the existing synthetic trace were read; no live services or production database were used.

Automated validation: all 100 unique worksheet IDs mapped exactly once; all 42 gold IDs and 40 source spans represented; 100 blank reviewer decisions; worksheet and protected-file hashes unchanged. Full offline regression command from backend: `.\.venv\Scripts\python.exe -m evaluation.run_offline_tests`. Result: **144 passed, 3 live-service tests skipped, 0 failures/errors** (147 total), 10.387 seconds. Fixture scores remained TP=17, FP=3, FN=7; these are not model accuracy. No Gemini/Ollama requests or production data access occurred.
