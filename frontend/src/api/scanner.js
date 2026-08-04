import { apiClient } from './client'

export const scannerApi = {
  run: (payload) => apiClient.post('/scanner/run', payload).then((r) => r.data),
}
