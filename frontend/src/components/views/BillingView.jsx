import React, { useState } from 'react'
import { useAuth } from '../../context/useAuth'
import {
  IconCreditCard,
  IconSparkles,
  IconCheck,
  IconAlertTriangle,
  IconClock,
  IconRefresh,
} from '../icons/Icons'

export default function BillingView({ onOpenPricing }) {
  const {
    user,
    subscription,
    isAuthenticated,
    openAuthModal,
    initiateCheckout,
    cancelSubscription,
    refreshSubscription,
    checkoutLoading,
  } = useAuth()

  const [cancelModalOpen, setCancelModalOpen] = useState(false)
  const [cancelling, setCancelling] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [nowMs] = useState(() => Date.now())

  if (!isAuthenticated) {
    return (
      <div className="py-16 text-center max-w-xl mx-auto space-y-6">
        <div className="w-16 h-16 rounded-3xl bg-[#101512] border border-[rgba(197,245,213,0.2)] mx-auto flex items-center justify-center text-[#C5F5D5]">
          <IconCreditCard className="w-8 h-8" />
        </div>
        <h2 className="font-editorial text-4xl text-[#C5F5D5]">ACCOUNT & BILLING</h2>
        <p className="text-sm font-sans text-[#8A9B91]">
          Please sign in to view your current plan, monthly quota utilization, and subscription settings.
        </p>
        <div className="flex justify-center gap-4">
          <button
            onClick={() => openAuthModal('login')}
            className="py-3 px-6 rounded-xl border border-[rgba(197,245,213,0.3)] bg-[#101512] hover:bg-[#151D18] text-[#C5F5D5] font-mono text-xs uppercase tracking-wider transition-all"
          >
            Sign In
          </button>
          <button
            onClick={() => openAuthModal('register', 'pro')}
            className="py-3 px-6 rounded-xl bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] font-mono text-xs font-semibold uppercase tracking-wider transition-all shadow-lg shadow-[#C5F5D5]/10"
          >
            Start 30-Day Trial
          </button>
        </div>
      </div>
    )
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await refreshSubscription()
    setRefreshing(false)
  }

  const handleConfirmCancel = async () => {
    setCancelling(true)
    try {
      await cancelSubscription()
      setCancelModalOpen(false)
    } finally {
      setCancelling(false)
    }
  }

  // Quota and calculations
  const used = subscription?.analyses_used ?? 0
  const limit = subscription?.analyses_limit ?? (subscription?.plan === 'pro' ? 30 : 10)
  const remaining = subscription?.analyses_remaining ?? Math.max(0, limit - used)
  const usagePercentage = Math.min(100, Math.round((used / Math.max(1, limit)) * 100))

  // Trial dates
  let trialDaysRemaining = null
  let trialEndDateFormatted = null
  if (subscription?.trial_end) {
    const end = new Date(subscription.trial_end)
    trialEndDateFormatted = end.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
    const diffMs = end.getTime() - nowMs
    trialDaysRemaining = Math.max(0, Math.ceil(diffMs / (1000 * 60 * 60 * 24)))
  }

  // Next billing date
  let nextBillingDateFormatted = null
  if (subscription?.current_period_end) {
    const nextBill = new Date(subscription.current_period_end)
    nextBillingDateFormatted = nextBill.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // Status mapping
  const status = subscription?.status || 'none'
  const isTrial = status === 'trialing'
  const isActive = subscription?.is_active
  const isPro = subscription?.plan === 'pro'

  // SVG Circular Gauge calculation
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (usagePercentage / 100) * circumference

  return (
    <div className="space-y-8 animate-fade-in font-sans">
      {/* Page Title & Status Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[rgba(197,245,213,0.1)]">
        <div>
          <div className="text-xs font-mono tracking-widest uppercase text-[#8A9B91]">
            SUBSCRIPTION & USAGE CONTROL
          </div>
          <h1 className="font-editorial text-4xl sm:text-5xl font-light text-[#C5F5D5] mt-1">
            ACCOUNT & BILLING
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl border border-[rgba(197,245,213,0.18)] bg-[#101512] hover:bg-[#151D18] text-[#C5F5D5] text-xs font-mono transition-all"
            title="Refresh subscription status from backend"
          >
            <IconRefresh className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Sync Status</span>
          </button>

          {!isPro && (
            <button
              onClick={async () => {
                try {
                  await initiateCheckout('pro')
                } catch {
                  // Errors handled and toasted in AuthContext
                }
              }}
              disabled={checkoutLoading}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] text-xs font-mono font-semibold transition-all shadow-lg shadow-[#C5F5D5]/10 disabled:opacity-50"
            >
              <IconSparkles className="w-3.5 h-3.5" />
              <span>{checkoutLoading ? 'Connecting...' : 'Upgrade to Pro'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Trial Countdown Banner (if trialing) */}
      {isTrial && trialDaysRemaining !== null && (
        <div className="p-4 sm:p-5 rounded-2xl border border-[#C5F5D5]/40 bg-[#101713] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-lg shadow-[#C5F5D5]/5">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-[#C5F5D5]/20 flex items-center justify-center text-[#C5F5D5] shrink-0">
              <IconClock className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-mono font-bold tracking-wider text-[#C5F5D5] uppercase">
                YOUR FREE TRIAL IS ACTIVE
              </div>
              <div className="text-sm text-[#F2F5F0] mt-0.5 font-light">
                <span className="font-mono font-semibold text-[#C5F5D5]">{trialDaysRemaining} DAYS REMAINING</span>{' '}
                · Expires on {trialEndDateFormatted}
              </div>
            </div>
          </div>

          <button
            onClick={onOpenPricing}
            className="px-4 py-2 rounded-xl border border-[rgba(197,245,213,0.3)] bg-[#121B15] hover:bg-[#16231B] text-[#C5F5D5] text-xs font-mono transition-all"
          >
            View Paid Plans &rarr;
          </button>
        </div>
      )}

      {/* Primary KPI & Visualizations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Plan & Status */}
        <div className="p-6 sm:p-7 rounded-3xl bg-[#0C110E] border border-[rgba(197,245,213,0.15)] flex flex-col justify-between">
          <div>
            <div className="text-[11px] font-mono tracking-widest uppercase text-[#8A9B91]">
              CURRENT PLAN
            </div>
            <div className="font-editorial text-3xl sm:text-4xl text-[#C5F5D5] mt-2 capitalize">
              {subscription?.plan || 'No Active Plan'}
            </div>
            <div className="mt-3 flex items-center gap-2">
              <span
                className={`px-3 py-1 rounded-full text-xs font-mono font-bold tracking-wider uppercase border ${
                  isActive
                    ? 'bg-[#C5F5D5]/15 text-[#C5F5D5] border-[#C5F5D5]/30'
                    : 'bg-[#F87171]/15 text-[#F87171] border-[#F87171]/30'
                }`}
              >
                {status}
              </span>
              <span className="text-xs font-mono text-[#8A9B91]">
                {isPro ? '₹299/mo' : '₹199/mo'}
              </span>
            </div>
          </div>

          <div className="mt-6 pt-5 border-t border-[rgba(197,245,213,0.08)] text-xs font-mono text-[#8A9B91] space-y-1.5">
            {trialEndDateFormatted && (
              <div className="flex justify-between">
                <span>Trial Expiration:</span>
                <span className="text-[#F2F5F0]">{trialEndDateFormatted}</span>
              </div>
            )}
            {nextBillingDateFormatted && (
              <div className="flex justify-between">
                <span>Next Billing Date:</span>
                <span className="text-[#F2F5F0]">{nextBillingDateFormatted}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span>Account:</span>
              <span className="text-[#F2F5F0] truncate max-w-[150px]">{user?.email}</span>
            </div>
          </div>
        </div>

        {/* Card 2: Circular Usage Meter */}
        <div className="p-6 sm:p-7 rounded-3xl bg-[#0C110E] border border-[rgba(197,245,213,0.15)] flex flex-col items-center justify-between text-center">
          <div className="w-full text-left text-[11px] font-mono tracking-widest uppercase text-[#8A9B91]">
            ANALYSES CONSUMPTION
          </div>

          {/* SVG Circular Meter */}
          <div className="relative my-4 flex items-center justify-center">
            <svg className="w-36 h-36 -rotate-90 transform" viewBox="0 0 128 128">
              {/* Background circle */}
              <circle
                cx="64"
                cy="64"
                r={radius}
                className="text-[#101512]"
                strokeWidth="10"
                stroke="currentColor"
                fill="transparent"
              />
              {/* Progress bar circle */}
              <circle
                cx="64"
                cy="64"
                r={radius}
                className="text-[#C5F5D5] transition-all duration-1000 ease-out"
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
              />
            </svg>

            {/* Inner Percentage */}
            <div className="absolute flex flex-col items-center justify-center">
              <span className="font-editorial text-3xl sm:text-4xl text-[#C5F5D5] font-light">
                {used}
              </span>
              <span className="text-[10px] font-mono text-[#8A9B91] uppercase">
                of {limit} Used
              </span>
            </div>
          </div>

          <div className="w-full text-xs font-mono text-[#8A9B91]">
            <span className="text-[#C5F5D5] font-semibold">{remaining}</span> analyses remaining this cycle
          </div>
        </div>

        {/* Card 3: Remaining & Capacity Progress Bar */}
        <div className="p-6 sm:p-7 rounded-3xl bg-[#0C110E] border border-[rgba(197,245,213,0.15)] flex flex-col justify-between">
          <div>
            <div className="text-[11px] font-mono tracking-widest uppercase text-[#8A9B91]">
              REMAINING ALLOWANCE
            </div>
            <div className="font-editorial text-4xl sm:text-5xl text-[#C5F5D5] mt-2">
              {remaining}
            </div>
            <div className="text-xs font-mono text-[#8A9B91] mt-1">
              Documents available for verification
            </div>

            {/* Progress bar */}
            <div className="mt-5 space-y-2">
              <div className="flex justify-between text-[11px] font-mono text-[#8A9B91]">
                <span>Quota Utilized</span>
                <span className="text-[#F2F5F0] font-semibold">{usagePercentage}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-[#101512] overflow-hidden border border-[rgba(197,245,213,0.1)]">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    usagePercentage >= 90
                      ? 'bg-[#F87171]'
                      : usagePercentage >= 70
                      ? 'bg-[#FDE047]'
                      : 'bg-[#C5F5D5]'
                  }`}
                  style={{ width: `${usagePercentage}%` }}
                />
              </div>
            </div>
          </div>

          <div className="mt-6 pt-5 border-t border-[rgba(197,245,213,0.08)] flex items-center justify-between">
            <span className="text-xs font-mono text-[#8A9B91]">Cycle Resets:</span>
            <span className="text-xs font-mono text-[#F2F5F0]">1st of next month</span>
          </div>
        </div>
      </div>

      {/* Plan Capabilities & Management Actions */}
      <div className="p-6 sm:p-8 rounded-3xl bg-[#0C110E] border border-[rgba(197,245,213,0.15)] space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[rgba(197,245,213,0.08)]">
          <div>
            <h3 className="font-editorial text-2xl text-[#C5F5D5]">PLAN CAPABILITIES & CONTROLS</h3>
            <p className="text-xs font-mono text-[#8A9B91] mt-0.5">
              Features active on your account according to backend tier configuration
            </p>
          </div>

          <button
            onClick={onOpenPricing}
            className="text-xs font-mono text-[#C5F5D5] hover:underline"
          >
            Compare All Features &rarr;
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.1)] flex items-center gap-2.5">
            <IconCheck className="w-4 h-4 text-[#C5F5D5]" />
            <span>Deterministic Evidence Verifier</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.1)] flex items-center gap-2.5">
            <IconCheck className="w-4 h-4 text-[#C5F5D5]" />
            <span>Obligation & Deadline Tracker</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.1)] flex items-center gap-2.5">
            <IconCheck className="w-4 h-4 text-[#C5F5D5]" />
            <span>Commercial Policy Playbook Matcher</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.1)] flex items-center gap-2.5">
            <IconCheck className="w-4 h-4 text-[#C5F5D5]" />
            <span>Focused Knowledge Graph</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.1)] flex items-center gap-2.5">
            {isPro ? (
              <IconCheck className="w-4 h-4 text-[#C5F5D5]" />
            ) : (
              <span className="w-4 h-4 text-[#8A9B91] text-center font-bold">×</span>
            )}
            <span className={isPro ? 'text-[#F2F5F0]' : 'text-[#8A9B91]'}>
              Category Knowledge Graph {isPro ? '' : '(Pro only)'}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.1)] flex items-center gap-2.5">
            {isPro ? (
              <IconCheck className="w-4 h-4 text-[#C5F5D5]" />
            ) : (
              <span className="w-4 h-4 text-[#8A9B91] text-center font-bold">×</span>
            )}
            <span className={isPro ? 'text-[#F2F5F0]' : 'text-[#8A9B91]'}>
              Full Network Knowledge Graph {isPro ? '' : '(Pro only)'}
            </span>
          </div>
        </div>

        {/* Subscription Operations Actions */}
        <div className="pt-6 border-t border-[rgba(197,245,213,0.08)] flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {!isPro && (
              <button
                onClick={async () => {
                  try {
                    await initiateCheckout('pro')
                  } catch {
                    // Errors handled and toasted in AuthContext
                  }
                }}
                disabled={checkoutLoading}
                className="py-2.5 px-5 rounded-xl bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] font-mono text-xs font-semibold transition-all shadow-md shadow-[#C5F5D5]/10 disabled:opacity-50"
              >
                {checkoutLoading ? 'Connecting to Razorpay...' : 'Upgrade to Pro (₹299/mo)'}
              </button>
            )}

            <button
              onClick={onOpenPricing}
              className="py-2.5 px-5 rounded-xl border border-[rgba(197,245,213,0.2)] bg-[#101512] hover:bg-[#151D18] text-[#C5F5D5] font-mono text-xs transition-all"
            >
              Manage Plans
            </button>
          </div>

          {status !== 'cancelled' && (
            <button
              onClick={() => setCancelModalOpen(true)}
              className="text-xs font-mono text-[#F87171] hover:underline hover:text-[#EF4444] transition-colors"
            >
              Cancel Subscription
            </button>
          )}
        </div>
      </div>

      {/* Cancellation Confirmation Dialog */}
      {cancelModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#080B0A]/85 backdrop-blur-xl animate-fade-in">
          <div className="relative w-full max-w-md bg-[#0E1411] border border-[#F87171]/30 rounded-2xl p-6 sm:p-8 text-[#F2F5F0] space-y-4 shadow-2xl">
            <div className="w-10 h-10 rounded-xl bg-[#F87171]/20 flex items-center justify-center text-[#F87171]">
              <IconAlertTriangle className="w-5 h-5" />
            </div>

            <h3 className="font-editorial text-2xl text-[#F2F5F0]">
              Cancel Subscription?
            </h3>

            <p className="text-xs font-mono text-[#8A9B91] leading-relaxed">
              Are you sure you want to cancel your {subscription?.plan?.toUpperCase()} subscription?
              Your access will remain active until the end of the current billing cycle, after which new contract analyses will be paused.
            </p>

            <div className="pt-4 flex items-center justify-end gap-3 font-mono text-xs">
              <button
                onClick={() => setCancelModalOpen(false)}
                className="px-4 py-2 rounded-xl text-[#8A9B91] hover:text-[#F2F5F0]"
              >
                Keep Subscription
              </button>
              <button
                onClick={handleConfirmCancel}
                disabled={cancelling}
                className="px-5 py-2.5 rounded-xl bg-[#F87171] hover:bg-[#EF4444] text-[#080B0A] font-semibold transition-all cursor-pointer"
              >
                {cancelling ? 'Cancelling...' : 'Confirm Cancellation'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
