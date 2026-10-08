import React, { useState } from 'react'
import {
  IconSparkles,
  IconDocument,
  IconShield,
  IconAlertTriangle,
  IconChevronDown,
  IconChevronUp,
} from '../icons/Icons'
import {
  CLAUSE_CATEGORIES,
  RISK_LEVELS,
  FINDING_STATUSES,
} from '../../types/constants'

export default function PolicyComparisonView({
  analysis,
  onOpenUpload,
  onLoadDemo,
}) {
  const findings = analysis?.findings || []
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [expandedIndices, setExpandedIndices] = useState(new Set())

  if (!analysis || findings.length === 0) {
    return (
      <div className="p-16 text-center rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] text-[#8A9B91] space-y-4 max-w-xl mx-auto my-12">
        <IconSparkles className="w-12 h-12 mx-auto text-[#C5F5D5] opacity-40" />
        <h4 className="font-editorial text-3xl font-light text-[#F2F5F0]">
          No Policy Comparisons Available
        </h4>
        <p className="text-sm font-sans text-[#8A9B91] leading-relaxed">
          Upload a contract or load the demo dataset to compare contractual provisions against company compliance rules.
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

  const toggleExpand = (idx) => {
    const next = new Set(expandedIndices)
    if (next.has(idx)) {
      next.delete(idx)
    } else {
      next.add(idx)
    }
    setExpandedIndices(next)
  }

  const filteredFindings = findings.filter((f) => {
    if (selectedCategory !== 'all' && f.clause_category !== selectedCategory) return false
    return true
  })

  return (
    <div className="space-y-10 text-left pb-12">
      {/* 1. HEADER */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="font-editorial text-4xl sm:text-5xl lg:text-6xl font-light text-[#F2F5F0]">
            CONTRACT VS COMPANY POLICY.
          </h1>
          <p className="font-sans text-base sm:text-lg text-[#8A9B91] mt-2 leading-relaxed max-w-3xl">
            See where contractual terms may differ from your organization's requirements.
          </p>
        </div>

        {/* Category Filter */}
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="bg-[#101512] border border-[rgba(197,245,213,0.15)] text-[#F2F5F0] text-xs font-sans rounded-full px-4 py-2 focus:outline-none focus:border-[#C5F5D5]"
        >
          <option value="all">All Legal Categories</option>
          {Object.entries(CLAUSE_CATEGORIES).map(([key, label]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {/* 2. SIDE-BY-SIDE COMPARISON CARDS */}
      <div className="space-y-6">
        {filteredFindings.map((item, idx) => {
          const riskConfig = RISK_LEVELS[item.risk_level] || RISK_LEVELS.medium
          const statusConfig = FINDING_STATUSES[item.finding_status] || FINDING_STATUSES.risky
          const isExpanded = expandedIndices.has(idx)
          const categoryLabel = CLAUSE_CATEGORIES[item.clause_category] || item.clause_category

          return (
            <div
              key={idx}
              className="p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-6 shadow-sm"
            >
              {/* Row Header */}
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[rgba(197,245,213,0.08)]">
                <div className="flex items-center gap-2.5">
                  <span className={`px-3 py-1 rounded-full text-xs font-sans font-semibold ${riskConfig.badgeClass}`}>
                    {riskConfig.label}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-sans font-medium ${statusConfig.badgeClass}`}>
                    {statusConfig.label}
                  </span>
                  <span className="text-sm font-sans font-semibold text-[#F2F5F0] ml-2">
                    {categoryLabel}
                  </span>
                </div>

                <div className="text-xs font-mono text-[#8A9B91]">
                  {item.clause_id ? `Clause ${item.clause_id} · Page ${item.page_number}` : 'Potential Omission'}
                </div>
              </div>

              {/* 3-COLUMN COMPARISON: WHAT CONTRACT SAYS | WHAT POLICY REQUIRES | WHAT SHOULD CHANGE */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* COLUMN 1: WHAT THE CONTRACT SAYS */}
                <div className="p-5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] space-y-3 flex flex-col justify-between">
                  <div className="space-y-2">
                    <span className="text-xs font-sans font-semibold text-[#C5F5D5] flex items-center gap-1.5 uppercase tracking-wider">
                      <IconDocument className="w-4 h-4 text-[#C5F5D5]" />
                      <span>WHAT THE CONTRACT SAYS</span>
                    </span>

                    {item.evidence_quote ? (
                      <div className="p-3.5 bg-[#101512] rounded-lg border border-white/5 font-editorial italic text-sm text-[#C5F5D5] leading-relaxed line-clamp-4">
                        "{item.evidence_quote}"
                      </div>
                    ) : item.potential_omission ? (
                      <div className="text-xs text-[#F87171] p-3 bg-[#180E10] rounded-lg border border-[#F87171]/20 font-sans">
                        Clause omitted in contract text.
                      </div>
                    ) : (
                      <div className="text-xs text-[#8A9B91] italic font-sans p-3">
                        No direct quote available.
                      </div>
                    )}
                  </div>

                  {item.evidence_quote && (
                    <button
                      onClick={() => toggleExpand(idx)}
                      className="text-xs font-sans text-[#8A9B91] hover:text-[#C5F5D5] flex items-center gap-1 pt-1 transition-colors"
                    >
                      <span>{isExpanded ? 'Collapse excerpt' : 'View full excerpt'}</span>
                      {isExpanded ? (
                        <IconChevronUp className="w-3.5 h-3.5" />
                      ) : (
                        <IconChevronDown className="w-3.5 h-3.5" />
                      )}
                    </button>
                  )}
                </div>

                {/* COLUMN 2: WHAT THE POLICY REQUIRES */}
                <div className="p-5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-sans font-semibold text-[#A8E6BF] flex items-center gap-1.5 uppercase tracking-wider">
                      <IconShield className="w-4 h-4 text-[#A8E6BF]" />
                      <span>WHAT THE POLICY REQUIRES</span>
                    </span>
                    <span className="text-[10px] font-mono text-[#A8E6BF]">{item.policy_id}</span>
                  </div>

                  <p className="text-sm text-[#F2F5F0] font-sans leading-relaxed">
                    {item.applicable_policy_rule?.rule || item.policy_requirement}
                  </p>
                </div>

                {/* COLUMN 3: WHAT SHOULD CHANGE */}
                <div className="p-5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] space-y-3">
                  <span className="text-xs font-sans font-semibold text-[#FDE047] flex items-center gap-1.5 uppercase tracking-wider">
                    <IconAlertTriangle className="w-4 h-4 text-[#FDE047]" />
                    <span>WHAT SHOULD CHANGE</span>
                  </span>

                  <p className="text-sm text-[#F2F5F0] font-sans leading-relaxed">
                    {item.recommended_action || item.applicable_policy_rule?.recommended_action || 'Negotiate revision to align with company standard.'}
                  </p>
                </div>
              </div>

              {/* Expandable full quote if opened */}
              {isExpanded && item.evidence_quote && (
                <div className="p-4 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.1)] font-editorial italic text-base text-[#C5F5D5] leading-relaxed">
                  "{item.evidence_quote}"
                </div>
              )}

              {/* BELOW: PLAIN-ENGLISH EXPLANATION */}
              <div className="p-4 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-1">
                <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#C5F5D5]">
                  PLAIN-ENGLISH ANALYSIS
                </span>
                <p className="text-sm text-[#8A9B91] font-sans leading-relaxed">
                  {item.explanation}
                </p>
              </div>
            </div>
          )
        })}

        {filteredFindings.length === 0 && (
          <div className="p-12 text-center text-[#8A9B91] text-sm font-sans rounded-2xl border border-[rgba(197,245,213,0.12)] bg-[#101512]">
            No policy comparisons found for the selected category.
          </div>
        )}
      </div>
    </div>
  )
}
