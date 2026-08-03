import { apiClient } from './client'

export const watchesApi = {
  list: () => apiClient.get('/watches').then((r) => r.data),
  create: (payload) => apiClient.post('/watches', payload).then((r) => r.data),
  remove: (id) => apiClient.delete(`/watches/${id}`),
}
