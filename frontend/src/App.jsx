import React, { useState, useEffect, useCallback, useRef } from 'react'
import LandingPage from './components/LandingPage'
import Workspace from './components/Workspace'
import PricingPage from './components/PricingPage'
import AuthModal from './components/AuthModal'
import QuotaExhaustedModal from './components/QuotaExhaustedModal'
import ErrorBoundary from './components/ErrorBoundary'
import { useAuth } from './context/useAuth'
import { AuthProvider } from './context/AuthContext'
import {
  checkHealth,
  uploadContract,
  analyzeContract,
  getDemoAnalysis,
  getAnalysis,
} from './api/client'

function MainApp() {
  const [currentView, setCurrentView] = useState('landing') // 'landing' | 'workspace' | 'pricing'
  const [previousView, setPreviousView] = useState('landing')
  const [connectionStatus, setConnectionStatus] = useState('checking') // 'checking' | 'online' | 'offline'

  // Application data
  const [contract, setContract] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [isDemoData, setIsDemoData] = useState(false)

  // Loading & Progress states
  const [isUploading, setIsUploading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  // Error handling
  const [error, setError] = useState(null)
  const lastActionRef = useRef(null)
  const requestBusyRef = useRef(false)
  const { user, authLoading } = useAuth()
  const userId = user?.id
  const previousOwnerRef = useRef(null)

  // Retain only a reference, never contract text, and reauthorize retrieval on refresh.
  useEffect(() => {
    if (authLoading) return
    let cancelled = false
    const previousOwner = previousOwnerRef.current
    previousOwnerRef.current = userId
    if (previousOwner && previousOwner !== userId) {
      lastActionRef.current = null
      Promise.resolve().then(() => {
        if (!cancelled) { setContract(null); setAnalysis(null); setError(null); setIsDemoData(false) }
      })
    }
    try {
      const saved = JSON.parse(sessionStorage.getItem('veritas_last_analysis') || 'null')
      if (saved && userId === saved.userId) {
        getAnalysis(saved.analysisId).then((data) => {
          if (!cancelled) { setAnalysis(data); setIsDemoData(false); setCurrentView('workspace') }
        }).catch(() => { if (!cancelled) sessionStorage.removeItem('veritas_last_analysis') })
      } else {
        sessionStorage.removeItem('veritas_last_analysis')
        if (saved) Promise.resolve().then(() => {
          if (!cancelled) { setAnalysis(null); setContract(null) }
        })
      }
    } catch { /* Storage can be unavailable. */ }
    return () => { cancelled = true }
  }, [userId, authLoading])

  const handleOpenPricing = () => {
    setPreviousView(currentView === 'pricing' ? 'landing' : currentView)
    setCurrentView('pricing')
  }

  const handleReturnFromPricing = () => {
    setCurrentView(previousView === 'pricing' ? 'landing' : previousView)
  }

  // Check backend health on mount
  const verifyConnection = useCallback(async (signal) => {
    try {
      const data = await checkHealth(signal)
      if (data && data.status === 'ok') {
        setConnectionStatus('online')
      } else {
        setConnectionStatus('offline')
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setConnectionStatus('offline')
      }
    }
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    Promise.resolve().then(() => {
      if (!controller.signal.aborted) {
        verifyConnection(controller.signal)
      }
    })
    return () => controller.abort()
  }, [verifyConnection])

  // Handle uploading PDF contract
  const handleUploadFile = async (file) => {
    if (requestBusyRef.current) return
    requestBusyRef.current = true
    const requestOwner = userId
    setIsUploading(true)
    setError(null)
    lastActionRef.current = () => handleUploadFile(file)

    try {
      const contractData = await uploadContract(file)
      if (previousOwnerRef.current !== requestOwner) return
      setContract(contractData)
      setAnalysis(null)
      setIsDemoData(false)
    } catch (err) {
      if (previousOwnerRef.current !== requestOwner) return
      setError(err)
    } finally {
      requestBusyRef.current = false
      setIsUploading(false)
    }
  }

  // Handle starting live analysis
  const handleStartAnalysis = async (contractId) => {
    if (!contractId || requestBusyRef.current) return
    requestBusyRef.current = true
    const requestOwner = userId
    setIsAnalyzing(true)
    setError(null)
    lastActionRef.current = () => handleStartAnalysis(contractId)

    try {
      const analysisData = await analyzeContract(contractId)
      if (previousOwnerRef.current !== requestOwner) return
      setAnalysis(analysisData)
      try { sessionStorage.setItem('veritas_last_analysis', JSON.stringify({ analysisId: analysisData.analysis_id, userId: user?.id })) } catch { /* Storage unavailable. */ }
      setIsDemoData(false)
    } catch (err) {
      if (previousOwnerRef.current !== requestOwner) return
      setError(err)
      // If error payload indicates a failure record was persisted, attempt to fetch it
      if (err.analysisId && err.failureRecorded) {
        try {
          const failureRecord = await getAnalysis(err.analysisId)
          if (failureRecord && previousOwnerRef.current === requestOwner) {
            setAnalysis(failureRecord)
          }
        } catch {
          // Keep primary error
        }
      }
    } finally {
      requestBusyRef.current = false
      setIsAnalyzing(false)
    }
  }

  // Handle loading offline demo data
  const handleLoadDemo = async () => {
    if (requestBusyRef.current) return
    setError(null)
    lastActionRef.current = handleLoadDemo
    try {
      const demoData = await getDemoAnalysis()
      try { sessionStorage.removeItem('veritas_last_analysis') } catch { /* Storage unavailable. */ }
      setContract(demoData.contract)
      setAnalysis(demoData.analysis)
      setIsDemoData(true)
      setCurrentView('workspace')
    } catch (err) {
      setError(err)
      setCurrentView('workspace')
    }
  }

  // Retry last action
  const handleRetryLastAction = () => {
    if (lastActionRef.current) {
      lastActionRef.current()
    }
  }

  return (
    <ErrorBoundary
      onReset={() => setCurrentView('landing')}
      onLoadDemo={handleLoadDemo}
    >
      <div className="w-full min-h-screen bg-[#080B0A] text-[#F2F5F0]">
        {currentView === 'landing' && (
          <LandingPage
            onLaunchWorkspace={() => setCurrentView('workspace')}
            onLoadDemo={handleLoadDemo}
            onOpenPricing={handleOpenPricing}
          />
        )}

        {currentView === 'pricing' && (
          <PricingPage onReturn={handleReturnFromPricing} />
        )}

        {currentView === 'workspace' && (
          <Workspace
            analysis={analysis}
            contract={contract}
            isDemoData={isDemoData}
            connectionStatus={connectionStatus}
            onRecheckConnection={() => verifyConnection()}
            onReturnToLanding={() => setCurrentView('landing')}
            onUploadFile={handleUploadFile}
            onStartAnalysis={handleStartAnalysis}
            onLoadDemo={handleLoadDemo}
            isUploading={isUploading}
            isAnalyzing={isAnalyzing}
            error={error}
            onDismissError={() => setError(null)}
            onRetryLastAction={handleRetryLastAction}
            onOpenPricing={handleOpenPricing}
          />
        )}

        {/* Global Modals */}
        <AuthModal onSuccess={() => setCurrentView('workspace')} />
        <QuotaExhaustedModal />
      </div>
    </ErrorBoundary>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  )
}
