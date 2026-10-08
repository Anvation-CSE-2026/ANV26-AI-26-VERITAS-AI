import React, { useState } from 'react'
import {
  IconShield,
  IconArrowRight,
  IconSearch,
  IconChevronDown,
  IconChevronUp,
} from '../icons/Icons'
import {
  RISK_LEVELS,
  CLAUSE_CATEGORIES,
  EVIDENCE_STATUSES,
} from '../../types/constants'

export default function RiskDashboardView({
  analysis,
  onNavigateToFinding,
  onOpenUpload,
  onLoadDemo,
}) {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedRiskFilter, setSelectedRiskFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedCardIndices, setExpandedCardIndices] = useState(new Set())

  if (!analysis) {
    return (
      <div className="p-16 text-center rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] text-[#8A9B91] space-y-4 max-w-xl mx-auto my-12">
        <IconShield className="w-12 h-12 mx-auto text-[#C5F5D5] opacity-40" />
        <h4 className="font-editorial text-3xl font-light text-[#F2F5F0]">
          No Risk Analysis Loaded
        </h4>
        <p className="text-sm font-sans text-[#8A9B91] leading-relaxed">
          Upload a contract or load the demo dataset to understand which terms may conflict with company requirements.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          {onOpenUpload && (
            <button
              onClick={onOpenUpload}
              className="px-6 py-2.5 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-xs font-sans font-semibold tracking-wide transition-all shadow-md"
            >
              Upload Contract
            </button>
          )}
          {onLoadDemo && (
            <button
              onClick={onLoadDemo}
              className="px-6 py-2.5 rounded-full border border-[rgba(197,245,213,0.25)] hover:border-[#C5F5D5] text-[#C5F5D5] text-xs font-sans tracking-wide transition-all"
            >
              Load Demo Data
            </button>
          )}
        </div>
      </div>
    )
  }

  const findings = analysis.findings || []

  // Counts from actual response data
  const criticalCount = findings.filter((f) => f.risk_level === 'critical').length
  const highCount = findings.filter((f) => f.risk_level === 'high').length
  const mediumCount = findings.filter((f) => f.risk_level === 'medium').length
  const lowRiskCount = findings.filter((f) => f.risk_level === 'low').length
  const totalFindingsCount = findings.length

  const toggleExpand = (idx) => {
    const next = new Set(expandedCardIndices)
    if (next.has(idx)) {
      next.delete(idx)
    } else {
      next.add(idx)
    }
    setExpandedCardIndices(next)
  }

  const filteredFindings = findings.filter((f) => {
    if (selectedRiskFilter !== 'all') {
      if (f.risk_level !== selectedRiskFilter) {
        return false
      }
    }
    if (selectedCategory !== 'all' && f.clause_category !== selectedCategory) {
      return false
    }
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      return (
        f.explanation.toLowerCase().includes(q) ||
        (f.clause_id && f.clause_id.toLowerCase().includes(q)) ||
        f.policy_id.toLowerCase().includes(q) ||
        (f.evidence_quote && f.evidence_quote.toLowerCase().includes(q))
      )
    }
    return true
  })

  // Risk distribution bar percentages
  const critPct = totalFindingsCount > 0 ? (criticalCount / totalFindingsCount) * 100 : 0
  const highPct = totalFindingsCount > 0 ? (highCount / totalFindingsCount) * 100 : 0
  const medPct = totalFindingsCount > 0 ? (mediumCount / totalFindingsCount) * 100 : 0
  const lowPct = totalFindingsCount > 0 ? (lowRiskCount / totalFindingsCount) * 100 : 0

  return (
    <div className="space-y-10 text-left pb-12">
      {/* 1. HEADER SECTION */}
      <div>
        <h1 className="font-editorial text-4xl sm:text-5xl lg:text-6xl font-light text-[#F2F5F0]">
          RISKS THAT MATTER.
        </h1>
        <p className="font-sans text-base sm:text-lg text-[#8A9B91] mt-2 leading-relaxed max-w-3xl">
          Understand which contract terms conflict with your company's policy requirements, categorized by severity.
        </p>
      </div>

      {/* 2. TOP METRICS STRIP */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[#101512] border border-[#F87171]/30 space-y-1">
          <div className="text-[11px] font-sans uppercase tracking-wider text-[#F87171] font-semibold">
            Critical Severity
          </div>
          <div className="font-editorial text-4xl sm:text-5xl font-light text-[#F87171]">
            {criticalCount}
          </div>
          <div className="text-[11px] font-sans text-[#8A9B91]">
            Immediate deal-breaker exposure
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#101512] border border-[#FB923C]/30 space-y-1">
          <div className="text-[11px] font-sans uppercase tracking-wider text-[#FB923C] font-semibold">
            High Priority
          </div>
          <div className="font-editorial text-4xl sm:text-5xl font-light text-[#FB923C]">
            {highCount}
          </div>
          <div className="text-[11px] font-sans text-[#8A9B91]">
            Important terms requiring redlines
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#101512] border border-[#FDE047]/30 space-y-1">
          <div className="text-[11px] font-sans uppercase tracking-wider text-[#FDE047] font-semibold">
            Medium Priority
          </div>
          <div className="font-editorial text-4xl sm:text-5xl font-light text-[#FDE047]">
            {mediumCount}
          </div>
          <div className="text-[11px] font-sans text-[#8A9B91]">
            Ambiguous or negotiable commitments
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] space-y-1">
          <div className="text-[11px] font-sans uppercase tracking-wider text-[#C5F5D5] font-semibold">
            Total Findings
          </div>
          <div className="font-editorial text-4xl sm:text-5xl font-light text-[#F2F5F0]">
            {totalFindingsCount}
          </div>
          <div className="text-[11px] font-sans text-[#8A9B91]">
            Objectively evaluated by AI
          </div>
        </div>
      </div>

      {/* 3. SIMPLE RISK DISTRIBUTION BAR */}
      <div className="p-6 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-3">
        <div className="flex items-center justify-between text-xs font-sans text-[#8A9B91]">
          <span className="font-semibold uppercase tracking-wider text-[#F2F5F0]">
            Risk Distribution
          </span>
          <div className="flex items-center gap-4">
            {criticalCount > 0 && (
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#F87171]" />
                <span>Critical ({critPct.toFixed(0)}%)</span>
              </span>
            )}
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#FB923C]" />
              <span>High ({highPct.toFixed(0)}%)</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#FDE047]" />
              <span>Medium ({medPct.toFixed(0)}%)</span>
            </span>
            {lowRiskCount > 0 && (
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#C5F5D5]" />
                <span>Low ({lowPct.toFixed(0)}%)</span>
              </span>
            )}
          </div>
        </div>

        <div className="w-full h-3 rounded-full bg-[#080B0A] overflow-hidden flex">
          {criticalCount > 0 && (
            <div
              className="h-full bg-[#F87171] transition-all"
              style={{ width: `${critPct}%` }}
              title={`Critical Risk: ${criticalCount}`}
            />
          )}
          <div
            className="h-full bg-[#FB923C] transition-all"
            style={{ width: `${highPct}%` }}
            title={`High Risk: ${highCount}`}
          />
          <div
            className="h-full bg-[#FDE047] transition-all"
            style={{ width: `${medPct}%` }}
            title={`Medium Risk: ${mediumCount}`}
          />
          {lowRiskCount > 0 && (
            <div
              className="h-full bg-[#C5F5D5] transition-all"
              style={{ width: `${lowPct}%` }}
              title={`Low Risk: ${lowRiskCount}`}
            />
          )}
        </div>
      </div>

      {/* 4. FILTER CONTROLS */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-2">
          {['all', 'critical', 'high', 'medium', 'low'].map((riskKey) => (
            <button
              key={riskKey}
              onClick={() => setSelectedRiskFilter(riskKey)}
              className={`px-4 py-1.5 rounded-full text-xs font-sans capitalize transition-all border ${
                selectedRiskFilter === riskKey
                  ? 'bg-[#15231B] border-[#C5F5D5] text-[#C5F5D5] font-semibold'
                  : 'bg-[#101512] border-[rgba(197,245,213,0.1)] text-[#8A9B91] hover:text-[#F2F5F0]'
              }`}
            >
              {riskKey === 'all' ? 'All Risks' : `${riskKey} Risk`}
            </button>
          ))}

          {/* Legal Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-[#101512] border border-[rgba(197,245,213,0.15)] text-[#F2F5F0] text-xs font-sans rounded-full px-4 py-1.5 focus:outline-none focus:border-[#C5F5D5]"
          >
            <option value="all">All Categories</option>
            {Object.entries(CLAUSE_CATEGORIES).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search risks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-[#101512] border border-[rgba(197,245,213,0.15)] rounded-full px-4 py-1.5 text-xs text-[#F2F5F0] placeholder-[#8A9B91] focus:outline-none focus:border-[#C5F5D5] w-56 font-sans"
          />
          <IconSearch className="w-3.5 h-3.5 text-[#8A9B91] absolute right-3.5 top-2.5 pointer-events-none" />
        </div>
      </div>

      {/* 5. FINDINGS AS CLEAN EXPANDABLE CARDS */}
      <div className="space-y-5">
        {filteredFindings.map((finding, idx) => {
          const riskConfig = RISK_LEVELS[finding.risk_level] || RISK_LEVELS.medium
          const categoryLabel =
            CLAUSE_CATEGORIES[finding.clause_category] || finding.clause_category
          const isExpanded = expandedCardIndices.has(idx)
          const evConfig = EVIDENCE_STATUSES[finding.evidence_status] || EVIDENCE_STATUSES.needs_review

          return (
            <div
              key={idx}
              className="p-6 sm:p-7 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] hover:border-[rgba(197,245,213,0.25)] transition-all space-y-4 shadow-sm"
            >
              {/* DEFAULT CARD HEADER: Risk Title & Severity Badge */}
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-sans font-semibold ${riskConfig.badgeClass}`}>
                    {riskConfig.label}
                  </span>
                  <h3 className="font-sans text-lg sm:text-xl font-semibold text-[#F2F5F0]">
                    {categoryLabel} {finding.finding_status === 'compliant' ? '— Compliant' : finding.potential_omission ? '— Potential omission' : 'Risk'}
                  </h3>
                </div>

                <div className="flex items-center gap-3">
                  {onNavigateToFinding && (
                    <button
                      onClick={() => onNavigateToFinding(finding)}
                      className="px-4 py-1.5 rounded-lg bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-xs font-sans font-semibold flex items-center gap-1.5 transition-all shadow-sm"
                    >
                      <span>VIEW SUPPORTING EVIDENCE</span>
                      <IconArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>

              {/* WHAT WE FOUND: One-sentence plain-English */}
              <div className="space-y-1">
                <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#C5F5D5]">
                  WHAT WE FOUND
                </span>
                <p className="text-base text-[#F2F5F0] font-sans leading-relaxed">
                  {finding.explanation}
                </p>
              </div>

              {/* WHY IT MATTERS: Grounded in available evidence */}
              <div className="space-y-1">
                <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#8A9B91]">
                  WHY IT MATTERS
                </span>
                <p className="text-sm text-[#8A9B91] font-sans leading-relaxed">
                  {finding.applicable_policy_rule?.rule
                    ? `Company policy requires: ${finding.applicable_policy_rule.rule}`
                    : finding.policy_requirement
                    ? `Policy standard: ${finding.policy_requirement}`
                    : 'This provision creates legal or operational exposure deviating from standard guidelines.'}
                </p>
              </div>

              {/* RECOMMENDED ACTION */}
              {finding.recommended_action && (
                <div className="p-4 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.1)] space-y-1">
                  <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#A8E6BF]">
                    RECOMMENDED ACTION
                  </span>
                  <p className="text-sm text-[#F2F5F0] font-sans leading-relaxed">
                    {finding.recommended_action}
                  </p>
                </div>
              )}

              {/* EXPANDABLE DETAILS ACCORDION */}
              <div className="pt-2 border-t border-[rgba(197,245,213,0.08)]">
                <button
                  onClick={() => toggleExpand(idx)}
                  className="text-xs font-mono text-[#8A9B91] hover:text-[#C5F5D5] flex items-center gap-1.5 transition-colors"
                >
                  <span>{isExpanded ? 'Hide Citation & Clause Details' : 'View Citation & Clause Details'}</span>
                  {isExpanded ? (
                    <IconChevronUp className="w-3.5 h-3.5" />
                  ) : (
                    <IconChevronDown className="w-3.5 h-3.5" />
                  )}
                </button>

                {isExpanded && (
                  <div className="mt-4 p-5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.1)] space-y-4 text-xs font-sans">
                    {/* Original Clause Quote */}
                    {finding.evidence_quote ? (
                      <div className="space-y-1.5">
                        <span className="font-sans font-semibold text-[#8A9B91] uppercase text-[11px]">
                          ORIGINAL CLAUSE QUOTE:
                        </span>
                        <div className="p-3.5 rounded-lg bg-[#101512] border border-[rgba(197,245,213,0.08)] text-[#C5F5D5] font-editorial text-base italic leading-relaxed">
                          "{finding.evidence_quote}"
                        </div>
                      </div>
                    ) : finding.potential_omission ? (
                      <div className="p-3 rounded-lg bg-[#180E10] border border-[#F87171]/30 text-[#F87171]">
                        Potential omission — absence and policy applicability require human review.
                      </div>
                    ) : null}

                    {/* Metadata Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1 text-xs font-mono">
                      <div>
                        <span className="text-[#8A9B91]">Clause ID:</span>{' '}
                        <span className="text-[#F2F5F0]">{finding.clause_id || 'Omission'}</span>
                      </div>
                      <div>
                        <span className="text-[#8A9B91]">Page:</span>{' '}
                        <span className="text-[#F2F5F0]">{finding.page_number || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="text-[#8A9B91]">Policy ID:</span>{' '}
                        <span className="text-[#A8E6BF]">{finding.policy_id}</span>
                      </div>
                      <div>
                        <span className="text-[#8A9B91]">Verification:</span>{' '}
                        <span className="text-[#C5F5D5]">{evConfig.label}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {filteredFindings.length === 0 && (
          <div className="p-12 text-center text-[#8A9B91] text-sm font-sans rounded-2xl border border-[rgba(197,245,213,0.12)] bg-[#101512]">
            No risks match the selected filter criteria.
          </div>
        )}
      </div>
    </div>
  )
}
