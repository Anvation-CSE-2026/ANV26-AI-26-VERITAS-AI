import React, { useState, useRef } from 'react'
import {
  IconUpload,
  IconSparkles,
  IconSearch,
  IconCheckCircle,
  IconAlertTriangle,
  IconShield,
} from '../icons/Icons'
import { RISK_LEVELS } from '../../types/constants'

export default function ContractsView({
  contract,
  analysis,
  isDemoData,
  onUploadFile,
  onStartAnalysis,
  isUploading,
  isAnalyzing,
}) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [fileError, setFileError] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedClauseId, setSelectedClauseId] = useState(null)
  const [showPlaybookDetails, setShowPlaybookDetails] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const validateAndSetFile = (file) => {
    setFileError(null)
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setFileError('Invalid file type. Only PDF documents (.pdf) are supported.')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setFileError('File exceeds 10 MB limit. Please select a smaller contract PDF.')
      return
    }

    setSelectedFile(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0])
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0])
    }
  }

  const handleUploadSubmit = async () => {
    if (!selectedFile) return
    await onUploadFile(selectedFile)
    setSelectedFile(null)
  }

  const clauses = contract?.clauses || []
  const pages = contract?.pages || []

  // Map each clause_id to its finding(s)
  const clauseFindingsMap = React.useMemo(() => {
    const map = new Map()
    const list = analysis?.findings || []
    list.forEach((f) => {
      const cid = f.clause_id || f.source_facts?.clause_id
      if (cid) {
        if (!map.has(cid)) map.set(cid, [])
        map.get(cid).push(f)
      }
    })
    return map
  }, [analysis?.findings])

  const filteredClauses = clauses.filter((c) => {
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      c.clause_id.toLowerCase().includes(q) ||
      c.text.toLowerCase().includes(q) ||
      `page ${c.page_number}`.includes(q)
    )
  })

  // Selected clause defaults to first filtered clause if none active
  const activeClause =
    clauses.find((c) => c.clause_id === selectedClauseId) ||
    filteredClauses[0] ||
    clauses[0]

  const activeFindings = activeClause ? clauseFindingsMap.get(activeClause.clause_id) || [] : []
  const primaryFinding = activeFindings[0]

  // Severity color mapping
  const getRiskDotColor = (clauseId) => {
    const clauseFindings = clauseFindingsMap.get(clauseId)
    if (!clauseFindings || clauseFindings.length === 0) {
      return 'bg-[#C5F5D5]/40' // Compliant / no risk detected
    }
    const highestRisk = clauseFindings.reduce((highest, curr) => {
      const order = { critical: 4, high: 3, medium: 2, low: 1 }
      const currVal = order[curr.risk_level?.toLowerCase()] || 0
      const highVal = order[highest?.risk_level?.toLowerCase()] || 0
      return currVal > highVal ? curr : highest
    }, clauseFindings[0])

    const level = highestRisk.risk_level?.toLowerCase()
    if (level === 'critical') return 'bg-[#F87171]'
    if (level === 'high') return 'bg-[#FB923C]'
    if (level === 'medium') return 'bg-[#FDE047]'
    return 'bg-[#C5F5D5]'
  }

  return (
    <div className="space-y-10 text-left pb-12">
      {/* 1. UPLOAD & POLICY PLAYBOOK CONFIGURATION */}
      <div className="p-8 sm:p-10 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-6">
        <div>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="font-editorial text-4xl sm:text-5xl font-light text-[#F2F5F0]">
                CONTRACT ANALYSIS WORKSPACE.
              </h1>
              <p className="font-sans text-base sm:text-lg text-[#8A9B91] mt-2 leading-relaxed">
                Upload your commercial PDF agreement to evaluate clauses against enterprise policy standards.
              </p>
            </div>

            {/* Playbook Badge & Inspector */}
            <div className="text-right">
              <button
                onClick={() => setShowPlaybookDetails(!showPlaybookDetails)}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#080B0A] border border-[rgba(197,245,213,0.2)] text-xs text-[#C5F5D5] hover:border-[#C5F5D5] transition-all"
                title="Click to view policy rules"
              >
                <IconShield className="w-3.5 h-3.5 text-[#C5F5D5]" />
                <span>Policy: Standard Commercial v1.0</span>
                <span className="text-[10px] text-[#8A9B91]">({showPlaybookDetails ? 'Hide' : 'Inspect'})</span>
              </button>
            </div>
          </div>

          {/* Collapsible Playbook Details */}
          {showPlaybookDetails && (
            <div className="mt-4 p-5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.15)] text-xs text-[#8A9B91] space-y-3 font-sans animate-fadeIn">
              <div className="flex items-center justify-between text-[#C5F5D5] font-semibold">
                <span>Built-in Evaluation Rules (7 Commercial Areas)</span>
                <span className="font-mono text-[11px]">sample-company-policy v1.0</span>
              </div>
              <p className="text-[#F2F5F0]">
                Every contract is objectively checked against these seven non-negotiable standards:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 pt-1">
                <div className="p-2.5 rounded bg-[#101512] border border-white/5">
                  <strong className="text-[#C5F5D5] block">1. Liability Caps</strong>
                  Must equal 12-month fees. Data & IP breach carve-outs required.
                </div>
                <div className="p-2.5 rounded bg-[#101512] border border-white/5">
                  <strong className="text-[#C5F5D5] block">2. Indemnification</strong>
                  Supplier must defend IP claims. No unlimited indemnity for company.
                </div>
                <div className="p-2.5 rounded bg-[#101512] border border-white/5">
                  <strong className="text-[#C5F5D5] block">3. Termination</strong>
                  Termination for convenience on max 30 days notice with zero penalties.
                </div>
                <div className="p-2.5 rounded bg-[#101512] border border-white/5">
                  <strong className="text-[#C5F5D5] block">4. Confidentiality</strong>
                  Mutual protection surviving at least 3 years post-termination.
                </div>
                <div className="p-2.5 rounded bg-[#101512] border border-white/5">
                  <strong className="text-[#C5F5D5] block">5. Payment Terms</strong>
                  Net 30 days minimum. Right to withhold disputed amounts in good faith.
                </div>
                <div className="p-2.5 rounded bg-[#101512] border border-white/5">
                  <strong className="text-[#C5F5D5] block">6. Data Protection</strong>
                  48-hour security breach notification & 30-day data return/deletion.
                </div>
                <div className="p-2.5 rounded bg-[#101512] border border-white/5">
                  <strong className="text-[#C5F5D5] block">7. Intellectual Property</strong>
                  Bespoke deliverables owned by Company or perpetual license.
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Drag and Drop Upload Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 sm:p-10 text-center cursor-pointer transition-all ${
            dragActive
              ? 'border-[#C5F5D5] bg-[#15231B]'
              : 'border-[rgba(197,245,213,0.2)] hover:border-[#C5F5D5] bg-[#080B0A]'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            className="hidden"
            onChange={handleFileChange}
          />
          <div className="w-14 h-14 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.15)] text-[#C5F5D5] flex items-center justify-center mx-auto mb-3">
            <IconUpload className="w-7 h-7" />
          </div>

          <p className="text-base sm:text-lg font-sans font-medium text-[#F2F5F0]">
            {selectedFile ? selectedFile.name : 'Select or drag and drop your contract PDF here'}
          </p>

          <p className="text-xs sm:text-sm text-[#8A9B91] mt-1.5 font-sans">
            Searchable PDF format · Max 10 MB · Up to 30 pages
          </p>

          {selectedFile && (
            <div className="mt-3 inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#101512] text-xs text-[#C5F5D5] font-sans border border-[#C5F5D5]/30">
              <IconCheckCircle className="w-3.5 h-3.5 text-[#C5F5D5]" />
              <span>{(selectedFile.size / 1024).toFixed(1)} KB selected and ready to extract</span>
            </div>
          )}
        </div>

        {fileError && (
          <div className="p-4 rounded-xl bg-[#180E10] border border-[#F87171]/40 text-sm text-[#F87171] flex items-center gap-2 font-sans">
            <IconAlertTriangle className="w-5 h-5 text-[#F87171] shrink-0" />
            <span>{fileError}</span>
          </div>
        )}

        {/* Upload Status & Action Buttons */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-1">
          <div className="text-xs sm:text-sm font-sans text-[#8A9B91]">
            {isUploading ? (
              <span className="text-[#C5F5D5] animate-pulse">Extracting text & clause structure on backend...</span>
            ) : selectedFile ? (
              <span className="text-[#C5F5D5]">Ready to upload and parse</span>
            ) : isDemoData ? (
              <span>Currently previewing synthetic demo contract. Upload your PDF above to analyze your own.</span>
            ) : contract ? (
              <span>Contract parsed and ready for live analysis.</span>
            ) : (
              <span>Upload a PDF contract to begin.</span>
            )}
          </div>

          <div className="flex items-center gap-3">
            {selectedFile && (
              <button
                onClick={handleUploadSubmit}
                disabled={isUploading}
                className="px-6 py-2.5 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-sm font-sans font-semibold flex items-center gap-2 transition-all disabled:opacity-50 shadow-md shadow-[#C5F5D5]/10"
              >
                {isUploading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-[#080B0A] border-t-transparent rounded-full animate-spin" />
                    <span>Extracting PDF...</span>
                  </>
                ) : (
                  <>
                    <IconUpload className="w-4 h-4" />
                    <span>Upload & Extract</span>
                  </>
                )}
              </button>
            )}

            {contract && !isDemoData && (
              <button
                onClick={() => onStartAnalysis(contract.contract_id)}
                disabled={isAnalyzing}
                className="px-6 py-2.5 rounded-full bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-sm font-sans font-bold flex items-center gap-2 transition-all shadow-lg shadow-[#C5F5D5]/15 disabled:opacity-50"
              >
                <IconSparkles className="w-4 h-4 text-[#080B0A]" />
                <span>Run Live AI Analysis</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 2. CONTRACT DETAILS & DOCUMENT EXPLORER */}
      {contract ? (
        <div className="space-y-6">
          {/* Contract Metadata Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)]">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono text-[#8A9B91] uppercase tracking-wider">
                  ACTIVE CONTRACT
                </span>
                {isDemoData && (
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#101512] text-[#A8E6BF] border border-[#A8E6BF]/30">
                    DEMO DATA
                  </span>
                )}
              </div>
              <h2 className="font-editorial text-3xl font-light text-[#F2F5F0]">
                {contract.filename}
              </h2>
              <div className="text-xs sm:text-sm font-sans text-[#8A9B91] mt-2 flex flex-wrap items-center gap-3">
                <span className="font-medium text-[#C5F5D5]">{pages.length} Pages</span>
                <span>·</span>
                <span className="font-medium text-[#A8E6BF]">{clauses.length} Extracted Clauses</span>
                <span>·</span>
                <span className="text-[#8A9B91]">{(analysis?.findings?.length || 0)} Evaluated Findings</span>
                {contract.warnings?.length > 0 && (
                  <>
                    <span>·</span>
                    <span className="text-[#FDE047]">{contract.warnings.length} extraction warnings</span>
                  </>
                )}
              </div>
            </div>

            {/* Searchable Clause Filter */}
            <div className="relative">
              <input
                type="text"
                placeholder="Search clauses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-[#080B0A] border border-[rgba(197,245,213,0.2)] rounded-xl px-4 py-2.5 text-sm text-[#F2F5F0] placeholder-[#8A9B91] focus:outline-none focus:border-[#C5F5D5] w-64 font-sans"
              />
              <IconSearch className="w-4 h-4 text-[#8A9B91] absolute right-3.5 top-3 pointer-events-none" />
            </div>
          </div>

          {/* TWO-COLUMN DOCUMENT EXPLORER */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* LEFT: Clause Outline Index (5 cols) */}
            <div className="lg:col-span-5 p-6 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-[rgba(197,245,213,0.08)]">
                <div>
                  <h3 className="font-sans text-base font-semibold text-[#F2F5F0]">
                    Clause Outline
                  </h3>
                  <p className="text-[11px] text-[#8A9B91]">
                    Colored indicators indicate detected risk severity
                  </p>
                </div>
                <span className="text-xs font-mono text-[#8A9B91]">
                  {filteredClauses.length} clauses
                </span>
              </div>

              <div className="space-y-2 max-h-[640px] overflow-y-auto pr-1">
                {filteredClauses.map((c) => {
                  const isSelected = activeClause?.clause_id === c.clause_id
                  const dotColor = getRiskDotColor(c.clause_id)
                  const hasRisk = clauseFindingsMap.has(c.clause_id)

                  return (
                    <div
                      key={c.clause_id}
                      onClick={() => setSelectedClauseId(c.clause_id)}
                      className={`p-3.5 rounded-xl text-left cursor-pointer transition-all border ${
                        isSelected
                          ? 'bg-[#15231B] border-[#C5F5D5] shadow-md ring-1 ring-[#C5F5D5]/30'
                          : 'bg-[#080B0A] border-[rgba(197,245,213,0.08)] hover:border-[rgba(197,245,213,0.25)]'
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs font-mono mb-1">
                        <div className="flex items-center gap-2">
                          <span
                            className={`w-2.5 h-2.5 rounded-full ${dotColor} shrink-0`}
                            title={hasRisk ? 'Risk detected' : 'Standard/Compliant'}
                          />
                          <span className={`font-bold ${isSelected ? 'text-[#C5F5D5]' : 'text-[#8A9B91]'}`}>
                            {c.clause_id}
                          </span>
                        </div>
                        <span className="text-[#8A9B91] text-[11px]">P.{c.page_number}</span>
                      </div>
                      <p className="text-xs font-sans text-[#F2F5F0]/90 line-clamp-2 leading-relaxed pl-4.5">
                        {c.text}
                      </p>
                    </div>
                  )
                })}

                {filteredClauses.length === 0 && (
                  <div className="text-center py-12 text-[#8A9B91] text-sm font-sans">
                    No clauses matched your search query.
                  </div>
                )}
              </div>
            </div>

            {/* RIGHT: Document Reader & Risk Callout (7 cols) */}
            <div className="lg:col-span-7 p-6 sm:p-8 rounded-2xl bg-[#101512] border border-[rgba(197,245,213,0.12)] space-y-6 flex flex-col justify-between">
              {activeClause ? (
                <div className="space-y-6">
                  {/* Selected Clause Header */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-[rgba(197,245,213,0.1)]">
                    <div>
                      <div className="text-xs font-mono text-[#8A9B91] uppercase tracking-wider">
                        DOCUMENT READER
                      </div>
                      <h3 className="font-editorial text-2xl sm:text-3xl font-light text-[#C5F5D5] mt-1">
                        {activeClause.clause_id}
                      </h3>
                    </div>

                    <div className="px-3 py-1 rounded-full bg-[#080B0A] border border-[rgba(197,245,213,0.15)] text-xs font-mono text-[#8A9B91]">
                      Page {activeClause.page_number} · Characters {activeClause.start_offset}–{activeClause.end_offset}
                    </div>
                  </div>

                  {/* Clause Text in Readable Typography */}
                  <div className="space-y-2">
                    <span className="text-xs font-sans font-semibold uppercase tracking-wider text-[#8A9B91]">
                      ORIGINAL CLAUSE TEXT
                    </span>
                    <div
                      className={`p-6 rounded-2xl bg-[#080B0A] border text-[#F2F5F0] font-sans text-base sm:text-lg leading-relaxed whitespace-pre-wrap ${
                        primaryFinding
                          ? primaryFinding.risk_level === 'critical'
                            ? 'border-[#F87171]/40'
                            : primaryFinding.risk_level === 'high'
                            ? 'border-[#FB923C]/40'
                            : primaryFinding.risk_level === 'medium'
                            ? 'border-[#FDE047]/40'
                            : 'border-[#C5F5D5]/40'
                          : 'border-[rgba(197,245,213,0.1)]'
                      }`}
                    >
                      {activeClause.text}
                    </div>
                  </div>

                  {/* Risk Callout Card or Compliant Notice */}
                  {primaryFinding ? (
                    <div className="p-6 rounded-2xl bg-[#080B0A] border border-[rgba(197,245,213,0.18)] space-y-4">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <IconAlertTriangle
                            className={`w-4 h-4 ${
                              primaryFinding.risk_level === 'critical'
                                ? 'text-[#F87171]'
                                : primaryFinding.risk_level === 'high'
                                ? 'text-[#FB923C]'
                                : primaryFinding.risk_level === 'medium'
                                ? 'text-[#FDE047]'
                                : 'text-[#C5F5D5]'
                            }`}
                          />
                          <span className="font-sans font-semibold text-sm text-[#F2F5F0]">
                            Identified Policy Deviation
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <span
                            className={`text-xs px-2.5 py-0.5 rounded-full font-mono font-medium ${
                              RISK_LEVELS[primaryFinding.risk_level?.toLowerCase()]?.badgeClass ||
                              'text-[#C5F5D5] bg-[#101512] border border-[#C5F5D5]/30'
                            }`}
                          >
                            {RISK_LEVELS[primaryFinding.risk_level?.toLowerCase()]?.label || primaryFinding.risk_level}
                          </span>
                          <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-[#101512] text-[#8A9B91] border border-white/10 uppercase">
                            {primaryFinding.clause_category || 'general'}
                          </span>
                        </div>
                      </div>

                      {/* Plain-English Explanation */}
                      <div className="space-y-1">
                        <span className="text-[11px] font-mono text-[#8A9B91] uppercase tracking-wider block">
                          WHAT VERITAS AI FOUND HERE
                        </span>
                        <p className="text-sm font-sans text-[#F2F5F0] leading-relaxed">
                          {primaryFinding.explanation}
                        </p>
                      </div>

                      {/* Policy Rule Conflict */}
                      {(primaryFinding.policy_requirement || primaryFinding.applicable_policy_rule?.rule) && (
                        <div className="p-3.5 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.1)] space-y-1">
                          <span className="text-[11px] font-mono text-[#C5F5D5] uppercase tracking-wider block">
                            POLICY RULE IN CONFLICT
                          </span>
                          <p className="text-xs font-sans text-[#8A9B91] leading-relaxed">
                            {primaryFinding.policy_requirement || primaryFinding.applicable_policy_rule?.rule}
                          </p>
                        </div>
                      )}

                      {/* Recommended Action */}
                      {primaryFinding.recommended_action && (
                        <div className="p-3.5 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.1)] space-y-1">
                          <span className="text-[11px] font-mono text-[#A8E6BF] uppercase tracking-wider block">
                            RECOMMENDED ACTION
                          </span>
                          <p className="text-xs font-sans text-[#F2F5F0] leading-relaxed">
                            {primaryFinding.recommended_action}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="p-5 rounded-2xl bg-[#080B0A] border border-[#C5F5D5]/20 flex items-center gap-3.5 text-xs font-sans text-[#8A9B91]">
                      <IconCheckCircle className="w-5 h-5 text-[#C5F5D5] shrink-0" />
                      <div>
                        <strong className="text-[#C5F5D5] block font-medium">Complies with Standard Policies</strong>
                        <span>No contractual deviation or elevated risk detected in this clause.</span>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-24 text-[#8A9B91] text-sm font-sans">
                  Select a clause from the outline on the left to inspect its content and policy alignment.
                </div>
              )}

              {/* Action Hint */}
              <div className="pt-4 border-t border-[rgba(197,245,213,0.08)] flex items-center justify-between text-xs text-[#8A9B91]">
                <span>Extracted text preserved verbatim from source document.</span>
                <span className="font-mono text-[#A8E6BF]">Source Grounded</span>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}
