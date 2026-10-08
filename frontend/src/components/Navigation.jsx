import React from 'react'
import {
  IconDocument,
  IconShield,
  IconScale,
  IconClock,
  IconGraph,
  IconSparkles,
  IconNetwork,
  IconRefresh,
  IconUpload,
  IconCreditCard,
} from './icons/Icons'
import { WORKSPACE_TABS } from '../types/constants'
import AccountMenu from './AccountMenu'

const TAB_ICONS = {
  IconNetwork,
  IconDocument,
  IconShield,
  IconScale,
  IconClock,
  IconSparkles,
  IconGraph,
  IconCreditCard,
}

export default function Navigation({
  activeTab,
  onSelectTab,
  connectionStatus,
  onRecheckConnection,
  onReturnToLanding,
  isDemoData,
  contractFilename,
  onOpenUpload,
  onLoadDemo,
  isAnalyzing,
  onOpenPricing,
}) {
  return (
    <header className="sticky top-0 z-30 bg-[#080B0A]/95 backdrop-blur-xl border-b border-[rgba(197,245,213,0.1)] text-[#F2F5F0]">
      {/* Top Banner & Metadata */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Brand & Home */}
        <div className="flex items-center gap-4">
          <button
            onClick={onReturnToLanding}
            className="flex items-center gap-2 group text-left"
            title="Return to Cinematic Story"
          >
            <span className="font-editorial text-2xl sm:text-3xl tracking-widest text-[#C5F5D5] group-hover:opacity-80 transition-opacity">
              VERITAS AI
            </span>
          </button>

          {/* Active Contract / Demo Indicator */}
          {contractFilename && !isDemoData && (
            <div className="hidden md:flex items-center gap-2 pl-4 border-l border-[rgba(197,245,213,0.12)] text-xs">
              <span className="text-[#8A9B91]">Contract:</span>
              <span className="font-mono text-[#F2F5F0] bg-[#101512] px-2.5 py-0.5 rounded border border-[rgba(197,245,213,0.15)] max-w-[200px] truncate">
                {contractFilename}
              </span>
            </div>
          )}

          {isDemoData ? (
            <div className="flex items-center gap-2.5">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono tracking-wider bg-[#101512] text-[#A8E6BF] border border-[#A8E6BF]/30">
                <span className="w-1.5 h-1.5 rounded-full bg-[#A8E6BF] animate-pulse" />
                DEMO — SAMPLE CONTRACT & POLICY
              </span>
              <button
                onClick={onOpenUpload}
                disabled={isAnalyzing}
                className="hidden sm:inline-flex items-center gap-1.5 text-xs font-sans font-medium px-2.5 py-1 rounded-md bg-[#101512] hover:bg-[#151D18] text-[#C5F5D5] border border-[#C5F5D5]/30 transition-all"
                title="Switch from demo to analyze your own contract"
              >
                <span>Analyze Your Own Contract &rarr;</span>
              </button>
            </div>
          ) : (
            <div className="hidden lg:flex items-center gap-2 text-[11px] font-mono text-[#8A9B91]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#C5F5D5]" />
              <span>Policy: Built-in Commercial Playbook v1.0</span>
            </div>
          )}
        </div>

        {/* Status & Actions */}
        <div className="flex items-center gap-3">
          {/* Connection Status */}
          <button
            onClick={onRecheckConnection}
            className={`text-xs px-3 py-1 rounded-full border flex items-center gap-2 transition-all font-mono ${
              connectionStatus === 'online'
                ? 'border-[#C5F5D5]/30 bg-[#101512] text-[#C5F5D5]'
                : connectionStatus === 'checking'
                ? 'border-[#A8E6BF]/30 bg-[#101512] text-[#A8E6BF]'
                : 'border-[#F87171]/30 bg-[#180E10] text-[#F87171]'
            }`}
            title="Click to check FastAPI health"
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                connectionStatus === 'online'
                  ? 'bg-[#C5F5D5]'
                  : connectionStatus === 'checking'
                  ? 'bg-[#A8E6BF] animate-ping'
                  : 'bg-[#F87171]'
              }`}
            />
            <span className="capitalize">{connectionStatus}</span>
            <IconRefresh className="w-3 h-3 opacity-60 ml-0.5" />
          </button>

          {/* Quick Demo Button */}
          <button
            onClick={onLoadDemo}
            disabled={isAnalyzing}
            className="text-xs font-mono px-3.5 py-1.5 rounded-lg border border-[rgba(197,245,213,0.18)] bg-[#101512] hover:bg-[#151D18] text-[#C5F5D5] transition-all disabled:opacity-50"
            title="Load hand-authored offline demo dataset"
          >
            Load Demo Data
          </button>

          {/* Upload Button */}
          <button
            onClick={onOpenUpload}
            disabled={isAnalyzing}
            className="text-xs font-sans font-semibold px-4 py-1.5 rounded-lg bg-[#C5F5D5] hover:bg-[#A8E6BF] text-[#080B0A] transition-all flex items-center gap-1.5 shadow-sm shadow-[#C5F5D5]/10 disabled:opacity-50"
          >
            <IconUpload className="w-3.5 h-3.5" />
            <span>Upload Contract</span>
          </button>

          {/* User Account & Subscription Menu */}
          <div className="pl-1 sm:pl-2 border-l border-[rgba(197,245,213,0.15)]">
            <AccountMenu
              onNavigateToBilling={() => onSelectTab('billing')}
              onOpenPricing={onOpenPricing}
            />
          </div>
        </div>
      </div>

      {/* Workspace Tabs Navigation */}
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 flex space-x-1 sm:space-x-2 overflow-x-auto scrollbar-none py-1 border-t border-[rgba(197,245,213,0.08)]" aria-label="Workspace tabs">
        {WORKSPACE_TABS.map((tab) => {
          const Icon = TAB_ICONS[tab.icon] || IconDocument
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              className={`flex items-center gap-2 px-3.5 py-2 text-xs sm:text-sm font-sans font-medium rounded-lg whitespace-nowrap transition-all border ${
                isActive
                  ? 'bg-[#101512] text-[#C5F5D5] border-[rgba(197,245,213,0.3)] shadow-sm'
                  : 'text-[#8A9B91] hover:text-[#F2F5F0] hover:bg-[#101512]/60 border-transparent'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-[#C5F5D5]' : 'text-[#8A9B91]'}`} />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </nav>
    </header>
  )
}
