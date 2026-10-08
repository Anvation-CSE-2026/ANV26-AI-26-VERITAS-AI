import React, { useEffect, useState } from 'react'
import { ANALYSIS_STAGES } from '../types/constants'
import { IconSparkles, IconClock } from './icons/Icons'

export default function AnalysisProgressModal({ isOpen, onCancel }) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0)

  useEffect(() => {
    if (!isOpen) return

    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1)
    }, 1000)

    return () => {
      clearInterval(timer)
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#080B0A]/85 backdrop-blur-md">
      <div className="bg-[#101512] border border-[rgba(197,245,213,0.18)] rounded-2xl max-w-xl w-full p-6 sm:p-8 shadow-2xl relative text-left text-[#F2F5F0]">
        {/* Header */}
        <div className="flex items-center justify-between pb-6 border-b border-[rgba(197,245,213,0.1)]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.15)] text-[#C5F5D5] flex items-center justify-center">
              <IconSparkles className="w-5 h-5 animate-pulse text-[#C5F5D5]" />
            </div>
            <div>
              <h3 className="font-editorial text-2xl text-[#F2F5F0]">Analyzing Contract</h3>
              <p className="text-xs font-mono text-[#8A9B91]">Live reasoning & deterministic verification</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#080B0A] border border-[rgba(197,245,213,0.15)] text-xs font-mono text-[#C5F5D5]">
            <IconClock className="w-3.5 h-3.5" />
            <span>{elapsedSeconds}s elapsed</span>
          </div>
        </div>

        {/* Informative Note */}
        <div className="mt-4 p-3.5 rounded-xl bg-[#080B0A] border border-[rgba(197,245,213,0.08)] text-xs text-[#8A9B91] font-sans">
          <span className="font-semibold text-[#C5F5D5]">Auditable Pipeline:</span> Deep semantic analysis against your corporate playbook with Gemini reasoning and Ollama vector retrieval. Quoted evidence is checked against extracted text; potential omissions require review. Pipeline steps below are informational; the server does not stream stage completion.
        </div>

        {/* Clear Stages List (No fake percentage) */}
        <div className="mt-6 space-y-3">
          {ANALYSIS_STAGES.map((stage, idx) => (
            <div key={stage.id} className="p-3.5 rounded-xl border border-white/10 bg-[#080B0A] flex items-start gap-3">
              <span className="text-[#C5F5D5] font-mono text-xs">{idx + 1}</span>
              <div><h4 className="text-sm text-[#F2F5F0]">{stage.label}</h4><p className="text-xs text-[#8A9B91] mt-0.5">{stage.detail}</p></div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-8 pt-4 border-t border-[rgba(197,245,213,0.08)] flex items-center justify-between text-xs font-mono text-[#8A9B91]">
          <span>Waiting for server response — duration varies</span>
          {onCancel && (
            <button
              onClick={onCancel}
              className="text-[#8A9B91] hover:text-[#F2F5F0] px-3 py-1.5 rounded-lg border border-white/10 hover:border-white/20"
            >
              Cancel Request
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
