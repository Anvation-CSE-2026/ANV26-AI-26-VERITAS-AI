import React, { useState, useEffect, useCallback } from 'react'
import { AuthContext } from './authContextDef'
import {
  getStoredToken,
  getCurrentUser,
  registerUser,
  loginUser,
  logoutUser,
  getBillingPlans,
  getUserSubscription,
  startFreeTrial,
  createCheckout,
  verifyPayment,
  cancelSubscription,
} from '../api/client'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [subscription, setSubscription] = useState(null)
  const [plans, setPlans] = useState([])
  const [authLoading, setAuthLoading] = useState(true)
  const [plansLoading, setPlansLoading] = useState(true)
  const [checkoutLoading, setCheckoutLoading] = useState(false)

  // Auth modal management
  const [authModal, setAuthModal] = useState({
    isOpen: false,
    mode: 'login', // 'login' | 'register' | 'trial'
    plan: 'pro',
    message: null,
  })

  // Quota modal management
  const [quotaModal, setQuotaModal] = useState({
    isOpen: false,
    data: null,
  })

  // Notification toast
  const [toast, setToast] = useState(null)

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => {
      setToast(null)
    }, 4500)
  }, [])

  // 1. Fetch available plans from backend on mount (public)
  const fetchPlans = useCallback(async () => {
    try {
      setPlansLoading(true)
      const data = await getBillingPlans()
      if (data?.plans) {
        setPlans(data.plans)
      }
    } catch {
      // Keep empty if server unavailable
    } finally {
      setPlansLoading(false)
    }
  }, [])

  // 2. Fetch active user subscription
  const refreshSubscription = useCallback(async () => {
    const token = getStoredToken()
    if (!token) {
      setSubscription(null)
      return null
    }

    try {
      const sub = await getUserSubscription()
      setSubscription(sub)
      return sub
    } catch {
      setSubscription(null)
      return null
    }
  }, [])

  // 3. Initialize user from stored JWT session
  useEffect(() => {
    let isMounted = true

    async function initAuthAndPlans() {
      // 1. Fetch plans
      try {
        const plansData = await getBillingPlans()
        if (isMounted && plansData?.plans) {
          setPlans(plansData.plans)
        }
      } catch {
        // Fallback
      } finally {
        if (isMounted) setPlansLoading(false)
      }

      // 2. Fetch auth user
      const token = getStoredToken()
      if (!token) {
        if (isMounted) setAuthLoading(false)
        return
      }

      try {
        const userData = await getCurrentUser()
        if (isMounted) {
          setUser(userData)
        }
        // Fetch subscription if user valid
        try {
          const subData = await getUserSubscription()
          if (isMounted) setSubscription(subData)
        } catch {
          // No active subscription
        }
      } catch {
        // Token invalid or expired
        if (isMounted) {
          setUser(null)
          setSubscription(null)
        }
      } finally {
        if (isMounted) setAuthLoading(false)
      }
    }

    initAuthAndPlans()

    return () => {
      isMounted = false
    }
  }, [])

  // Login handler
  const handleLogin = async (email, password) => {
    const data = await loginUser(email, password)
    setUser(data.user)
    try {
      const sub = await getUserSubscription()
      setSubscription(sub)
    } catch {
      setSubscription(null)
    }
    showToast(`Welcome back, ${data.user.email}`)
    return data
  }

  // Register handler
  const handleRegister = async (email, password) => {
    const data = await registerUser(email, password)
    setUser(data.user)
    showToast('Account created successfully!')
    return data
  }

  // Logout handler
  const handleLogout = async () => {
    try {
      await logoutUser()
    } catch {
      // Ignored
    } finally {
      setUser(null)
      setSubscription(null)
      showToast('You have been logged out.')
    }
  }

  // Free Trial start handler
  const handleStartTrial = async (plan = 'standard') => {
    const sub = await startFreeTrial(plan)
    setSubscription(sub)
    if (user) {
      setUser((prev) => (prev ? { ...prev, trial_used: true } : prev))
    }
    showToast(`Your 30-day ${plan.toUpperCase()} trial is now active!`)
    return sub
  }

  // Helper to ensure Razorpay checkout.js is loaded
  const ensureRazorpayLoaded = async () => {
    if (window.Razorpay) return true
    return new Promise((resolve) => {
      const existing = document.querySelector('script[src*="checkout.razorpay.com"]')
      if (existing) {
        existing.addEventListener('load', () => resolve(!!window.Razorpay))
        existing.addEventListener('error', () => resolve(false))
        setTimeout(() => resolve(!!window.Razorpay), 2500)
      } else {
        const script = document.createElement('script')
        script.src = 'https://checkout.razorpay.com/v1/checkout.js'
        script.onload = () => resolve(true)
        script.onerror = () => resolve(false)
        document.body.appendChild(script)
      }
    })
  }

  // Razorpay Checkout handler
  const handleInitiateCheckout = async (plan = 'pro') => {
    setCheckoutLoading(true)
    try {
      const isLoaded = await ensureRazorpayLoaded()
      if (!isLoaded || !window.Razorpay) {
        throw new Error('Razorpay SDK could not be loaded. Please check your internet connection.')
      }

      // 1. Request subscription checkout session from backend
      const checkoutData = await createCheckout(plan)

      return new Promise((resolve, reject) => {
        // Official Razorpay Subscriptions Checkout configuration:
        // Do not pass amount/currency for recurring subscriptions;
        // Razorpay derives them directly from the plan associated with subscription_id.
        const options = {
          key: checkoutData.razorpay_key_id,
          subscription_id: checkoutData.subscription_id,
          name: checkoutData.name || 'VERITAS AI',
          description: checkoutData.description || `VERITAS AI ${plan.toUpperCase()} Plan`,
          prefill: {
            email: user?.email || '',
          },
          theme: {
            color: '#C5F5D5',
            backdrop_color: '#080B0A',
          },
          handler: async (response) => {
            try {
              // 2. Client verification against backend HMAC check
              const verifyRes = await verifyPayment({
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_subscription_id: response.razorpay_subscription_id,
                razorpay_signature: response.razorpay_signature,
              })

              if (verifyRes.success) {
                setSubscription(verifyRes.subscription)
                showToast(`Payment verified! ${plan.toUpperCase()} plan is now active.`)
                resolve(verifyRes)
              } else {
                const failMsg = verifyRes.message || 'Payment verification failed.'
                showToast(failMsg, 'error')
                reject(new Error(failMsg))
              }
            } catch (err) {
              const msg = err?.message || err?.detail || 'Server payment verification failed.'
              showToast(msg, 'error')
              reject(err)
            } finally {
              setCheckoutLoading(false)
            }
          },
          modal: {
            ondismiss: () => {
              setCheckoutLoading(false)
              reject({ message: 'Checkout cancelled by user.', dismissed: true })
            },
          },
        }

        try {
          const rzp = new window.Razorpay(options)
          rzp.on('payment.failed', (failRes) => {
            setCheckoutLoading(false)
            const failMsg = failRes?.error?.description || 'Razorpay payment transaction failed.'
            showToast(failMsg, 'error')
            reject({
              message: failMsg,
              error: failRes?.error,
            })
          })
          rzp.open()
        } catch (openErr) {
          setCheckoutLoading(false)
          showToast(openErr?.message || 'Failed to open Razorpay modal.', 'error')
          reject(openErr)
        }
      })
    } catch (err) {
      setCheckoutLoading(false)
      const isDismissed = err?.dismissed || err?.message === 'Checkout cancelled by user.'
      if (!isDismissed) {
        const errorMsg =
          err?.message ||
          err?.detail ||
          'Failed to initialize checkout. Please try again.'
        showToast(errorMsg, 'error')
        console.error('[Billing Checkout Diagnostic]:', errorMsg)
      }
      throw err
    }
  }

  // Cancel subscription handler
  const handleCancelSubscription = async () => {
    const res = await cancelSubscription()
    if (res?.subscription) {
      setSubscription(res.subscription)
    }
    showToast('Your subscription has been cancelled.', 'info')
    return res
  }

  // Modal controls
  const openAuthModal = (mode = 'login', plan = 'pro', message = null) => {
    setAuthModal({
      isOpen: true,
      mode,
      plan,
      message,
    })
  }

  const closeAuthModal = () => {
    setAuthModal((prev) => ({ ...prev, isOpen: false, message: null }))
  }

  const openQuotaModal = (data) => {
    setQuotaModal({
      isOpen: true,
      data,
    })
  }

  const closeQuotaModal = () => {
    setQuotaModal({
      isOpen: false,
      data: null,
    })
  }

  const value = {
    user,
    subscription,
    plans,
    authLoading,
    plansLoading,
    checkoutLoading,
    isAuthenticated: !!user,
    isTrialActive: subscription?.status === 'trialing' && subscription?.is_active,
    isSubscribed: subscription?.status === 'active' && subscription?.is_active,
    isExpired: subscription?.status === 'expired' || (subscription && !subscription.is_active),
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    startTrial: handleStartTrial,
    initiateCheckout: handleInitiateCheckout,
    cancelSubscription: handleCancelSubscription,
    refreshSubscription,
    fetchPlans,
    // Modals
    authModal,
    openAuthModal,
    closeAuthModal,
    quotaModal,
    openQuotaModal,
    closeQuotaModal,
    // Toast
    toast,
    showToast,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
      {/* Global Toast */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3 rounded-xl border border-[rgba(197,245,213,0.3)] bg-[#101512]/95 backdrop-blur-xl shadow-2xl text-xs font-mono tracking-wide animate-fade-in">
          <span
            className={`w-2 h-2 rounded-full ${
              toast.type === 'error'
                ? 'bg-[#F87171]'
                : toast.type === 'info'
                ? 'bg-[#A8E6BF]'
                : 'bg-[#C5F5D5]'
            }`}
          />
          <span className="text-[#F2F5F0]">{toast.message}</span>
          <button
            onClick={() => setToast(null)}
            className="ml-2 text-[#8A9B91] hover:text-[#F2F5F0]"
          >
            &times;
          </button>
        </div>
      )}
    </AuthContext.Provider>
  )
}

