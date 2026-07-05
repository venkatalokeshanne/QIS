import { apiClient } from './client'

// No CSV upload on mobile (per user's choice) -- data only ever comes
// in live via Twelve Data, so this is a smaller surface than the web
// app's datasets.js.
export const datasetsApi = {
  list: () => apiClient.get('/datasets').then((r) => r.data),

  fetchFromTwelvedata: (params) => apiClient.post('/datasets/twelvedata', params).then((r) => r.data),

  remove: (id) => apiClient.delete(`/datasets/${id}`),
}
