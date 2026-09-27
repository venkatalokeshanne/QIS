import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { catalogApi } from './catalog'
import { backtestsApi } from './backtests'
import { marketLightApi } from './marketLight'

// --- Catalog ---

export function useStrategies() {
  return useQuery({ queryKey: ['catalog', 'strategies'], queryFn: catalogApi.strategies })
}

export function useMetricDefinitions() {
  return useQuery({ queryKey: ['catalog', 'metrics'], queryFn: catalogApi.metrics })
}

// --- Backtests ---

export function useRunBacktest() {
  return useMutation({ mutationFn: backtestsApi.run })
}

// Fetched lazily -- only when the Historical Performance popup for a
// specific strategy is actually open (see Results.jsx) -- computing
// this for every strategy on every backtest run doubled the request's
// network cost (two ~20s-capped fetches instead of one) for 34
// strategies nobody ever looks at.
export function useHistoricalPerformance({ symbol, interval, strategyName, strategyParams, execution, endDate, enabled }) {
  return useQuery({
    queryKey: ['historical-performance', symbol, interval, strategyName, strategyParams, execution, endDate],
    queryFn: () =>
      backtestsApi.historicalPerformance({
        symbol,
        interval,
        strategy_name: strategyName,
        strategy_params: strategyParams,
        execution,
        end_date: endDate,
      }),
    enabled,
    staleTime: 5 * 60 * 1000,
  })
}

// --- Daily Levels ---

// --- Daily Strategy Selector ---

// --- Strategy Selection Engine ---

// --- Market light ---

export function useMarketLight(timeframe) {
  return useQuery({
    queryKey: ['market-light', timeframe],
    queryFn: () => marketLightApi.get(timeframe),
    refetchInterval: 5 * 60 * 1000,
    staleTime: 60 * 1000,
  })
}
