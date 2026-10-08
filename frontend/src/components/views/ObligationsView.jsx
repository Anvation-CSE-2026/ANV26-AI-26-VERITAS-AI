import React, { useState } from 'react'
import {
  IconClock,
  IconSearch,
  IconChevronDown,
  IconChevronUp,
} from '../icons/Icons'
import { DEADLINE_TYPES } from '../../types/constants'

export default function ObligationsView({
  obligations = [],
  onOpenUpload,
  onLoadDemo,
}) {
  const [viewMode, setViewMode] = useState('party') // 'party' or 'timeline'
  const [filterParty, setFilterParty] = useState('all')
  const [filterDeadlineType, setFilterDeadlineType] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedIndices, setExpandedIndices] = useState(new Set())

  if (!obligations || obligations.length === 0) {
    return (
      <div className="p-16 text-center rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] text-[#8A9B91] space-y-4 max-w-xl mx-auto my-12">
        <IconClock className="w-12 h-12 mx-auto text-[#C5F5D5] opacity-40" />
        <h4 className="font-editorial text-3xl font-light text-[#F2F5F0]">
          No Contract Obligations Extracted
        </h4>
        <p className="text-sm font-sans text-[#8A9B91] leading-relaxed">
          Upload an agreement or load the demo dataset to review responsibilities, deadlines, and action items.
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

  // Unique parties
  const parties = Array.from(
    new Set(obligations.map((o) => o.responsible_party || 'Unspecified'))
  )

  const toggleExpand = (idx) => {
    const next = new Set(expandedIndices)
    if (next.has(idx)) {
      next.delete(idx)
    } else {
      next.add(idx)
    }
    setExpandedIndices(next)
  }

  const filteredObligations = obligations.filter((o) => {
    const party = o.responsible_party || 'Unspecified'
    if (filterParty !== 'all' && party !== filterParty) return false
    if (filterDeadlineType !== 'all' && o.deadline_type !== filterDeadlineType) return false
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      return (
        o.description.toLowerCase().includes(q) ||
        (o.responsible_party && o.responsible_party.toLowerCase().includes(q)) ||
        (o.deadline && o.deadline.toLowerCase().includes(q)) ||
        (o.clause_id && o.clause_id.toLowerCase().includes(q)) ||
        (o.evidence_quote && o.evidence_quote.toLowerCase().includes(q))
      )
    }
    return true
  })

  return (
    <div className="space-y-10 text-left pb-12">
      {/* 1. HEADER & VIEW MODE SWITCHER */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="font-editorial text-4xl sm:text-5xl lg:text-6xl font-light text-[#F2F5F0]">
            WHAT NEEDS TO BE DONE?
          </h1>
          <p className="font-sans text-base sm:text-lg text-[#8A9B91] mt-2 leading-relaxed max-w-3xl">
            Track contractual responsibilities, relative timelines, and operational commitments.
          </p>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center p-1 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] gap-1">
          <button
            onClick={() => setViewMode('party')}
            className={`px-4 py-2 rounded-xl text-xs font-sans font-semibold transition-all ${
              viewMode === 'party'
                ? 'bg-[#15231B] text-[#C5F5D5] shadow-sm border border-[#C5F5D5]/30'
                : 'text-[#8A9B91] hover:text-[#F2F5F0]'
            }`}
          >
            BY RESPONSIBLE PARTY
          </button>
          <button
            onClick={() => setViewMode('timeline')}
            className={`px-4 py-2 rounded-xl text-xs font-sans font-semibold transition-all ${
              viewMode === 'timeline'
                ? 'bg-[#15231B] text-[#C5F5D5] shadow-sm border border-[#C5F5D5]/30'
                : 'text-[#8A9B91] hover:text-[#F2F5F0]'
            }`}
          >
            SEQUENTIAL TIMELINE
          </button>
        </div>
      </div>

      {/* 2. FILTER & SEARCH CONTROLS */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          {/* Party Filter */}
          <select
            value={filterParty}
            onChange={(e) => setFilterParty(e.target.value)}
            className="bg-[#101512] border border-[rgba(197,245,213,0.15)] text-[#F2F5F0] text-xs font-sans rounded-full px-4 py-2 focus:outline-none focus:border-[#C5F5D5]"
          >
            <option value="all">All Responsible Parties</option>
            {parties.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>

          {/* Deadline Type Filter */}
          <select
            value={filterDeadlineType}
            onChange={(e) => setFilterDeadlineType(e.target.value)}
            className="bg-[#101512] border border-[rgba(197,245,213,0.15)] text-[#F2F5F0] text-xs font-sans rounded-full px-4 py-2 focus:outline-none focus:border-[#C5F5D5]"
          >
            <option value="all">All Deadline Types</option>
            <option value="fixed_date">Fixed Date</option>
            <option value="relative">Relative Timeline</option>
            <option value="ambiguous">Ambiguous</option>
            <option value="unspecified">Unspecified</option>
          </select>
        </div>

        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search obligations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-[#101512] border border-[rgba(197,245,213,0.15)] rounded-full px-4 py-2 text-xs text-[#F2F5F0] placeholder-[#8A9B91] focus:outline-none focus:border-[#C5F5D5] w-56 font-sans"
          />
          <IconSearch className="w-3.5 h-3.5 text-[#8A9B91] absolute right-3.5 top-2.5 pointer-events-none" />
        </div>
      </div>

      {/* 3. OBLIGATION TASK CARDS */}
      {viewMode === 'party' ? (
        <div className="space-y-10">
          {parties
            .filter((p) => filterParty === 'all' || p === filterParty)
            .map((partyName) => {
              const partyObs = filteredObligations.filter(
                (o) => (o.responsible_party || 'Unspecified') === partyName
              )
              if (partyObs.length === 0) return null

              return (
                <div key={partyName} className="space-y-4">
                  <div className="flex items-center justify-between pb-2 border-b border-[rgba(197,245,213,0.1)]">
                    <div className="flex items-center gap-2.5">
                      <span className="w-3 h-3 rounded-full bg-[#C5F5D5]" />
                      <h2 className="font-editorial text-2xl font-light text-[#F2F5F0]">
                        {partyName}
                      </h2>
                    </div>
                    <span className="text-xs font-mono text-[#8A9B91]">
                      {partyObs.length} action item{partyObs.length > 1 ? 's' : ''}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {partyObs.map((ob, idx) => {
                      const dlConfig = DEADLINE_TYPES[ob.deadline_type] || DEADLINE_TYPES.unspecified
                      const globalIdx = obligations.indexOf(ob)
                      const isExpanded = expandedIndices.has(globalIdx)

                      return (
                        <div
                          key={idx}
                          className="p-6 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] hover:border-[rgba(197,245,213,0.25)] transition-all flex flex-col justify-between space-y-5 shadow-sm"
                        >
                          <div className="space-y-4">
                            <div className="flex items-center justify-between gap-2">
                              <span className={`px-3 py-1 rounded-full text-xs font-sans font-semibold ${dlConfig.badgeClass}`}>
                                {dlConfig.label}
                              </span>
                              <span className="text-xs font-mono text-[#8A9B91]">
                                Clause {ob.clause_id} · P{ob.page_number}
                              </span>
                            </div>

                            <div className="space-y-1">
                              <span className="text-[11px] font-sans font-semibold uppercase tracking-wider text-[#A8E6BF]">
                                WHAT?
                              </span>
                              <h3 className="font-sans text-base font-medium text-[#F2F5F0] leading-snug">
                                {ob.description}
                              </h3>
                            </div>

                            <div className="p-4 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] space-y-2 text-xs font-sans">
                              <div>
                                <span className="text-[#8A9B91] font-semibold text-[10px] uppercase tracking-wider block">
                                  TIMING / DEADLINE
                                </span>
                                <span className="text-sm font-medium text-[#C5F5D5] mt-0.5 block">
                                  {ob.deadline || 'Unspecified timing condition'}
                                </span>
                              </div>
                            </div>

                            <div className="space-y-1 pt-1">
                              <span className="text-[11px] font-sans font-semibold uppercase tracking-wider text-[#8A9B91]">
                                SOURCE
                              </span>
                              <div className="text-xs font-mono text-[#8A9B91]">
                                Extracted from Clause {ob.clause_id} on Page {ob.page_number}
                              </div>
                            </div>
                          </div>

                          <div className="pt-3 border-t border-[rgba(197,245,213,0.08)]">
                            <button
                              onClick={() => toggleExpand(globalIdx)}
                              className="text-xs font-sans text-[#8A9B91] hover:text-[#C5F5D5] flex items-center justify-between w-full transition-colors"
                            >
                              <span>{isExpanded ? 'Hide Quoted Clause' : 'View Quoted Clause'}</span>
                              {isExpanded ? (
                                <IconChevronUp className="w-3.5 h-3.5" />
                              ) : (
                                <IconChevronDown className="w-3.5 h-3.5" />
                              )}
                            </button>

                            {isExpanded && (
                              <div className="mt-3 p-3.5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] font-editorial italic text-xs text-[#C5F5D5] leading-relaxed">
                                "{ob.evidence_quote}"
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
        </div>
      ) : (
        <div className="space-y-6 relative border-l-2 border-[rgba(197,245,213,0.2)] ml-4 pl-6">
          {filteredObligations.map((ob, idx) => {
            const dlConfig = DEADLINE_TYPES[ob.deadline_type] || DEADLINE_TYPES.unspecified

            return (
              <div key={idx} className="relative group">
                <span className="absolute -left-[31px] top-4 w-3.5 h-3.5 rounded-full bg-[#C5F5D5] border-2 border-[#080B0A]" />
                <div className="p-6 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <span className={`px-3 py-1 rounded-full text-xs font-sans font-semibold ${dlConfig.badgeClass}`}>
                        {dlConfig.label}
                      </span>
                      <span className="text-xs font-mono font-medium text-[#C5F5D5]">
                        {ob.deadline || 'Timing unspecified'}
                      </span>
                    </div>
                    <span className="text-xs font-mono text-[#8A9B91]">
                      Duty assigned to <strong className="text-[#F2F5F0]">{ob.responsible_party || 'Unspecified'}</strong>
                    </span>
                  </div>

                  <p className="text-base font-sans text-[#F2F5F0]">
                    {ob.description}
                  </p>

                  <div className="text-xs font-mono text-[#8A9B91] pt-1">
                    Clause {ob.clause_id} · Page {ob.page_number}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {filteredObligations.length === 0 && (
        <div className="p-12 text-center text-[#8A9B91] text-sm font-sans rounded-2xl border border-[rgba(197,245,213,0.12)] bg-[#101512]">
          No obligations match the selected filter criteria.
        </div>
      )}
    </div>
  )
}
