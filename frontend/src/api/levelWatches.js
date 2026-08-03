import { apiClient } from './client'

export const levelWatchesApi = {
  list: () => apiClient.get('/level-watches').then((r) => r.data),
  create: (symbol) => apiClient.post('/level-watches', { symbol }).then((r) => r.data),
  remove: (id) => apiClient.delete(`/level-watches/${id}`),
}
