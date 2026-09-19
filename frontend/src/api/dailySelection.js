import { apiClient } from './client'

export const dailySelectionApi = {
  calibrate: (payload) => apiClient.post('/daily-selection/calibrate', payload).then((r) => r.data),
  run: (payload) => apiClient.post('/daily-selection/run', payload).then((r) => r.data),
  backtest: (payload) => apiClient.post('/daily-selection/backtest', payload).then((r) => r.data),
}
