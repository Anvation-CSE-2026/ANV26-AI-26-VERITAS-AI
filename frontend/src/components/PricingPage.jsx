import React from 'react'
import { useAuth } from '../context/useAuth'
import {
  IconCheck,
  IconSparkles,
  IconArrowLeft,
} from './icons/Icons'

export default function PricingPage({ onReturn }) {
  const {
    plans,
    user,
    subscription,
    isAuthenticated,
    openAuthModal,
    initiateCheckout,
    checkoutLoading,
  } = useAuth()

  // Find backend plans, falling back to canonical defaults if loading
  const stdPlan = plans.find((p) => p.tier === 'standard')
  const proPlan = plans.find((p) => p.tier === 'pro')

  const stdPrice = stdPlan ? stdPlan.price_inr : 199
  const proPrice = proPlan ? proPlan.price_inr : 299

  const handlePlanAction = async (planTier) => {
    // 1. If not authenticated, prompt registration with selected plan
    if (!isAuthenticated) {
      openAuthModal('register', planTier)
      return
    }

    // 2. If authenticated and trial has NOT been used, open trial confirmation
    if (!user?.trial_used) {
      openAuthModal('trial', planTier)
      return
    }

    // 3. If trial was already used, initiate Razorpay Checkout in Test Mode
    try {
      await initiateCheckout(planTier)
    } catch {
      // Errors handled via toast in AuthContext
    }
  }

  const isCurrentPlan = (tier) => {
    return subscription?.plan === tier && subscription?.is_active
  }

  return (
    <div className="min-h-screen bg-[#080B0A] text-[#F2F5F0] selection:bg-[#C5F5D5] selection:text-[#080B0A] py-12 px-4 sm:px-6 lg:px-8">
      {/* Background ambient lighting */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-[#C5F5D5]/5 rounded-full blur-[140px]" />
      </div>

      <div className="relative max-w-6xl mx-auto">
        {/* Top bar with back button */}
        <div className="flex items-center justify-between pb-10">
          <button
            onClick={onReturn}
            className="inline-flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[#8A9B91] hover:text-[#C5F5D5] transition-colors py-2 px-3 rounded-lg hover:bg-[#101512]"
          >
            <IconArrowLeft className="w-4 h-4" />
            <span>Back to Workspace</span>
          </button>

          <div className="text-[11px] font-mono text-[#8A9B91] tracking-wider uppercase flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#C5F5D5] animate-pulse" />
            <span>TRANSPARENT ENTERPRISE PRICING</span>
          </div>
        </div>

        {/* Section Heading */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="text-xs font-mono tracking-widest text-[#8A9B91] uppercase">
            PLANS & ENTITLEMENTS // COMMERCIAL TERMS
          </div>
          <h1 className="font-editorial text-4xl sm:text-6xl md:text-7xl font-light text-[#C5F5D5] leading-[1.05] tracking-tight mint-glow">
            Contract Intelligence.<br />
            Deterministic Value.
          </h1>
          <p className="font-sans text-sm sm:text-base text-[#8A9B91] font-light max-w-xl mx-auto leading-relaxed">
            Every plan includes our deterministic evidence verification engine. Start with a 30-day zero-risk trial.
          </p>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto items-stretch">
          {/* =========================================================
              STANDARD PLAN — ₹199/month
              ========================================================= */}
          <div
            className={`relative rounded-3xl p-8 sm:p-10 flex flex-col justify-between transition-all border ${
              isCurrentPlan('standard')
                ? 'border-[#C5F5D5] bg-[#0E1511] shadow-2xl shadow-[#C5F5D5]/10'
                : 'border-[rgba(197,245,213,0.15)] bg-[#0C100E] hover:border-[rgba(197,245,213,0.3)] shadow-xl'
            }`}
          >
            <div>
              {/* Plan Header */}
              <div className="flex items-center justify-between mb-4">
                <span className="font-mono text-xs uppercase tracking-widest text-[#8A9B91]">
                  STANDARD
                </span>
                {isCurrentPlan('standard') && (
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono tracking-wider bg-[#C5F5D5]/20 text-[#C5F5D5] border border-[#C5F5D5]/30">
                    CURRENT PLAN
                  </span>
                )}
              </div>

              <div className="flex items-baseline gap-2 mb-2">
                <span className="font-editorial text-5xl sm:text-6xl text-[#F2F5F0]">
                  ₹{stdPrice}
                </span>
                <span className="font-mono text-xs text-[#8A9B91]">/ month</span>
              </div>

              <p className="font-sans text-xs sm:text-sm text-[#8A9B91] leading-relaxed mb-8">
                Essential intelligence for legal analysts and growing teams reviewing active commercial supplier contracts.
              </p>

              {/* Feature Checklist */}
              <div className="space-y-3.5 mb-8 text-xs font-mono text-[#F2F5F0]">
                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[#C5F5D5] font-semibold">30-day free trial</span>
                    <span className="text-[#8A9B91] block text-[11px]">Zero upfront fee or credit card needed</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold">10 contract analyses / month</span>
                    <span className="text-[#8A9B91] block text-[11px]">Full PDF ingestion up to 30 pages</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <span>AI risk analysis across 7 core categories</span>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <span>Evidence verification with exact provenance</span>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <span>Policy comparison against company playbooks</span>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <span>Obligation tracking with action deadlines</span>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <span>Focused knowledge graph view</span>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <span className="text-[#8A9B91]">5-item analysis history retention</span>
                </div>
              </div>
            </div>

            {/* Action Button */}
            <button
              onClick={() => handlePlanAction('standard')}
              disabled={checkoutLoading || isCurrentPlan('standard')}
              className={`w-full py-3.5 px-6 rounded-xl font-mono text-xs font-semibold uppercase tracking-widest transition-all cursor-pointer ${
                isCurrentPlan('standard')
                  ? 'bg-[#151D18] text-[#8A9B91] cursor-default border border-[rgba(197,245,213,0.1)]'
                  : 'bg-[#101512] hover:bg-[#151D18] text-[#C5F5D5] border border-[rgba(197,245,213,0.3)] hover:border-[#C5F5D5] shadow-lg hover:scale-[1.01]'
              }`}
            >
              {isCurrentPlan('standard')
                ? 'Active Plan'
                : !user?.trial_used
                ? 'START 30-DAY FREE TRIAL'
                : 'SELECT STANDARD'}
            </button>
          </div>

          {/* =========================================================
              PRO PLAN — ₹299/month (RECOMMENDED)
              ========================================================= */}
          <div
            className={`relative rounded-3xl p-8 sm:p-10 flex flex-col justify-between transition-all border ${
              isCurrentPlan('pro')
                ? 'border-[#C5F5D5] bg-[#0E1712] shadow-2xl shadow-[#C5F5D5]/20 ring-1 ring-[#C5F5D5]/30'
                : 'border-[#C5F5D5]/40 bg-[#0E1511] hover:border-[#C5F5D5] shadow-2xl shadow-[#C5F5D5]/10'
            }`}
          >
            {/* Recommended Pill */}
            <div className="absolute -top-3.5 right-8">
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-[10px] font-mono tracking-widest uppercase bg-[#C5F5D5] text-[#080B0A] font-bold shadow-md shadow-[#C5F5D5]/20">
                <IconSparkles className="w-3.5 h-3.5" />
                <span>RECOMMENDED</span>
              </span>
            </div>

            <div>
              {/* Plan Header */}
              <div className="flex items-center justify-between mb-4">
                <span className="font-mono text-xs uppercase tracking-widest text-[#A8E6BF]">
                  PRO PLAN
                </span>
                {isCurrentPlan('pro') && (
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono tracking-wider bg-[#C5F5D5]/20 text-[#C5F5D5] border border-[#C5F5D5]/30">
                    CURRENT PLAN
                  </span>
                )}
              </div>

              <div className="flex items-baseline gap-2 mb-2">
                <span className="font-editorial text-5xl sm:text-6xl text-[#C5F5D5]">
                  ₹{proPrice}
                </span>
                <span className="font-mono text-xs text-[#8A9B91]">/ month</span>
              </div>

              <p className="font-sans text-xs sm:text-sm text-[#8A9B91] leading-relaxed mb-8">
                Comprehensive contract risk command center for enterprise legal teams managing multi-vendor portfolios.
              </p>

              {/* Feature Checklist */}
              <div className="space-y-3.5 mb-8 text-xs font-mono text-[#F2F5F0]">
                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[#C5F5D5] font-semibold">30-day free trial</span>
                    <span className="text-[#8A9B91] block text-[11px]">Instant activation without card requirement</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[#C5F5D5] font-semibold">30 contract analyses / month</span>
                    <span className="text-[#8A9B91] block text-[11px]">3x capacity for active procurement teams</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <span className="text-[#A8E6BF] font-semibold">Everything in Standard Plan</span>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#F2F5F0]">Full network knowledge graph</span>
                    <span className="text-[#8A9B91] block text-[11px]">Interactive dependency clustering</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#F2F5F0]">Category graph views</span>
                    <span className="text-[#8A9B91] block text-[11px]">Filtered risk topology visualization</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-[#F2F5F0]">30-item analysis history retention</span>
                    <span className="text-[#8A9B91] block text-[11px]">Comprehensive archive and retrieval</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <IconCheck className="w-4 h-4 text-[#C5F5D5] shrink-0 mt-0.5" />
                  <span>Unlimited synthetic demo evaluations</span>
                </div>
              </div>
            </div>

            {/* Action Button */}
            <button
              onClick={() => handlePlanAction('pro')}
              disabled={checkoutLoading || isCurrentPlan('pro')}
              className={`w-full py-4 px-6 rounded-xl font-mono text-xs font-semibold uppercase tracking-widest transition-all shadow-xl cursor-pointer ${
                isCurrentPlan('pro')
                  ? 'bg-[#151D18] text-[#8A9B91] cursor-default border border-[rgba(197,245,213,0.1)]'
                  : 'bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] shadow-[#C5F5D5]/20 hover:scale-[1.02] active:scale-[0.98]'
              }`}
            >
              {checkoutLoading ? (
                'Connecting to Razorpay...'
              ) : isCurrentPlan('pro') ? (
                'Active Plan'
              ) : !user?.trial_used ? (
                'START 30-DAY FREE TRIAL'
              ) : (
                'UPGRADE TO PRO'
              )}
            </button>
          </div>
        </div>

        {/* Feature Comparison Matrix Table */}
        <div className="mt-20 max-w-4xl mx-auto rounded-2xl border border-[rgba(197,245,213,0.12)] bg-[#0C100E] p-6 sm:p-8">
          <div className="text-xs font-mono uppercase tracking-wider text-[#8A9B91] mb-6 text-center">
            DETAILED ENTITLEMENT MATRIX
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[rgba(197,245,213,0.1)] text-[#8A9B91]">
                  <th className="py-3 px-4">Capability</th>
                  <th className="py-3 px-4">Standard</th>
                  <th className="py-3 px-4 text-[#C5F5D5]">Pro (Recommended)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(197,245,213,0.06)] text-[#F2F5F0]">
                <tr>
                  <td className="py-3 px-4">Monthly Analysis Allowance</td>
                  <td className="py-3 px-4 text-[#8A9B91]">10 contracts</td>
                  <td className="py-3 px-4 text-[#C5F5D5] font-semibold">30 contracts</td>
                </tr>
                <tr>
                  <td className="py-3 px-4">Audit History Retention</td>
                  <td className="py-3 px-4 text-[#8A9B91]">5 contracts</td>
                  <td className="py-3 px-4 text-[#C5F5D5] font-semibold">30 contracts</td>
                </tr>
                <tr>
                  <td className="py-3 px-4">Deterministic Evidence Verification</td>
                  <td className="py-3 px-4">Included</td>
                  <td className="py-3 px-4 text-[#C5F5D5]">Included</td>
                </tr>
                <tr>
                  <td className="py-3 px-4">Knowledge Graph Visualizations</td>
                  <td className="py-3 px-4 text-[#8A9B91]">Focused only</td>
                  <td className="py-3 px-4 text-[#C5F5D5] font-semibold">Focused, Category & Full Network</td>
                </tr>
                <tr>
                  <td className="py-3 px-4">Action Plan & Obligation Tracker</td>
                  <td className="py-3 px-4">Included</td>
                  <td className="py-3 px-4 text-[#C5F5D5]">Included</td>
                </tr>
                <tr>
                  <td className="py-3 px-4">Commercial Playbook Alignment</td>
                  <td className="py-3 px-4">Included</td>
                  <td className="py-3 px-4 text-[#C5F5D5]">Included</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Security & Guarantee Footer */}
        <div className="mt-12 text-center text-xs font-mono text-[#8A9B91]/70 max-w-xl mx-auto space-y-2">
          <p>
            Payments processed securely via Razorpay Test Mode · Cancel anytime in one click.
          </p>
          <p className="text-[10px]">
            Introductory 30-day trial limited to 1 trial per enterprise account.
          </p>
        </div>
      </div>
    </div>
  )
}
