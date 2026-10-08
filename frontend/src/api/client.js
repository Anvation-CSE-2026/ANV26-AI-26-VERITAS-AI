/**
 * VERITAS AI - API Client
 * Integrated strictly with backend contracts in:
 * - docs/frontend-api-contract.md
 * - docs/BILLING_API_CONTRACT.md
 */

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

const TOKEN_STORAGE_KEY = 'veritas_jwt_token'

/**
 * Token management helpers
 */
export function getStoredToken() {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY)
  } catch {
    return null
  }
}

export function setStoredToken(token) {
  try {
    if (token) {
      localStorage.setItem(TOKEN_STORAGE_KEY, token)
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
    }
  } catch {
    // LocalStorage unavailable
  }
}

export function clearStoredToken() {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
  } catch {
    // LocalStorage unavailable
  }
}

export function getAuthHeaders(extraHeaders = {}) {
  const token = getStoredToken()
  const headers = { ...extraHeaders }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

/**
 * Format structured error response from FastAPI
 */
export async function parseErrorResponse(response) {
  let errorData = null
  try {
    errorData = await response.json()
  } catch {
    return {
      status: response.status,
      message: `HTTP ${response.status}: ${response.statusText || 'Server Error'}`,
      detail: null,
    }
  }

  const detail = errorData?.detail

  // Handle case: detail is a string
  if (typeof detail === 'string') {
    return {
      status: response.status,
      message: detail,
      detail,
    }
  }

  // Handle case: detail is a validation array (HTTP 422)
  if (Array.isArray(detail)) {
    const messages = detail.map((err) => `${err.loc?.join('.') || 'field'}: ${err.msg}`).join(', ')
    return {
      status: response.status,
      message: messages || 'Validation error in request payload.',
      detail,
      validationErrors: detail,
    }
  }

  // Handle case: detail is a structured error object (Gemini, quota exhausted, etc.)
  if (detail && typeof detail === 'object') {
    return {
      status: response.status,
      message: detail.message || 'Operation failed on backend.',
      state: detail.state,
      analysesUsed: detail.analyses_used,
      analysesLimit: detail.analyses_limit,
      billingPeriod: detail.billing_period,
      upgradeRequired: detail.upgrade_required,
      failedStage: detail.failed_stage,
      errorCategory: detail.error_category,
      analysisId: detail.analysis_id,
      failureRecorded: detail.failure_recorded,
      verificationRejections: detail.verification_rejections || [],
      geminiAttempts: detail.gemini_attempts,
      upstreamStatus: detail.upstream_http_status,
      syntheticDemoCommand: detail.synthetic_demo_command,
      detail,
    }
  }

  return {
    status: response.status,
    message: errorData?.message || `HTTP ${response.status}: Unexpected error`,
    detail,
  }
}

/**
 * GET /health
 */
export async function checkHealth(signal) {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: signal || AbortSignal.timeout(5000),
    })
    if (!res.ok) {
      throw await parseErrorResponse(res)
    }
    return await res.json()
  } catch (err) {
    if (err.name === 'AbortError') throw err
    if (err.message && err.status) throw err
    throw { status: 0, message: 'Backend unreachable. Please verify FastAPI is running at ' + API_BASE_URL }
  }
}

// =========================================================
// AUTHENTICATION API
// =========================================================

/**
 * POST /api/auth/register
 */
export async function registerUser(email, password, signal) {
  const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({ email, password }),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  const data = await res.json()
  if (data?.access_token) {
    setStoredToken(data.access_token)
  }
  return data
}

/**
 * POST /api/auth/login
 */
export async function loginUser(email, password, signal) {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({ email, password }),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  const data = await res.json()
  if (data?.access_token) {
    setStoredToken(data.access_token)
  }
  return data
}

/**
 * GET /api/auth/me
 */
export async function getCurrentUser(signal) {
  const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
    method: 'GET',
    headers: getAuthHeaders({ Accept: 'application/json' }),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

/**
 * POST /api/auth/logout
 */
export async function logoutUser(signal) {
  try {
    await fetch(`${API_BASE_URL}/api/auth/logout`, {
      method: 'POST',
      headers: getAuthHeaders({ Accept: 'application/json' }),
      signal,
    })
  } finally {
    clearStoredToken()
  }
  return { success: true }
}

// =========================================================
// SUBSCRIPTION & BILLING API
// =========================================================

/**
 * GET /api/billing/plans
 */
export async function getBillingPlans(signal) {
  const res = await fetch(`${API_BASE_URL}/api/billing/plans`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

/**
 * POST /api/billing/trial/start
 * Body: { plan: "standard" | "pro" }
 */
export async function startFreeTrial(plan = 'standard', signal) {
  const res = await fetch(`${API_BASE_URL}/api/billing/trial/start`, {
    method: 'POST',
    headers: getAuthHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    }),
    body: JSON.stringify({ plan }),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

/**
 * GET /api/billing/subscription
 */
export async function getUserSubscription(signal) {
  const res = await fetch(`${API_BASE_URL}/api/billing/subscription`, {
    method: 'GET',
    headers: getAuthHeaders({ Accept: 'application/json' }),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

/**
 * POST /api/billing/checkout
 * Body: { plan: "standard" | "pro" }
 */
export async function createCheckout(plan = 'pro', signal) {
  const res = await fetch(`${API_BASE_URL}/api/billing/checkout`, {
    method: 'POST',
    headers: getAuthHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    }),
    body: JSON.stringify({ plan }),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

/**
 * POST /api/billing/verify
 * Body: { razorpay_payment_id, razorpay_subscription_id, razorpay_signature }
 */
export async function verifyPayment(paymentData, signal) {
  const res = await fetch(`${API_BASE_URL}/api/billing/verify`, {
    method: 'POST',
    headers: getAuthHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    }),
    body: JSON.stringify(paymentData),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

/**
 * POST /api/billing/cancel
 */
export async function cancelSubscription(signal) {
  const res = await fetch(`${API_BASE_URL}/api/billing/cancel`, {
    method: 'POST',
    headers: getAuthHeaders({
      Accept: 'application/json',
    }),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

// =========================================================
// CONTRACT ANALYSIS API (AUTH-AWARE)
// =========================================================

/**
 * POST /api/contracts/upload
 * Content-Type: multipart/form-data
 * Returns Contract (HTTP 201)
 */
export async function uploadContract(file, signal) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE_URL}/api/contracts/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

/**
 * POST /api/analyze
 * Content-Type: application/json
 * Body: { contract_id }
 * Returns Analysis (HTTP 200)
 */
export async function analyzeContract(contractId, signal) {
  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: getAuthHeaders({
      'Content-Type': 'application/json',
      Accept: 'application/json',
    }),
    body: JSON.stringify({ contract_id: contractId }),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

/**
 * GET /api/analysis/{analysis_id}
 * Returns Analysis (status: "completed"|"partial") or AnalysisFailure (status: "failed")
 */
export async function getAnalysis(analysisId, signal) {
  const res = await fetch(`${API_BASE_URL}/api/analysis/${encodeURIComponent(analysisId)}`, {
    method: 'GET',
    headers: getAuthHeaders({ Accept: 'application/json' }),
    signal,
  })

  if (!res.ok) {
    throw await parseErrorResponse(res)
  }

  return await res.json()
}

import fallbackDemoData from './demoData.json'

/**
 * GET /api/demo/analysis
 * Returns DemoArtifact (HTTP 200)
 * Seamlessly falls back to verified offline snapshot if backend is unreachable
 */
export async function getDemoAnalysis(signal) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/demo/analysis`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal,
    })

    if (res.ok) {
      return await res.json()
    }
  } catch {
    // Return offline snapshot if backend server is not running
  }

  return fallbackDemoData
}
