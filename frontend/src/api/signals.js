import { apiClient } from './client'

export const signalsApi = {
  check: (payload) => apiClient.post('/signals/check', payload).then((r) => r.data),
}
