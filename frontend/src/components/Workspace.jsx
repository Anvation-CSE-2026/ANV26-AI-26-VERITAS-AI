import React, { useState, useEffect } from 'react'
import Navigation from './Navigation'
import ErrorBanner from './ErrorBanner'
import AnalysisProgressModal from './AnalysisProgressModal'
import OverviewView from './views/OverviewView'
import ContractsView from './views/ContractsView'
import RiskDashboardView from './views/RiskDashboardView'
import EvidenceExplorerView from './views/EvidenceExplorerView'
import ObligationsView from './views/ObligationsView'
import PolicyComparisonView from './views/PolicyComparisonView'
import KnowledgeGraphView from './views/KnowledgeGraphView'
import CompanyWorkspaceView from './views/CompanyWorkspaceView'
import BillingView from './views/BillingView'
import { useAuth } from '../context/useAuth'

export default function Workspace({
  analysis,
  contract,
  isDemoData,
  connectionStatus,
  onRecheckConnection,
  onReturnToLanding,
  onUploadFile,
  onStartAnalysis,
  onLoadDemo,
  isUploading,
  isAnalyzing,
  error,
  onDismissError,
  onRetryLastAction,
  onOpenPricing,
}) {
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedFinding, setSelectedFinding] = useState(null)
  const { isAuthenticated, openAuthModal, isExpired, openQuotaModal } = useAuth()

  // Catch HTTP 429 quota exhaustion and open the upgrade dialog
  useEffect(() => {
    if (error && (error.status === 429 || error.state === 'quota_exhausted')) {
      openQuotaModal(error)
    }
  }, [error, openQuotaModal])

  const handleNavigateToFinding = (finding) => {
    setSelectedFinding(finding)
    setActiveTab('evidence')
  }

  const handleOpenUpload = () => {
    setActiveTab('contracts')
  }

  // Guarded actions that require authentication & active subscription
  const handleGuardedUpload = async (file) => {
    if (!isAuthenticated) {
      openAuthModal('register', 'pro', 'Please sign in or start a free trial to upload your custom contracts.')
      return
    }
    await onUploadFile(file)
  }

  const handleGuardedStartAnalysis = async (contractId) => {
    if (!isAuthenticated) {
      openAuthModal('register', 'pro', 'Please sign in or start a free trial to analyze contracts.')
      return
    }
    if (isExpired && !isDemoData) {
      onOpenPricing()
      return
    }
    await onStartAnalysis(contractId)
  }

  return (
    <div className="min-h-screen bg-[#080B0A] text-[#F2F5F0] flex flex-col selection:bg-[#C5F5D5] selection:text-[#080B0A]">
      {/* Top Header & Tab Navigation */}
      <Navigation
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        connectionStatus={connectionStatus}
        onRecheckConnection={onRecheckConnection}
        onReturnToLanding={onReturnToLanding}
        isDemoData={isDemoData}
        contractFilename={contract?.filename}
        onOpenUpload={handleOpenUpload}
        onLoadDemo={onLoadDemo}
        isAnalyzing={isAnalyzing}
        onOpenPricing={onOpenPricing}
      />

      {/* Main Workspace Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
        {/* Expired Subscription Notice Banner */}
        {isExpired && !isDemoData && (
          <div className="mb-6 p-4 rounded-2xl border border-[#F87171]/40 bg-[#180E10] text-[#F87171] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono">
            <div className="flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full bg-[#F87171] animate-pulse shrink-0" />
              <span>
                <strong>SUBSCRIPTION EXPIRED:</strong> Your free trial or monthly period has concluded. Existing evaluated records remain viewable, but new AI analyses require an active subscription.
              </span>
            </div>
            <button
              onClick={onOpenPricing}
              className="px-4 py-1.5 rounded-lg bg-[#C5F5D5] text-[#080B0A] font-semibold hover:bg-[#A8E6BF] transition-all shrink-0"
            >
              Renew / Upgrade Plan &rarr;
            </button>
          </div>
        )}

        {/* Error Banner */}
        <ErrorBanner
          error={error}
          onDismiss={onDismissError}
          onRetry={onRetryLastAction}
          onLoadDemo={onLoadDemo}
        />

        {/* Tab Views */}
        {activeTab === 'overview' && (
          <OverviewView
            analysis={analysis}
            contract={contract}
            isDemoData={isDemoData}
            onNavigateTab={setActiveTab}
            onNavigateToFinding={handleNavigateToFinding}
            onOpenUpload={handleOpenUpload}
            onLoadDemo={onLoadDemo}
          />
        )}

        {activeTab === 'contracts' && (
          <ContractsView
            contract={contract}
            analysis={analysis}
            isDemoData={isDemoData}
            onUploadFile={handleGuardedUpload}
            onStartAnalysis={handleGuardedStartAnalysis}
            isUploading={isUploading}
            isAnalyzing={isAnalyzing}
          />
        )}

        {activeTab === 'risk' && (
          <RiskDashboardView
            analysis={analysis}
            onNavigateToFinding={handleNavigateToFinding}
            onOpenUpload={handleOpenUpload}
            onLoadDemo={onLoadDemo}
          />
        )}

        {activeTab === 'evidence' && (
          <EvidenceExplorerView
            analysis={analysis}
            initialSelectedFinding={selectedFinding}
            onOpenUpload={handleOpenUpload}
            onLoadDemo={onLoadDemo}
          />
        )}

        {activeTab === 'obligations' && (
          <ObligationsView
            obligations={analysis?.obligations || []}
            onOpenUpload={handleOpenUpload}
            onLoadDemo={onLoadDemo}
          />
        )}

        {activeTab === 'policy' && (
          <PolicyComparisonView
            analysis={analysis}
            onOpenUpload={handleOpenUpload}
            onLoadDemo={onLoadDemo}
          />
        )}

        {activeTab === 'graph' && (
          <KnowledgeGraphView
            analysis={analysis}
            contract={contract}
            onNavigateToFinding={handleNavigateToFinding}
            onNavigateTab={setActiveTab}
            onOpenUpload={handleOpenUpload}
            onLoadDemo={onLoadDemo}
          />
        )}

        {activeTab === 'billing' && (
          <BillingView onOpenPricing={onOpenPricing} />
        )}

        {activeTab === 'company' && (
          <CompanyWorkspaceView
            onSwitchToContracts={() => setActiveTab('contracts')}
            onOpenDemo={onLoadDemo}
          />
        )}
      </main>

      {/* Synchronous Analysis Progress Modal */}
      <AnalysisProgressModal isOpen={isAnalyzing} />

      {/* Minimal Footer */}
      <footer className="border-t border-[rgba(197,245,213,0.08)] py-6 px-6 text-center text-xs text-[#8A9B91]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-editorial text-lg text-[#C5F5D5] tracking-wider">VERITAS AI</span>
            <span className="font-mono text-[11px]">· ENTERPRISE CONTRACT INTELLIGENCE</span>
          </div>
          <div className="text-[11px] font-mono text-[#8A9B91]/70">
            Decision support system. Requires qualified human legal review before contract execution.
          </div>
        </div>
      </footer>
    </div>
  )
}
