import { apiClient } from './client'

export const watchesApi = {
  create: (payload) => apiClient.post('/watches', payload).then((r) => r.data),
  list: (pushToken) => apiClient.get('/watches', { params: { expo_push_token: pushToken } }).then((r) => r.data),
  remove: (id) => apiClient.delete(`/watches/${id}`),
}
