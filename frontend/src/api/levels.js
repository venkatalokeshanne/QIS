import { apiClient } from './client'

export const levelsApi = {
  get: (symbol) => apiClient.get(`/levels/${encodeURIComponent(symbol)}`).then((r) => r.data),
  backtest: (symbol) => apiClient.post('/levels/backtest', { symbol }).then((r) => r.data),
  dayReports: ({ symbol, dates }) =>
    apiClient.post('/levels/backtest/days', { symbol, dates }).then((r) => r.data),
}
