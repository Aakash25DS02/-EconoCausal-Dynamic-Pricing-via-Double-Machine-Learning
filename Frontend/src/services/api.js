const API_BASE_URL = 'http://127.0.0.1:8000'

async function request(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`)

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }

  return response.json()
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

export function getPromotionEffect() {
  return request('/analysis/promotion-effect')
}