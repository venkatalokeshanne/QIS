import { apiClient } from './client'

export const backtestsApi = {
  run: (payload) => apiClient.post('/backtests/run', payload).then((r) => r.data),
}
