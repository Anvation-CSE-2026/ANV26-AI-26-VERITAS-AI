import React, { useState } from 'react'
import { useAuth } from '../context/useAuth'
import {
  IconX,
  IconLock,
  IconEye,
  IconEyeOff,
  IconCheck,
  IconSparkles,
} from './icons/Icons'

export default function AuthModal({ onSuccess }) {
  const { authModal, closeAuthModal, login, register, startTrial } = useAuth()
  const { isOpen, mode: initialMode, plan: initialPlan, message } = authModal

  const [mode, setMode] = useState(initialMode || 'login')
  const [selectedPlan, setSelectedPlan] = useState(initialPlan || 'pro')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [formError, setFormError] = useState(message || null)
  const [trialSuccessData, setTrialSuccessData] = useState(null)

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setFormError(null)

    if (mode !== 'trial') {
      if (!email.trim() || !password.trim()) {
        setFormError('Please enter both email and password.')
        return
      }
      if (password.length < 8) {
        setFormError('Password must be at least 8 characters.')
        return
      }
    }

    setLoading(true)
    try {
      if (mode === 'login') {
        await login(email.trim(), password)
        closeAuthModal()
        if (onSuccess) onSuccess()
      } else if (mode === 'register') {
        await register(email.trim(), password)
        // Switch to trial activation mode seamlessly!
        setMode('trial')
      } else if (mode === 'trial') {
        const sub = await startTrial(selectedPlan)
        setTrialSuccessData(sub)
        setTimeout(() => {
          closeAuthModal()
          if (onSuccess) onSuccess()
        }, 1200)
      }
    } catch (err) {
      setFormError(err.message || 'Operation failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#080B0A]/80 backdrop-blur-xl animate-fade-in">
      <div
        className="relative w-full max-w-lg bg-[#0E1310] border border-[rgba(197,245,213,0.2)] rounded-2xl shadow-2xl overflow-hidden text-[#F2F5F0]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Subtle decorative glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#C5F5D5]/5 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Header */}
        <div className="px-6 sm:px-8 pt-7 pb-4 flex items-center justify-between border-b border-[rgba(197,245,213,0.08)]">
          <div>
            <div className="text-[10px] font-mono tracking-widest uppercase text-[#8A9B91]">
              VERITAS AI // ACCESS CONTROL
            </div>
            <h2 className="font-editorial text-2xl sm:text-3xl text-[#C5F5D5] mt-1">
              {mode === 'login'
                ? 'Welcome Back'
                : mode === 'register'
                ? 'Create Your Account'
                : 'Activate 30-Day Free Trial'}
            </h2>
          </div>
          <button
            onClick={closeAuthModal}
            className="p-2 text-[#8A9B91] hover:text-[#F2F5F0] rounded-lg hover:bg-[#151D18] transition-colors"
            title="Close dialog"
          >
            <IconX className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 sm:p-8">
          {/* Mode Switch Tabs (when not in trial confirmation) */}
          {mode !== 'trial' && (
            <div className="flex border-b border-[rgba(197,245,213,0.12)] mb-6">
              <button
                type="button"
                onClick={() => {
                  setMode('login')
                  setFormError(null)
                }}
                className={`flex-1 pb-3 text-xs sm:text-sm font-medium transition-all border-b-2 text-center ${
                  mode === 'login'
                    ? 'border-[#C5F5D5] text-[#C5F5D5]'
                    : 'border-transparent text-[#8A9B91] hover:text-[#F2F5F0]'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => {
                  setMode('register')
                  setFormError(null)
                }}
                className={`flex-1 pb-3 text-xs sm:text-sm font-medium transition-all border-b-2 text-center ${
                  mode === 'register'
                    ? 'border-[#C5F5D5] text-[#C5F5D5]'
                    : 'border-transparent text-[#8A9B91] hover:text-[#F2F5F0]'
                }`}
              >
                Sign Up & Trial
              </button>
            </div>
          )}

          {/* Form Error Banner */}
          {formError && (
            <div className="mb-5 p-3.5 rounded-xl border border-[#F87171]/30 bg-[#180E10] text-[#F87171] text-xs font-mono flex items-start gap-2.5">
              <span className="w-2 h-2 rounded-full bg-[#F87171] mt-1 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          {/* Trial Success Toast inside modal */}
          {trialSuccessData && (
            <div className="mb-5 p-4 rounded-xl border border-[#C5F5D5]/40 bg-[#101512] text-[#C5F5D5] text-xs font-mono flex items-center gap-3">
              <IconCheck className="w-5 h-5 text-[#C5F5D5] shrink-0" />
              <div>
                <div className="font-semibold text-sm">YOUR FREE TRIAL IS ACTIVE</div>
                <div className="text-[11px] text-[#8A9B91] mt-0.5">
                  30 Days Remaining · {trialSuccessData.analyses_limit} Monthly Analyses Included
                </div>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode !== 'trial' ? (
              <>
                <div>
                  <label className="block text-xs font-mono uppercase tracking-wider text-[#8A9B91] mb-1.5">
                    Corporate Email
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="legal@organization.com"
                    className="w-full px-4 py-3 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.18)] focus:border-[#C5F5D5] text-[#F2F5F0] placeholder-[#8A9B91]/40 text-sm font-mono outline-none transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-xs font-mono uppercase tracking-wider text-[#8A9B91] mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="At least 8 characters"
                      className="w-full px-4 py-3 pr-12 rounded-xl bg-[#101512] border border-[rgba(197,245,213,0.18)] focus:border-[#C5F5D5] text-[#F2F5F0] placeholder-[#8A9B91]/40 text-sm font-mono outline-none transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#8A9B91] hover:text-[#F2F5F0]"
                      tabIndex={-1}
                    >
                      {showPassword ? <IconEyeOff className="w-4 h-4" /> : <IconEye className="w-4 h-4" />}
                    </button>
                  </div>
                  <p className="text-[10px] text-[#8A9B91] mt-1 font-mono">
                    Must be at least 8 characters with letters and numbers.
                  </p>
                </div>
              </>
            ) : (
              /* Trial Confirmation Step */
              <div className="space-y-4">
                <div className="p-3.5 rounded-xl border border-[rgba(197,245,213,0.2)] bg-[#101512] text-xs font-mono text-[#8A9B91] space-y-1">
                  <div className="text-[#C5F5D5] font-semibold flex items-center gap-1.5">
                    <IconSparkles className="w-4 h-4" />
                    <span>Select Your 30-Day Introductory Plan</span>
                  </div>
                  <div>No credit card required. Full feature access granted immediately.</div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {/* Standard Option */}
                  <button
                    type="button"
                    onClick={() => setSelectedPlan('standard')}
                    className={`p-4 rounded-xl border text-left transition-all relative ${
                      selectedPlan === 'standard'
                        ? 'border-[#C5F5D5] bg-[#121B15] shadow-lg shadow-[#C5F5D5]/5'
                        : 'border-[rgba(197,245,213,0.12)] bg-[#101512] hover:border-[rgba(197,245,213,0.25)]'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs uppercase tracking-wider text-[#8A9B91]">STANDARD</span>
                      {selectedPlan === 'standard' && <IconCheck className="w-4 h-4 text-[#C5F5D5]" />}
                    </div>
                    <div className="font-editorial text-2xl text-[#F2F5F0] mt-1">₹199</div>
                    <div className="text-[11px] font-mono text-[#8A9B91]">10 analyses/mo</div>
                    <div className="text-[10px] text-[#C5F5D5] font-mono mt-2">30-day free trial</div>
                  </button>

                  {/* Pro Option (Recommended) */}
                  <button
                    type="button"
                    onClick={() => setSelectedPlan('pro')}
                    className={`p-4 rounded-xl border text-left transition-all relative ${
                      selectedPlan === 'pro'
                        ? 'border-[#C5F5D5] bg-[#121B15] shadow-lg shadow-[#C5F5D5]/10'
                        : 'border-[rgba(197,245,213,0.12)] bg-[#101512] hover:border-[rgba(197,245,213,0.25)]'
                    }`}
                  >
                    <span className="absolute -top-2.5 right-3 px-2 py-0.5 rounded-full text-[9px] font-mono tracking-wider bg-[#C5F5D5] text-[#080B0A] font-bold">
                      RECOMMENDED
                    </span>
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs uppercase tracking-wider text-[#A8E6BF]">PRO PLAN</span>
                      {selectedPlan === 'pro' && <IconCheck className="w-4 h-4 text-[#C5F5D5]" />}
                    </div>
                    <div className="font-editorial text-2xl text-[#C5F5D5] mt-1">₹299</div>
                    <div className="text-[11px] font-mono text-[#8A9B91]">30 analyses/mo</div>
                    <div className="text-[10px] text-[#A8E6BF] font-mono mt-2">Full knowledge graph</div>
                  </button>
                </div>

                {/* Plan Highlights */}
                <div className="p-3 bg-[#101512] rounded-xl border border-[rgba(197,245,213,0.1)] text-xs text-[#8A9B91] space-y-1.5 font-mono">
                  <div className="flex items-center gap-2 text-[#F2F5F0]">
                    <IconCheck className="w-3.5 h-3.5 text-[#C5F5D5]" />
                    <span>30 days zero-cost evaluation period</span>
                  </div>
                  <div className="flex items-center gap-2 text-[#F2F5F0]">
                    <IconCheck className="w-3.5 h-3.5 text-[#C5F5D5]" />
                    <span>Deterministic evidence verification & citations</span>
                  </div>
                  <div className="flex items-center gap-2 text-[#F2F5F0]">
                    <IconCheck className="w-3.5 h-3.5 text-[#C5F5D5]" />
                    <span>
                      {selectedPlan === 'pro' ? '30 contract analyses/month' : '10 contract analyses/month'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !!trialSuccessData}
              className="w-full mt-4 py-3.5 px-6 rounded-xl bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] font-semibold text-xs font-mono uppercase tracking-widest transition-all shadow-lg shadow-[#C5F5D5]/10 disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-[#080B0A] border-t-transparent rounded-full animate-spin" />
                  <span>Processing...</span>
                </>
              ) : mode === 'login' ? (
                <span>Sign In to Veritas</span>
              ) : mode === 'register' ? (
                <span>Create Account & Continue</span>
              ) : (
                <span>START 30-DAY FREE TRIAL</span>
              )}
            </button>
          </form>

          {/* Security footnote */}
          <div className="mt-5 text-center text-[11px] font-mono text-[#8A9B91]/70 flex items-center justify-center gap-1.5">
            <IconLock className="w-3.5 h-3.5 text-[#C5F5D5]/60" />
            <span>End-to-end multi-tenant isolation · PBKDF2 encryption</span>
          </div>
        </div>
      </div>
    </div>
  )
}
