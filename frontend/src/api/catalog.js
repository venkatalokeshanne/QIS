import { apiClient } from './client'

export const catalogApi = {
  indicators: () => apiClient.get('/catalog/indicators').then((r) => r.data),
  filters: () => apiClient.get('/catalog/filters').then((r) => r.data),
  strategies: () => apiClient.get('/catalog/strategies').then((r) => r.data),
  metrics: () => apiClient.get('/catalog/metrics').then((r) => r.data),
}
