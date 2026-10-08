import React, { useState, useMemo } from 'react'
import {
  IconDocument,
  IconArrowRight,
  IconSparkles,
  IconChevronDown,
  IconChevronUp,
} from '../icons/Icons'
import { RISK_LEVELS, CLAUSE_CATEGORIES } from '../../types/constants'

export default function OverviewView({
  analysis,
  contract,
  isDemoData,
  onNavigateTab,
  onNavigateToFinding,
  onOpenUpload,
  onLoadDemo,
}) {
  const [selectedChartSegment, setSelectedChartSegment] = useState(null)
  const [expandedAttentionCard, setExpandedAttentionCard] = useState(null)
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false)

  const findings = useMemo(() => analysis?.findings || [], [analysis])
  const obligations = useMemo(() => analysis?.obligations || [], [analysis])
  const warnings = useMemo(() => analysis?.warnings || [], [analysis])
  const rejections = useMemo(() => analysis?.verification_rejections || [], [analysis])

  // Counts strictly from actual backend data
  const criticalCount = findings.filter((f) => f.risk_level === 'critical').length
  const highCount = findings.filter((f) => f.risk_level === 'high').length
  const mediumCount = findings.filter((f) => f.risk_level === 'medium').length
  const lowCount = findings.filter((f) => f.risk_level === 'low').length
  const totalFindings = findings.length
  const highPriorityTotal = criticalCount + highCount
  const evidenceBackedCount = findings.filter((f) => f.evidence_status === 'verified').length
  const obligationsCount = obligations.length

  // Counts per category for the horizontal bar chart
  const categoryCounts = useMemo(() => {
    const counts = {}
    Object.keys(CLAUSE_CATEGORIES).forEach((cat) => {
      counts[cat] = 0
    })
    findings.forEach((f) => {
      const cat = f.clause_category || 'other'
      counts[cat] = (counts[cat] || 0) + 1
    })
    return counts
  }, [findings])

  const maxCategoryCount = Math.max(...Object.values(categoryCounts), 1)

  // Top 3 attention findings (Critical & High first, then Medium)
  const topAttentionFindings = useMemo(() => {
    const sorted = [...findings].sort((a, b) => {
      const priority = { critical: 4, high: 3, medium: 2, low: 1 }
      return (priority[b.risk_level] || 0) - (priority[a.risk_level] || 0)
    })
    return sorted.slice(0, 3)
  }, [findings])

  // Groupings for the Priority Actions Panel
  const fixFirstItems = useMemo(
    () => findings.filter((f) => f.risk_level === 'critical' || f.risk_level === 'high'),
    [findings]
  )
  const reviewNextItems = useMemo(
    () => findings.filter((f) => f.risk_level === 'medium'),
    [findings]
  )
  const monitorItems = useMemo(
    () => [
      ...findings.filter((f) => f.risk_level === 'low'),
      ...obligations.slice(0, 3).map((o) => ({
        explanation: o.description,
        recommended_action: o.deadline ? `Duty assigned to ${o.responsible_party || 'contractor'} (${o.deadline})` : `Responsible party: ${o.responsible_party || 'unspecified'}`,
        isObligation: true,
      })),
    ],
    [findings, obligations]
  )

  // Doughnut chart math
  const doughnutSegments = useMemo(() => {
    if (totalFindings === 0) return []
    const segments = [
      { key: 'critical', label: 'Critical Risk', count: criticalCount, color: '#F87171' },
      { key: 'high', label: 'High Risk', count: highCount, color: '#FB923C' },
      { key: 'medium', label: 'Medium Risk', count: mediumCount, color: '#FDE047' },
      { key: 'low', label: 'Low Risk', count: lowCount, color: '#C5F5D5' },
    ].filter((s) => s.count > 0)

    let accumulatedAngle = 0
    return segments.map((seg) => {
      const angle = (seg.count / totalFindings) * 360
      const startAngle = accumulatedAngle
      accumulatedAngle += angle
      return {
        ...seg,
        startAngle,
        endAngle: accumulatedAngle,
        pct: ((seg.count / totalFindings) * 100).toFixed(0),
      }
    })
  }, [totalFindings, criticalCount, highCount, mediumCount, lowCount])

  if (!analysis) {
    return (
      <div className="text-center py-24 px-6 max-w-xl mx-auto space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] text-[#C5F5D5] flex items-center justify-center mx-auto mb-4">
          <IconDocument className="w-8 h-8" />
        </div>
        <h3 className="font-editorial text-4xl font-light text-[#C5F5D5]">
          Your Contract. Decoded.
        </h3>
        <p className="font-sans text-base text-[#8A9B91] leading-relaxed">
          Upload a supplier PDF agreement to review potential risks against company policy standards, or explore our precomputed sample dataset immediately.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <button
            onClick={onOpenUpload}
            className="px-6 py-3 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-sm font-semibold tracking-wide transition-all shadow-md shadow-[#C5F5D5]/10"
          >
            Upload Contract PDF
          </button>
          {onLoadDemo && (
            <button
              onClick={onLoadDemo}
              className="px-6 py-3 rounded-full border border-[rgba(197,245,213,0.25)] hover:border-[#C5F5D5] bg-[#101512] text-[#C5F5D5] text-sm font-medium tracking-wide transition-all"
            >
              Explore Sample Demo
            </button>
          )}
        </div>
      </div>
    )
  }

  // Helper to render SVG arc for doughnut
  const getCoordinatesForAngle = (angle, radius) => {
    const rad = ((angle - 90) * Math.PI) / 180
    return [100 + radius * Math.cos(rad), 100 + radius * Math.sin(rad)]
  }

  const getDoughnutPath = (startAngle, endAngle) => {
    const isFullCircle = endAngle - startAngle >= 359.99
    const actualEnd = isFullCircle ? startAngle + 359.99 : endAngle
    const [startX, startY] = getCoordinatesForAngle(startAngle, 78)
    const [endX, endY] = getCoordinatesForAngle(actualEnd, 78)
    const [innerStartX, innerStartY] = getCoordinatesForAngle(startAngle, 52)
    const [innerEndX, innerEndY] = getCoordinatesForAngle(actualEnd, 52)
    const largeArcFlag = actualEnd - startAngle > 180 ? 1 : 0

    return [
      `M ${startX} ${startY}`,
      `A 78 78 0 ${largeArcFlag} 1 ${endX} ${endY}`,
      `L ${innerEndX} ${innerEndY}`,
      `A 52 52 0 ${largeArcFlag} 0 ${innerStartX} ${innerStartY}`,
      'Z',
    ].join(' ')
  }

  return (
    <div className="space-y-10 text-left pb-12 max-w-7xl mx-auto">
      {/* 1. TOP SECTION & CONTRACT IDENTITY STRIP */}
      <div className="space-y-4">
        {/* Compact Contract Identity Strip */}
        <div className="p-3.5 sm:p-4 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex flex-wrap items-center gap-3">
            {/* Demo or Live Badge */}
            {isDemoData ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-sans font-semibold bg-[#15231B] text-[#A8E6BF] border border-[#A8E6BF]/40">
                <span className="w-2 h-2 rounded-full bg-[#A8E6BF] animate-pulse" />
                <span>DEMO — SAMPLE CONTRACT & POLICY</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-sans font-semibold bg-[#15231B] text-[#C5F5D5] border border-[#C5F5D5]/40">
                <span className="w-2 h-2 rounded-full bg-[#C5F5D5]" />
                <span>LIVE AI ANALYSIS</span>
              </span>
            )}

            {/* Contract Name */}
            <div className="flex items-center gap-1.5 font-sans">
              <span className="text-[#8A9B91]">Document:</span>
              <span className="text-[#F2F5F0] font-medium max-w-[220px] truncate">
                {contract?.filename || 'Document Draft'}
              </span>
            </div>

            {/* Policy Source */}
            <div className="flex items-center gap-1.5 font-sans">
              <span className="text-[#8A9B91]">Policy:</span>
              <span className="text-[#A8E6BF] font-medium">
                {isDemoData ? 'Synthetic Benchmark Playbook' : 'Standard Commercial Playbook (v1.0)'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Status */}
            <span
              className={`px-2.5 py-0.5 rounded text-[11px] font-sans font-semibold uppercase ${
                analysis.status === 'completed'
                  ? 'bg-[#15231B] text-[#C5F5D5] border border-[#C5F5D5]/30'
                  : 'bg-[#1F1C10] text-[#FDE047] border border-[#FDE047]/30'
              }`}
            >
              {analysis.status === 'completed' ? 'Analysis Complete' : 'Human Review Needed'}
            </span>

            {/* Mode A CTA if in Demo */}
            {isDemoData && (
              <button
                onClick={onOpenUpload}
                className="px-3.5 py-1 rounded-lg bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-xs font-sans font-semibold transition-all shadow-sm"
              >
                Analyze Your Own Contract →
              </button>
            )}
          </div>
        </div>

        {/* Hero Headline */}
        <div>
          <h1 className="font-editorial text-4xl sm:text-5xl lg:text-6xl font-light text-[#F2F5F0] tracking-tight">
            YOUR CONTRACT. DECODED.
          </h1>
          <p className="font-sans text-base sm:text-lg text-[#8A9B91] mt-1.5 leading-relaxed">
            See what matters, what could go wrong, and what to do next.
          </p>
        </div>
      </div>

      {/* 2. KEY NUMBERS METRIC CARDS (3-4 Meaningful Metrics) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          onClick={() => onNavigateTab('risk')}
          className="p-5 sm:p-6 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] hover:border-[rgba(197,245,213,0.3)] transition-all cursor-pointer group shadow-sm"
        >
          <span className="text-xs font-sans font-medium uppercase tracking-wider text-[#8A9B91]">
            Total Findings
          </span>
          <div className="font-editorial text-4xl sm:text-5xl font-light text-[#F2F5F0] mt-1 group-hover:text-[#C5F5D5] transition-colors">
            {totalFindings}
          </div>
          <p className="text-xs text-[#8A9B91] font-sans mt-2">
            Contract terms evaluated against policy
          </p>
        </div>

        <div
          onClick={() => onNavigateTab('risk')}
          className="p-5 sm:p-6 rounded-2xl bg-[#101512] border border-[#FB923C]/30 hover:border-[#FB923C]/60 transition-all cursor-pointer group shadow-sm"
        >
          <span className="text-xs font-sans font-medium uppercase tracking-wider text-[#FB923C]">
            High Priority Risks
          </span>
          <div className="font-editorial text-4xl sm:text-5xl font-light text-[#FB923C] mt-1">
            {highPriorityTotal}
          </div>
          <p className="text-xs text-[#8A9B91] font-sans mt-2">
            Critical terms needing immediate review
          </p>
        </div>

        <div
          onClick={() => onNavigateTab('evidence')}
          className="p-5 sm:p-6 rounded-2xl bg-[#101512] border border-[#C5F5D5]/30 hover:border-[#C5F5D5]/60 transition-all cursor-pointer group shadow-sm"
        >
          <span className="text-xs font-sans font-medium uppercase tracking-wider text-[#C5F5D5]">
            Evidence-Backed
          </span>
          <div className="font-editorial text-4xl sm:text-5xl font-light text-[#C5F5D5] mt-1">
            {evidenceBackedCount}
          </div>
          <p className="text-xs text-[#8A9B91] font-sans mt-2">
            Exact quotes verified in original text
          </p>
        </div>

        <div
          onClick={() => onNavigateTab('obligations')}
          className="p-5 sm:p-6 rounded-2xl bg-[#101512] border border-[#A8E6BF]/30 hover:border-[#A8E6BF]/60 transition-all cursor-pointer group shadow-sm"
        >
          <span className="text-xs font-sans font-medium uppercase tracking-wider text-[#A8E6BF]">
            Contract Obligations
          </span>
          <div className="font-editorial text-4xl sm:text-5xl font-light text-[#A8E6BF] mt-1">
            {obligationsCount}
          </div>
          <p className="text-xs text-[#8A9B91] font-sans mt-2">
            Operational deadlines and assigned parties
          </p>
        </div>
      </div>

      {/* 3. VISUAL CHARTS SECTION: DOUGHNUT & HORIZONTAL BARS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* CHART 1: Interactive Risk Distribution Doughnut (5 cols) */}
        <div className="lg:col-span-5 p-6 sm:p-7 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] flex flex-col justify-between space-y-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-editorial text-2xl font-light text-[#F2F5F0]">
                Risk Distribution
              </h3>
              <p className="text-xs text-[#8A9B91] font-sans mt-0.5">
                Breakdown of findings by severity
              </p>
            </div>
            <button
              onClick={() => onNavigateTab('risk')}
              className="text-xs font-sans text-[#C5F5D5] hover:underline flex items-center gap-1"
            >
              <span>View All</span>
              <IconArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* SVG Doughnut */}
          <div className="relative flex items-center justify-center my-2">
            <svg viewBox="0 0 200 200" className="w-56 h-56 transform -rotate-90">
              {doughnutSegments.map((seg, idx) => (
                <path
                  key={idx}
                  d={getDoughnutPath(seg.startAngle, seg.endAngle)}
                  fill={seg.color}
                  opacity={selectedChartSegment && selectedChartSegment !== seg.key ? 0.35 : 1}
                  className="transition-all duration-300 cursor-pointer hover:opacity-80"
                  onClick={() =>
                    setSelectedChartSegment(selectedChartSegment === seg.key ? null : seg.key)
                  }
                />
              ))}
            </svg>

            {/* Doughnut Center Metric */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="font-editorial text-4xl font-light text-[#F2F5F0]">
                {selectedChartSegment
                  ? doughnutSegments.find((s) => s.key === selectedChartSegment)?.count || totalFindings
                  : totalFindings}
              </span>
              <span className="text-[11px] font-sans uppercase tracking-wider text-[#8A9B91]">
                {selectedChartSegment
                  ? doughnutSegments.find((s) => s.key === selectedChartSegment)?.label || 'Findings'
                  : 'Total Findings'}
              </span>
            </div>
          </div>

          {/* Doughnut Legend */}
          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-[rgba(197,245,213,0.08)] text-xs font-sans">
            {doughnutSegments.map((seg) => (
              <div
                key={seg.key}
                onClick={() =>
                  setSelectedChartSegment(selectedChartSegment === seg.key ? null : seg.key)
                }
                className={`p-2 rounded-lg cursor-pointer flex items-center justify-between transition-colors ${
                  selectedChartSegment === seg.key ? 'bg-[#080B0A] ring-1 ring-[#C5F5D5]' : 'hover:bg-[#080B0A]'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: seg.color }} />
                  <span className="text-[#8A9B91]">{seg.label}</span>
                </div>
                <span className="font-semibold text-[#F2F5F0]">{seg.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* CHART 2: Top Risk Categories Horizontal Bar Chart (7 cols) */}
        <div className="lg:col-span-7 p-6 sm:p-7 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] flex flex-col justify-between space-y-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-editorial text-2xl font-light text-[#F2F5F0]">
                Top Risk Categories
              </h3>
              <p className="text-xs text-[#8A9B91] font-sans mt-0.5">
                Concentration of findings across commercial contract domains
              </p>
            </div>
          </div>

          {/* Horizontal Bars */}
          <div className="space-y-3 pt-1">
            {Object.entries(CLAUSE_CATEGORIES).map(([catKey, label]) => {
              const count = categoryCounts[catKey] || 0
              const pct = (count / maxCategoryCount) * 100

              return (
                <div
                  key={catKey}
                  onClick={() => onNavigateTab('risk')}
                  className="space-y-1.5 cursor-pointer group"
                >
                  <div className="flex items-center justify-between text-xs font-sans">
                    <span className="text-[#8A9B91] group-hover:text-[#F2F5F0] transition-colors">
                      {label}
                    </span>
                    <span className="font-semibold text-[#F2F5F0]">{count}</span>
                  </div>

                  <div className="w-full h-2 rounded-full bg-[#080B0A] overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${pct}%`,
                        backgroundColor:
                          count >= 2 ? '#FB923C' : count === 1 ? '#FDE047' : 'rgba(197,245,213,0.2)',
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>

          <div className="pt-2 text-xs text-[#8A9B91] font-sans border-t border-[rgba(197,245,213,0.08)] flex items-center justify-between">
            <span>Derived strictly from semantic policy matching against playbook rules.</span>
            <span className="text-[#C5F5D5]">Grounded</span>
          </div>
        </div>
      </div>

      {/* 4. WHAT NEEDS ATTENTION (Top 3 Findings) */}
      <div className="space-y-5">
        <div className="flex items-end justify-between">
          <div>
            <h2 className="font-editorial text-3xl font-light text-[#F2F5F0]">
              WHAT NEEDS ATTENTION
            </h2>
            <p className="text-sm text-[#8A9B91] font-sans mt-1">
              Top contract terms that may conflict with company requirements.
            </p>
          </div>
          <button
            onClick={() => onNavigateTab('risk')}
            className="text-sm font-sans font-medium text-[#C5F5D5] hover:underline flex items-center gap-1.5"
          >
            <span>Explore All Risks</span>
            <IconArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-4">
          {topAttentionFindings.map((finding, idx) => {
            const riskConfig = RISK_LEVELS[finding.risk_level] || RISK_LEVELS.medium
            const categoryLabel =
              CLAUSE_CATEGORIES[finding.clause_category] || finding.clause_category
            const isExpanded = expandedAttentionCard === idx

            return (
              <div
                key={idx}
                className="p-6 sm:p-7 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] hover:border-[rgba(197,245,213,0.25)] transition-all space-y-4 shadow-sm"
              >
                {/* Header: Human-Readable Title & Severity Badge */}
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-sans font-semibold ${riskConfig.badgeClass}`}>
                      {riskConfig.label}
                    </span>
                    <h3 className="font-sans text-lg sm:text-xl font-semibold text-[#F2F5F0]">
                      {categoryLabel} Clause Issue
                    </h3>
                  </div>

                  <button
                    onClick={() =>
                      onNavigateToFinding
                        ? onNavigateToFinding(finding)
                        : onNavigateTab('evidence')
                    }
                    className="px-4 py-1.5 rounded-lg bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-xs font-sans font-semibold flex items-center gap-1.5 transition-all shadow-sm"
                  >
                    <span>View Evidence</span>
                    <IconArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* What We Found (One-Sentence Plain-English) */}
                <div className="space-y-1">
                  <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#C5F5D5]">
                    WHAT WE FOUND
                  </span>
                  <p className="text-base text-[#F2F5F0] font-sans leading-relaxed">
                    {finding.explanation}
                  </p>
                </div>

                {/* Why It Matters */}
                {(finding.applicable_policy_rule?.rule || finding.policy_requirement) && (
                  <div className="space-y-1">
                    <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#8A9B91]">
                      WHY IT MATTERS
                    </span>
                    <p className="text-sm text-[#8A9B91] font-sans leading-relaxed">
                      Company policy requires: {finding.applicable_policy_rule?.rule || finding.policy_requirement}
                    </p>
                  </div>
                )}

                {/* Recommended Action */}
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

                {/* Progressive Disclosure: Technical IDs inside toggle */}
                <div className="pt-2 border-t border-[rgba(197,245,213,0.08)]">
                  <button
                    onClick={() => setExpandedAttentionCard(isExpanded ? null : idx)}
                    className="text-xs font-mono text-[#8A9B91] hover:text-[#C5F5D5] flex items-center gap-1.5 transition-colors"
                  >
                    <span>{isExpanded ? 'Hide Technical Metadata' : 'Show Technical Metadata'}</span>
                    {isExpanded ? <IconChevronUp className="w-3.5 h-3.5" /> : <IconChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {isExpanded && (
                    <div className="mt-3 p-3.5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
                      <div>
                        <span className="text-[#8A9B91]">Clause ID:</span>{' '}
                        <span className="text-[#C5F5D5]">{finding.clause_id || 'Omission'}</span>
                      </div>
                      <div>
                        <span className="text-[#8A9B91]">Policy Rule:</span>{' '}
                        <span className="text-[#A8E6BF]">{finding.policy_id}</span>
                      </div>
                      <div>
                        <span className="text-[#8A9B91]">Page Number:</span>{' '}
                        <span className="text-[#F2F5F0]">{finding.page_number || 'N/A'}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* 5. PRIORITY ACTIONS PANEL (FIX FIRST, REVIEW NEXT, MONITOR) */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-6">
        <div>
          <h2 className="font-editorial text-3xl font-light text-[#F2F5F0]">
            PRIORITY ACTIONS
          </h2>
          <p className="text-sm text-[#8A9B91] font-sans mt-0.5">
            Structured roadmap prioritizing remediation before signing.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Column 1: FIX FIRST */}
          <div className="p-5 rounded-xl bg-[#080B0A] border border-[#FB923C]/30 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-[#FB923C]/20">
              <span className="text-xs font-sans font-bold uppercase tracking-wider text-[#FB923C] flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#FB923C]" />
                <span>FIX FIRST</span>
              </span>
              <span className="text-xs font-mono text-[#FB923C] font-semibold">
                {fixFirstItems.length}
              </span>
            </div>

            <div className="space-y-3">
              {fixFirstItems.slice(0, 2).map((item, i) => (
                <div key={i} className="p-3 rounded-lg bg-[#101512] text-xs font-sans space-y-1.5">
                  <span className="font-semibold text-[#F2F5F0] block">
                    {CLAUSE_CATEGORIES[item.clause_category] || item.clause_category}
                  </span>
                  <p className="text-[#8A9B91] leading-relaxed line-clamp-2">
                    {item.recommended_action || item.explanation}
                  </p>
                </div>
              ))}
              {fixFirstItems.length === 0 && (
                <div className="text-xs text-[#8A9B91] italic">No critical risks flagged.</div>
              )}
            </div>
          </div>

          {/* Column 2: REVIEW NEXT */}
          <div className="p-5 rounded-xl bg-[#080B0A] border border-[#FDE047]/30 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-[#FDE047]/20">
              <span className="text-xs font-sans font-bold uppercase tracking-wider text-[#FDE047] flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#FDE047]" />
                <span>REVIEW NEXT</span>
              </span>
              <span className="text-xs font-mono text-[#FDE047] font-semibold">
                {reviewNextItems.length}
              </span>
            </div>

            <div className="space-y-3">
              {reviewNextItems.slice(0, 2).map((item, i) => (
                <div key={i} className="p-3 rounded-lg bg-[#101512] text-xs font-sans space-y-1.5">
                  <span className="font-semibold text-[#F2F5F0] block">
                    {CLAUSE_CATEGORIES[item.clause_category] || item.clause_category}
                  </span>
                  <p className="text-[#8A9B91] leading-relaxed line-clamp-2">
                    {item.recommended_action || item.explanation}
                  </p>
                </div>
              ))}
              {reviewNextItems.length === 0 && (
                <div className="text-xs text-[#8A9B91] italic">No medium risks flagged.</div>
              )}
            </div>
          </div>

          {/* Column 3: MONITOR */}
          <div className="p-5 rounded-xl bg-[#080B0A] border border-[#C5F5D5]/30 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-[#C5F5D5]/20">
              <span className="text-xs font-sans font-bold uppercase tracking-wider text-[#C5F5D5] flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#C5F5D5]" />
                <span>MONITOR</span>
              </span>
              <span className="text-xs font-mono text-[#C5F5D5] font-semibold">
                {monitorItems.length}
              </span>
            </div>

            <div className="space-y-3">
              {monitorItems.slice(0, 2).map((item, i) => (
                <div key={i} className="p-3 rounded-lg bg-[#101512] text-xs font-sans space-y-1.5">
                  <span className="font-semibold text-[#F2F5F0] block">
                    {item.isObligation ? 'Operational Duty' : (CLAUSE_CATEGORIES[item.clause_category] || 'Standard Clause')}
                  </span>
                  <p className="text-[#8A9B91] leading-relaxed line-clamp-2">
                    {item.recommended_action || item.explanation}
                  </p>
                </div>
              ))}
              {monitorItems.length === 0 && (
                <div className="text-xs text-[#8A9B91] italic">No operational items tracked.</div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 6. TECHNICAL DETAILS ACCORDION */}
      <div className="border border-[rgba(197,245,213,0.1)] rounded-2xl bg-[#101512]/60 overflow-hidden">
        <button
          onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
          className="w-full p-5 flex items-center justify-between text-left hover:bg-[#101512] transition-colors"
        >
          <div className="flex items-center gap-2 text-xs font-mono text-[#8A9B91] uppercase tracking-wider">
            <IconSparkles className="w-4 h-4 text-[#C5F5D5]" />
            <span>Technical System Details & Provenance</span>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono text-[#C5F5D5]">
            <span>{showTechnicalDetails ? 'Collapse' : 'Expand Details'}</span>
            {showTechnicalDetails ? <IconChevronUp className="w-4 h-4" /> : <IconChevronDown className="w-4 h-4" />}
          </div>
        </button>

        {showTechnicalDetails && (
          <div className="p-6 border-t border-[rgba(197,245,213,0.08)] space-y-4 font-mono text-xs bg-[#080B0A]">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-3 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.08)]">
                <span className="text-[#8A9B91]">Analysis ID:</span>
                <div className="text-[#F2F5F0] truncate font-bold mt-1">{analysis.analysis_id}</div>
              </div>
              <div className="p-3 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.08)]">
                <span className="text-[#8A9B91]">Origin:</span>
                <div className="text-[#C5F5D5] font-bold mt-1">{analysis.output_origin}</div>
              </div>
              <div className="p-3 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.08)]">
                <span className="text-[#8A9B91]">Gemini Model:</span>
                <div className="text-[#F2F5F0] font-bold mt-1">{analysis.gemini_model}</div>
              </div>
              <div className="p-3 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.08)]">
                <span className="text-[#8A9B91]">Processing Time:</span>
                <div className="text-[#F2F5F0] font-bold mt-1">{analysis.processing_seconds}s</div>
              </div>
            </div>

            {(warnings.length > 0 || rejections.length > 0) && (
              <div className="space-y-2 pt-2">
                {warnings.map((w, i) => (
                  <div key={i} className="p-3 rounded-xl bg-[#180E10] border border-[#F87171]/20 text-[#F87171]">
                    Warning: {w}
                  </div>
                ))}
                {rejections.length > 0 && (
                  <div className="p-3 rounded-xl bg-[#180E10] border border-[#F87171]/20 text-[#F87171]">
                    {rejections.length} record(s) excluded by evidence verification filter.
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
