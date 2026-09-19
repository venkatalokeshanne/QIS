import { apiClient } from './client'

export const strategySelectionApi = {
  // GET /api/strategy-selection/{ticker}?timeframe=&timestamp=&include_premarket=
  select: ({ ticker, timeframe, timestamp, includePremarket }) =>
    apiClient
      .get(`/strategy-selection/${encodeURIComponent(ticker)}`, {
        params: {
          timeframe,
          include_premarket: includePremarket,
          ...(timestamp ? { timestamp } : {}),
        },
        // regime detection + qualification over the whole registry
        timeout: 120000,
      })
      .then((r) => r.data),
  catalog: () => apiClient.get('/strategy-selection/catalog').then((r) => r.data),
}
