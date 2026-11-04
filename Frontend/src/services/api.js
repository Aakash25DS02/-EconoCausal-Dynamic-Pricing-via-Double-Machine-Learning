
const API_BASE_URL = 'http://127.0.0.1:8000'

async function request(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`)

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }

  return response.json()
}

async function postRequest(endpoint, body) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.detail || `API request failed: ${response.status}`
    )
  }

  return data
}

export function getHealth() {
  return request('/health')
}

export function getDataSummary() {
  return request('/data/summary')
}

export function getDataPreview() {
  return request('/data/preview')
}

export function getPromotionEffect(records = null) {
  return postRequest('/analysis/promotion-effect', {
    records: Array.isArray(records) ? records : []
  })
}

export function getPromotionEffectDML(records = null) {
  return postRequest('/analysis/promotion-effect-dml', {
    records: Array.isArray(records) ? records : []
  })
}

export async function optimizeBudgetAllocation(budget, records = null) {
  return postRequest('/allocation/optimize', {
    budget: Number(budget),
    records: Array.isArray(records) ? records : null
  })
}
