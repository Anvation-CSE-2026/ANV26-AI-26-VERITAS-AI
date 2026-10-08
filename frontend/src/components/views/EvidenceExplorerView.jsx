import React, { useState, useMemo } from 'react'
import {
  IconScale,
  IconDocument,
  IconShield,
  IconArrowLeft,
  IconArrowRight,
  IconCheckCircle,
} from '../icons/Icons'
import {
  RISK_LEVELS,
  CLAUSE_CATEGORIES,
} from '../../types/constants'

export default function EvidenceExplorerView({
  analysis,
  initialSelectedFinding,
  onOpenUpload,
  onLoadDemo,
}) {
  const findings = useMemo(() => analysis?.findings || [], [analysis])
  const [userSelectedIndex, setUserSelectedIndex] = useState(null)

  const initialIndex = useMemo(() => {
    if (!initialSelectedFinding || findings.length === 0) return 0
    const idx = findings.findIndex(
      (f) =>
        (f.clause_id && f.clause_id === initialSelectedFinding.clause_id) ||
        (f.policy_id && f.policy_id === initialSelectedFinding.policy_id)
    )
    return idx !== -1 ? idx : 0
  }, [initialSelectedFinding, findings])

  const selectedIndex = userSelectedIndex !== null ? userSelectedIndex : initialIndex

  if (!analysis || findings.length === 0) {
    return (
      <div className="p-16 text-center rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] text-[#8A9B91] space-y-4 max-w-xl mx-auto my-12">
        <IconScale className="w-12 h-12 mx-auto text-[#C5F5D5] opacity-40" />
        <h4 className="font-editorial text-3xl font-light text-[#F2F5F0]">
          No Evidence Citations Available
        </h4>
        <p className="text-sm font-sans text-[#8A9B91] leading-relaxed">
          Upload an agreement or load the demo dataset to review verified quotes and policy comparisons.
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

  const currentFinding = findings[selectedIndex] || findings[0]
  const riskConfig = RISK_LEVELS[currentFinding?.risk_level] || RISK_LEVELS.medium
  const categoryLabel =
    CLAUSE_CATEGORIES[currentFinding?.clause_category] || currentFinding?.clause_category

  const handlePrev = () => {
    setUserSelectedIndex((prev) => {
      const curr = prev !== null ? prev : initialIndex
      return curr > 0 ? curr - 1 : findings.length - 1
    })
  }

  const handleNext = () => {
    setUserSelectedIndex((prev) => {
      const curr = prev !== null ? prev : initialIndex
      return curr < findings.length - 1 ? curr + 1 : 0
    })
  }

  return (
    <div className="space-y-10 text-left pb-12">
      {/* 1. HEADER SECTION */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="font-editorial text-4xl sm:text-5xl lg:text-6xl font-light text-[#F2F5F0]">
            SEE THE PROOF.
          </h1>
          <p className="font-sans text-base sm:text-lg text-[#8A9B91] mt-2 leading-relaxed max-w-2xl">
            Understand exactly why VERITAS AI flagged each contract clause.
          </p>
        </div>

        {/* Previous / Next Controls */}
        <div className="flex items-center gap-3 bg-[#101512] px-4 py-2 rounded-2xl border border-[rgba(197,245,213,0.12)]">
          <button
            onClick={handlePrev}
            className="p-2 rounded-xl hover:bg-[#080B0A] text-[#8A9B91] hover:text-[#C5F5D5] transition-colors"
            title="Previous finding"
          >
            <IconArrowLeft className="w-5 h-5" />
          </button>
          <span className="text-sm font-sans font-medium text-[#F2F5F0] min-w-[110px] text-center">
            {selectedIndex + 1} of {findings.length} findings
          </span>
          <button
            onClick={handleNext}
            className="p-2 rounded-xl hover:bg-[#080B0A] text-[#8A9B91] hover:text-[#C5F5D5] transition-colors"
            title="Next finding"
          >
            <IconArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Finding Selector Chips */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
        {findings.map((f, idx) => {
          const isSelected = idx === selectedIndex
          const fRisk = RISK_LEVELS[f.risk_level] || RISK_LEVELS.medium
          return (
            <button
              key={idx}
              onClick={() => setUserSelectedIndex(idx)}
              className={`px-4 py-2 rounded-xl text-xs font-sans font-medium whitespace-nowrap transition-all border shrink-0 flex items-center gap-2 ${
                isSelected
                  ? 'bg-[#15231B] border-[#C5F5D5] text-[#C5F5D5] shadow-md ring-1 ring-[#C5F5D5]/30'
                  : 'bg-[#101512] border-[rgba(197,245,213,0.1)] text-[#8A9B91] hover:text-[#F2F5F0]'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${fRisk.bg}`} />
              <span>{CLAUSE_CATEGORIES[f.clause_category] || f.clause_category}</span>
              <span className="text-[10px] font-mono opacity-70">#{idx + 1}</span>
            </button>
          )
        })}
      </div>

      {/* 2. FINDING OVERVIEW BANNER */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-sans font-semibold ${riskConfig.badgeClass}`}>
              {riskConfig.label}
            </span>
            <span className="text-sm font-sans text-[#8A9B91]">
              Category: <strong className="text-[#F2F5F0]">{categoryLabel}</strong>
            </span>
          </div>
          <h2 className="font-editorial text-2xl sm:text-3xl font-light text-[#F2F5F0] pt-1">
            {currentFinding.explanation}
          </h2>
        </div>

        {/* Source Verified Badge with Accurate Disclaimer */}
        <div className="p-3.5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.15)] flex items-start gap-2.5 max-w-sm">
          <IconCheckCircle className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
          <div className="text-xs font-sans text-[#8A9B91] leading-relaxed">
            <span className="font-semibold text-[#C5F5D5] block mb-0.5">SOURCE VERIFIED</span>
            The quoted source text and references were checked against the available document data.
          </div>
        </div>
      </div>

      {/* 3. THREE-STEP VISUALLY CONNECTED COMPARISON */}
      <div className="space-y-6 relative">
        {/* STEP 1: WHAT THE CONTRACT SAYS */}
        <div className="p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] space-y-4 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="w-7 h-7 rounded-full bg-[#15231B] border border-[#C5F5D5]/40 text-[#C5F5D5] text-xs font-mono font-bold flex items-center justify-center">
                1
              </span>
              <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#C5F5D5] flex items-center gap-2">
                <IconDocument className="w-4 h-4" />
                <span>STEP 1: WHAT THE CONTRACT SAYS</span>
              </span>
            </div>

            {/* Source IDs & Page Number */}
            <div className="text-xs font-mono text-[#8A9B91] bg-[#080B0A] px-3 py-1 rounded-lg border border-white/5">
              {currentFinding.clause_id ? (
                <span>Clause {currentFinding.clause_id} · Page {currentFinding.page_number}</span>
              ) : (
                <span className="text-[#FB923C]">Potential Omission</span>
              )}
            </div>
          </div>

          {currentFinding.evidence_quote ? (
            <div className="p-6 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.1)] text-[#C5F5D5] font-editorial text-lg sm:text-xl italic leading-relaxed">
              "{currentFinding.evidence_quote}"
            </div>
          ) : currentFinding.potential_omission ? (
            <div className="p-5 rounded-xl bg-[#180E10] border border-[#F87171]/30 text-sm text-[#F87171] font-sans">
              <strong>Potential Omission:</strong> This requirement was not identified in the contract text. A full manual document review is required to confirm absence.
            </div>
          ) : (
            <div className="p-5 rounded-xl bg-[#080B0A] text-sm text-[#8A9B91] italic font-sans">
              No direct quotation available in document data.
            </div>
          )}
        </div>

        {/* Visual Connector Line */}
        <div className="flex justify-center -my-3 relative z-10">
          <div className="w-0.5 h-6 bg-[rgba(197,245,213,0.3)]" />
        </div>

        {/* STEP 2: WHAT YOUR COMPANY REQUIRES */}
        <div className="p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] space-y-4 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="w-7 h-7 rounded-full bg-[#15231B] border border-[#A8E6BF]/40 text-[#A8E6BF] text-xs font-mono font-bold flex items-center justify-center">
                2
              </span>
              <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#A8E6BF] flex items-center gap-2">
                <IconShield className="w-4 h-4" />
                <span>STEP 2: WHAT YOUR COMPANY REQUIRES</span>
              </span>
            </div>

            <div className="text-xs font-mono text-[#A8E6BF] bg-[#080B0A] px-3 py-1 rounded-lg border border-white/5">
              Rule {currentFinding.policy_id}
            </div>
          </div>

          <div className="p-6 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.1)] text-[#F2F5F0] font-sans text-base leading-relaxed">
            {currentFinding.applicable_policy_rule?.rule ||
              currentFinding.policy_requirement ||
              'Internal policy guidance governing this contractual provision.'}
          </div>
        </div>

        {/* Visual Connector Line */}
        <div className="flex justify-center -my-3 relative z-10">
          <div className="w-0.5 h-6 bg-[rgba(197,245,213,0.3)]" />
        </div>

        {/* STEP 3: IDENTIFIED DEVIATION */}
        <div className="p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] space-y-4 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span
                className="w-7 h-7 rounded-full text-xs font-mono font-bold flex items-center justify-center border"
                style={{
                  color: riskConfig.color,
                  borderColor: `${riskConfig.color}60`,
                  backgroundColor: `${riskConfig.color}15`,
                }}
              >
                3
              </span>
              <span
                className="text-xs font-sans font-semibold uppercase tracking-wider flex items-center gap-2"
                style={{ color: riskConfig.color }}
              >
                <IconScale className="w-4 h-4" />
                <span>STEP 3: IDENTIFIED DEVIATION</span>
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-mono ${riskConfig.badgeClass}`}>
                {riskConfig.label}
              </span>
              <span className="text-xs font-mono text-[#8A9B91] uppercase bg-[#080B0A] px-2.5 py-0.5 rounded border border-white/5">
                {currentFinding.finding_status || 'Deviation'}
              </span>
            </div>
          </div>

          <div className="p-5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.1)] text-[#F2F5F0] font-sans text-base leading-relaxed">
            {currentFinding.explanation}
          </div>
        </div>

        {/* Visual Connector Line */}
        <div className="flex justify-center -my-3 relative z-10">
          <div className="w-0.5 h-6 bg-[rgba(197,245,213,0.3)]" />
        </div>

        {/* STEP 4: RECOMMENDED ACTION */}
        <div className="p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] space-y-4 relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="w-7 h-7 rounded-full bg-[#15231B] border border-[#C5F5D5]/40 text-[#C5F5D5] text-xs font-mono font-bold flex items-center justify-center">
                4
              </span>
              <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#C5F5D5] flex items-center gap-2">
                <IconCheckCircle className="w-4 h-4 text-[#C5F5D5]" />
                <span>STEP 4: RECOMMENDED ACTION & REMEDIATION</span>
              </span>
            </div>

            <div className="text-xs font-mono text-[#C5F5D5] bg-[#080B0A] px-3 py-1 rounded-lg border border-white/5">
              Action Plan
            </div>
          </div>

          <div className="p-5 rounded-xl bg-[#080B0A] border border-[#C5F5D5]/20 space-y-2">
            <p className="text-base text-[#F2F5F0] font-sans leading-relaxed">
              {currentFinding.recommended_action ||
                'Request formal redline amendment from counterparty to align with company policy minimums.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
