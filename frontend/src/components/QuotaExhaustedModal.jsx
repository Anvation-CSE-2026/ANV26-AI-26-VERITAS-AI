import React from 'react'
import { useAuth } from '../context/useAuth'
import { IconX, IconSparkles } from './icons/Icons'

export default function QuotaExhaustedModal() {
  const { quotaModal, closeQuotaModal, initiateCheckout, checkoutLoading, subscription } = useAuth()
  const { isOpen, data } = quotaModal

  if (!isOpen) return null

  const used = data?.analysesUsed ?? subscription?.analyses_used ?? 10
  const limit = data?.analysesLimit ?? subscription?.analyses_limit ?? 10
  const currentPlan = subscription?.plan === 'pro' ? 'Pro' : 'Standard'

  const handleUpgrade = async () => {
    try {
      await initiateCheckout('pro')
      closeQuotaModal()
    } catch {
      // Handled via toast in AuthContext
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#080B0A]/85 backdrop-blur-xl animate-fade-in">
      <div
        className="relative w-full max-w-lg bg-[#0E1411] border border-[rgba(197,245,213,0.3)] rounded-3xl shadow-2xl overflow-hidden text-[#F2F5F0] p-8 sm:p-10"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#C5F5D5]/10 rounded-full blur-3xl pointer-events-none" />

        {/* Close Button */}
        <button
          onClick={closeQuotaModal}
          className="absolute top-6 right-6 p-2 text-[#8A9B91] hover:text-[#F2F5F0] rounded-lg hover:bg-[#151D18] transition-colors"
        >
          <IconX className="w-5 h-5" />
        </button>

        {/* Header Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-mono tracking-wider bg-[#F87171]/20 text-[#F87171] border border-[#F87171]/30 mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-[#F87171] animate-pulse" />
          <span>MONTHLY QUOTA LIMIT REACHED</span>
        </div>

        {/* Title */}
        <h2 className="font-editorial text-3xl sm:text-4xl text-[#C5F5D5] leading-tight mb-4">
          YOU'VE USED ALL YOUR ANALYSES
        </h2>

        {/* Explanatory Text */}
        <div className="space-y-3 font-sans text-sm text-[#8A9B91] font-light leading-relaxed mb-8">
          <p>
            Your <span className="font-semibold text-[#F2F5F0]">{currentPlan}</span> plan includes{' '}
            <span className="font-mono text-[#C5F5D5] font-semibold">{limit}</span> contract analyses per month.
            You have analyzed <span className="font-mono text-[#F87171] font-semibold">{used}</span> documents in the current cycle.
          </p>
          <p>
            Upgrade to <span className="text-[#C5F5D5] font-semibold">Pro</span> to immediately unlock{' '}
            <span className="font-mono text-[#C5F5D5] font-semibold">30 analyses per month</span>, full network knowledge graphs, and extended audit history.
          </p>
        </div>

        {/* Feature comparison mini-box */}
        <div className="p-4 rounded-xl border border-[rgba(197,245,213,0.15)] bg-[#101613] text-xs font-mono text-[#8A9B91] space-y-2 mb-8">
          <div className="flex justify-between text-[#F2F5F0]">
            <span>Pro Capacity:</span>
            <span className="text-[#C5F5D5] font-semibold">30 analyses / month</span>
          </div>
          <div className="flex justify-between text-[#F2F5F0]">
            <span>Network Knowledge Graph:</span>
            <span className="text-[#C5F5D5] font-semibold">Enabled</span>
          </div>
          <div className="flex justify-between text-[#F2F5F0]">
            <span>Subscription Rate:</span>
            <span className="text-[#C5F5D5] font-semibold">₹299 / month</span>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <button
            onClick={handleUpgrade}
            disabled={checkoutLoading}
            className="w-full py-4 px-6 rounded-xl bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] font-semibold text-xs font-mono uppercase tracking-widest transition-all shadow-xl shadow-[#C5F5D5]/20 flex items-center justify-center gap-2 cursor-pointer"
          >
            <IconSparkles className="w-4 h-4" />
            <span>{checkoutLoading ? 'Opening Checkout...' : 'UPGRADE TO PRO'}</span>
          </button>

          <button
            onClick={closeQuotaModal}
            className="w-full py-2.5 text-center text-xs font-mono text-[#8A9B91] hover:text-[#F2F5F0] transition-colors"
          >
            I'll wait for the next billing cycle
          </button>
        </div>
      </div>
    </div>
  )
}
