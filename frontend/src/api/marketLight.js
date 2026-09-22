import { apiClient } from './client'

export const marketLightApi = {
  get: (timeframe) =>
    apiClient.get('/market-light', { params: { timeframe } }).then((r) => r.data),
}
