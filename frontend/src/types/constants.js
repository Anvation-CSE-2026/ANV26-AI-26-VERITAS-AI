/**
 * VERITAS AI - Frontend Constants & Contract Enums
 * Strictly mapped to docs/frontend-api-contract.md
 * Styled with the Editorial Mint & Charcoal Design System
 */

export const RISK_LEVELS = {
  critical: {
    label: 'Critical Risk',
    badgeClass: 'text-[#F87171] bg-[#180E10] border border-[#F87171]/30',
    color: '#F87171',
    bg: 'bg-[#F87171]',
  },
  high: {
    label: 'High Risk',
    badgeClass: 'text-[#FB923C] bg-[#19130D] border border-[#FB923C]/30',
    color: '#FB923C',
    bg: 'bg-[#FB923C]',
  },
  medium: {
    label: 'Medium Risk',
    badgeClass: 'text-[#FDE047] bg-[#19190D] border border-[#FDE047]/30',
    color: '#FDE047',
    bg: 'bg-[#FDE047]',
  },
  low: {
    label: 'Low Risk',
    badgeClass: 'text-[#C5F5D5] bg-[#101512] border border-[#C5F5D5]/30',
    color: '#C5F5D5',
    bg: 'bg-[#C5F5D5]',
  },
}

export const FINDING_STATUSES = {
  compliant: {
    label: 'Compliant',
    badgeClass: 'text-[#C5F5D5] bg-[#101512] border border-[#C5F5D5]/30',
  },
  risky: {
    label: 'Risky Clause',
    badgeClass: 'text-[#FB923C] bg-[#19130D] border border-[#FB923C]/30',
  },
  ambiguous: {
    label: 'Ambiguous Language',
    badgeClass: 'text-[#E879F9] bg-[#190D1A] border border-[#E879F9]/30',
  },
  conflicting: {
    label: 'Conflicting Terms',
    badgeClass: 'text-[#F87171] bg-[#180E10] border border-[#F87171]/30',
  },
  missing: {
    label: 'Potential Omission',
    badgeClass: 'text-[#F87171] bg-[#180E10] border border-[#F87171]/30',
  },
}

export const EVIDENCE_STATUSES = {
  verified: {
    label: 'Verified Provenance',
    description: 'Exact quote verified against original source text.',
    badgeClass: 'text-[#C5F5D5] bg-[#101512] border border-[#C5F5D5]/40',
  },
  needs_review: {
    label: 'Needs Review',
    description: 'Interpretation or context requires human review.',
    badgeClass: 'text-[#FDE047] bg-[#19190D] border border-[#FDE047]/30',
  },
  unsupported: {
    label: 'Unsupported',
    description: 'Excluded from accepted records by verification filter.',
    badgeClass: 'text-[#F87171] bg-[#180E10] border border-[#F87171]/30',
  },
}

export const CLAUSE_CATEGORIES = {
  liability: 'Liability & Caps',
  indemnification: 'Indemnification',
  termination: 'Termination & Exit',
  confidentiality: 'Confidentiality & NDAs',
  payment: 'Payment & Billing',
  data_protection: 'Data Protection & Security',
  intellectual_property: 'Intellectual Property (IP)',
}

export const DEADLINE_TYPES = {
  fixed_date: { label: 'Fixed Date', badgeClass: 'text-[#A8E6BF] bg-[#101512] border border-[#A8E6BF]/30' },
  relative: { label: 'Relative Timeline', badgeClass: 'text-[#C5F5D5] bg-[#101512] border border-[#C5F5D5]/30' },
  ambiguous: { label: 'Ambiguous Timeline', badgeClass: 'text-[#FDE047] bg-[#19190D] border border-[#FDE047]/30' },
  unspecified: { label: 'Unspecified', badgeClass: 'text-[#8A9B91] bg-[#101512] border border-white/10' },
}

export const ANALYSIS_STAGES = [
  { id: 'extract', label: 'Extracting document', detail: 'Parsing PDF bytes, token offsets, and clause boundaries' },
  { id: 'match', label: 'Matching company policies', detail: 'Vector semantic retrieval against company playbook' },
  { id: 'reason', label: 'Analyzing contractual risks', detail: 'Gemini reasoning across risk categories and obligations' },
  { id: 'verify', label: 'Verifying evidence', detail: 'Deterministic quote verification and provenance validation' },
  { id: 'prepare', label: 'Preparing results', detail: 'Synthesizing verified findings and audit trails' },
]

export const WORKSPACE_TABS = [
  { id: 'overview', label: 'Overview', icon: 'IconNetwork' },
  { id: 'contracts', label: 'Contract', icon: 'IconDocument' },
  { id: 'risk', label: 'Risks', icon: 'IconShield' },
  { id: 'evidence', label: 'Evidence', icon: 'IconScale' },
  { id: 'obligations', label: 'Action Plan', icon: 'IconClock' },
  { id: 'policy', label: 'Policy Comparison', icon: 'IconSparkles' },
  { id: 'graph', label: 'Knowledge Graph', icon: 'IconGraph' },
  { id: 'billing', label: 'Billing & Plan', icon: 'IconCreditCard' },
  { id: 'company', label: 'Company Workspace', icon: 'IconShield' },
]
