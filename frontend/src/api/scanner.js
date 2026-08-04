import { apiClient } from './client'

export const scannerApi = {
  run: (payload) => apiClient.post('/scanner/run', payload).then((r) => r.data),
  dayPrep: (payload) => apiClient.post('/scanner/day-prep', payload).then((r) => r.data),
}
