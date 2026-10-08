import React, { useState, useRef, useEffect } from 'react'
import { useAuth } from '../context/useAuth'
import {
  IconCreditCard,
  IconLogout,
  IconChevronDown,
  IconSparkles,
} from './icons/Icons'

export default function AccountMenu({ onNavigateToBilling, onOpenPricing }) {
  const { user, subscription, isAuthenticated, logout, openAuthModal } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef(null)

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  if (!isAuthenticated) {
    return (
      <div className="flex items-center gap-2">
        <button
          onClick={onOpenPricing}
          className="text-xs font-mono px-3 py-1.5 rounded-lg border border-[rgba(197,245,213,0.18)] bg-[#101512] hover:bg-[#151D18] text-[#C5F5D5] transition-all"
        >
          Pricing
        </button>
        <button
          onClick={() => openAuthModal('login')}
          className="text-xs font-mono px-3 py-1.5 rounded-lg text-[#8A9B91] hover:text-[#F2F5F0] hover:bg-[#101512] transition-all"
        >
          Sign In
        </button>
        <button
          onClick={() => openAuthModal('register', 'pro')}
          className="text-xs font-mono font-medium px-3.5 py-1.5 rounded-lg bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] transition-all shadow-sm shadow-[#C5F5D5]/10"
        >
          Start Trial
        </button>
      </div>
    )
  }

  const planName = subscription?.plan ? subscription.plan.toUpperCase() : 'NO PLAN'
  const isTrial = subscription?.status === 'trialing'
  const statusLabel = isTrial ? 'TRIAL' : (subscription?.status || 'INACTIVE').toUpperCase()
  const analysesRemaining = subscription?.analyses_remaining ?? 0

  return (
    <div className="relative" ref={menuRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl border border-[rgba(197,245,213,0.2)] bg-[#101512] hover:bg-[#151D18] text-[#F2F5F0] transition-all text-xs font-mono"
      >
        <div className="w-5 h-5 rounded-full bg-[#C5F5D5]/15 border border-[#C5F5D5]/30 flex items-center justify-center text-[#C5F5D5] text-[10px] font-bold">
          {user.email.charAt(0).toUpperCase()}
        </div>

        <span className="max-w-[120px] truncate hidden sm:inline">{user.email}</span>

        {/* Plan status pill */}
        <span
          className={`px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider ${
            subscription?.is_active
              ? 'bg-[#C5F5D5]/20 text-[#C5F5D5] border border-[#C5F5D5]/30'
              : 'bg-[#F87171]/20 text-[#F87171] border border-[#F87171]/30'
          }`}
        >
          {planName} · {statusLabel}
        </span>

        <IconChevronDown className="w-3.5 h-3.5 text-[#8A9B91]" />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 rounded-2xl bg-[#0E1411] border border-[rgba(197,245,213,0.2)] shadow-2xl z-50 text-[#F2F5F0] py-2 overflow-hidden animate-fade-in font-mono text-xs">
          {/* User info section */}
          <div className="px-4 py-3 border-b border-[rgba(197,245,213,0.08)] bg-[#121914]/50">
            <div className="text-[#8A9B91] text-[10px] tracking-wider uppercase">Signed in as</div>
            <div className="font-semibold text-sm truncate text-[#C5F5D5] mt-0.5">{user.email}</div>

            {subscription && (
              <div className="mt-2.5 pt-2 border-t border-[rgba(197,245,213,0.08)] flex items-center justify-between text-[11px]">
                <span className="text-[#8A9B91]">Remaining:</span>
                <span className="font-semibold text-[#F2F5F0]">
                  {analysesRemaining} / {subscription.analyses_limit} analyses
                </span>
              </div>
            )}
          </div>

          {/* Menu Items */}
          <div className="p-1 space-y-0.5">
            <button
              onClick={() => {
                setIsOpen(false)
                if (onNavigateToBilling) onNavigateToBilling()
              }}
              className="w-full flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl hover:bg-[#151D18] text-[#F2F5F0] hover:text-[#C5F5D5] transition-colors text-left"
            >
              <IconCreditCard className="w-4 h-4 text-[#C5F5D5]" />
              <span>Account & Billing</span>
            </button>

            <button
              onClick={() => {
                setIsOpen(false)
                if (onOpenPricing) onOpenPricing()
              }}
              className="w-full flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl hover:bg-[#151D18] text-[#F2F5F0] hover:text-[#C5F5D5] transition-colors text-left"
            >
              <IconSparkles className="w-4 h-4 text-[#A8E6BF]" />
              <span>View Plans & Upgrades</span>
            </button>
          </div>

          {/* Sign Out */}
          <div className="p-1 border-t border-[rgba(197,245,213,0.08)] mt-1">
            <button
              onClick={() => {
                setIsOpen(false)
                logout()
              }}
              className="w-full flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl hover:bg-[#180E10] text-[#F87171] transition-colors text-left"
            >
              <IconLogout className="w-4 h-4 text-[#F87171]" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
