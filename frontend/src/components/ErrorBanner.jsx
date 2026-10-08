import React from 'react'
import { IconAlertTriangle, IconX, IconRefresh } from './icons/Icons'

export default function ErrorBanner({ error, onDismiss, onRetry, onLoadDemo }) {
  if (!error) return null

  return (
    <div className="mb-6 p-5 rounded-2xl border border-[#F87171]/40 bg-[#180E10] text-[#F87171] text-left shadow-lg backdrop-blur-md">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 w-8 h-8 rounded-lg bg-[#251013] text-[#F87171] flex items-center justify-center shrink-0 border border-[#F87171]/30">
            <IconAlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-xs font-semibold text-[#F87171]">
                {error.status ? `Backend Error (HTTP ${error.status})` : 'System Notice'}
              </span>
              {error.failedStage && (
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#080B0A] text-[#FB923C] border border-[#FB923C]/30">
                  Stage: {error.failedStage}
                </span>
              )}
              {error.errorCategory && (
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#080B0A] text-[#8A9B91] border border-white/10">
                  Category: {error.errorCategory}
                </span>
              )}
            </div>

            <p className="mt-1.5 text-xs sm:text-sm font-sans text-[#F2F5F0]/90 leading-relaxed">
              {error.message || 'An unexpected issue occurred while communicating with the backend.'}
            </p>

            {error.errorCategory === 'unsupported_evidence' && (
              <p className="mt-2 text-xs text-[#F2F5F0]">
                Your uploaded contract is retained. The AI response could not be grounded in its source clauses.
                Retry only when ready; a retry makes a new AI request. Unsupported findings were excluded.
              </p>
            )}

            {/* Verification Rejections List if present */}
            {error.verificationRejections && error.verificationRejections.length > 0 && (
              <div className="mt-3 p-3 rounded-lg bg-[#080B0A] border border-[#F87171]/30 text-xs font-mono">
                <span className="font-semibold text-[#F87171]">Evidence Verification Exclusions:</span>
                <ul className="mt-1 list-disc list-inside space-y-1 text-[#8A9B91]">
                  {error.verificationRejections.map((rej, idx) => (
                    <li key={idx}>
                      Record {rej.index} ({rej.record_type}): {rej.reason} [{rej.evidence_status}]
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Action buttons */}
            <div className="mt-4 flex flex-wrap items-center gap-3">
              {onRetry && (
                <button
                  onClick={onRetry}
                  className="px-3.5 py-1.5 rounded-lg bg-[#F87171]/20 hover:bg-[#F87171]/30 border border-[#F87171]/40 text-[#F2F5F0] text-xs font-mono flex items-center gap-1.5 transition-colors"
                >
                  <IconRefresh className="w-3.5 h-3.5" />
                  <span>Retry Request</span>
                </button>
              )}
              {onLoadDemo && (
                <button
                  onClick={onLoadDemo}
                  className="px-3.5 py-1.5 rounded-lg border border-[rgba(197,245,213,0.25)] hover:border-[#C5F5D5] bg-[#101512] text-[#C5F5D5] text-xs font-mono transition-colors"
                >
                  Load Offline Demo Dataset
                </button>
              )}
            </div>
          </div>
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-[#8A9B91] hover:text-[#F2F5F0] p-1 rounded-lg hover:bg-white/5"
            title="Dismiss error"
          >
            <IconX className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  )
}
