import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query'
import { catalogApi } from './catalog'
import { backtestsApi } from './backtests'
import { levelsApi } from './levels'
import { signalsApi } from './signals'
import { watchesApi } from './watches'
import { levelWatchesApi } from './levelWatches'
import { scannerApi } from './scanner'

// --- Catalog ---

export function useIndicators() {
  return useQuery({ queryKey: ['catalog', 'indicators'], queryFn: catalogApi.indicators })
}

export function useFilters() {
  return useQuery({ queryKey: ['catalog', 'filters'], queryFn: catalogApi.filters })
}

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

export function useDailyLevels() {
  return useMutation({ mutationFn: levelsApi.get })
}

export function useLevelsBacktest() {
  return useMutation({ mutationFn: levelsApi.backtest })
}

export function useLevelsDayReports() {
  return useMutation({ mutationFn: levelsApi.dayReports })
}

// --- Live Signal ---

// One query per ticker (each {symbol, interval}) so every selected
// ticker's signal refreshes independently -- a slow/failing check for
// one symbol doesn't block or blank out the others.
export function useSignalChecks(tickers, strategyName, strategyParams, executionSettings) {
  return useQueries({
    queries: (tickers || []).map((ticker) => ({
      queryKey: ['signals', 'check', ticker.symbol, ticker.interval, strategyName, strategyParams, executionSettings],
      queryFn: () =>
        signalsApi.check({
          symbol: ticker.symbol,
          interval: ticker.interval,
          strategy_name: strategyName,
          strategy_params: strategyParams,
          execution: executionSettings,
        }),
      // Matches the backend Poller's own 30s tick cadence -- each check
      // triggers a real multi-second Tastytrade historical-bar fetch
      // server-side, so this shouldn't poll more aggressively than that.
      refetchInterval: 30000,
    })),
  })
}

// --- Alerts (Telegram) ---

export function useWatches() {
  return useQuery({ queryKey: ['watches'], queryFn: watchesApi.list })
}

export function useCreateWatch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: watchesApi.create,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watches'] }),
  })
}

export function useDeleteWatch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: watchesApi.remove,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watches'] }),
  })
}

export function useLevelWatches() {
  return useQuery({ queryKey: ['level-watches'], queryFn: levelWatchesApi.list })
}

export function useCreateLevelWatch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: levelWatchesApi.create,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['level-watches'] }),
  })
}

export function useDeleteLevelWatch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: levelWatchesApi.remove,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['level-watches'] }),
  })
}

// --- Scanner ---

export function useRunScanner() {
  return useMutation({ mutationFn: scannerApi.run })
}

export function useRunDayPrep() {
  return useMutation({ mutationFn: scannerApi.dayPrep })
}
