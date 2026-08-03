import { useMutation, useQueries, useQuery } from '@tanstack/react-query'
import { catalogApi } from './catalog'
import { backtestsApi } from './backtests'
import { levelsApi } from './levels'
import { signalsApi } from './signals'

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
export function useSignalChecks(tickers, strategyName, strategyParams) {
  return useQueries({
    queries: (tickers || []).map((ticker) => ({
      queryKey: ['signals', 'check', ticker.symbol, ticker.interval, strategyName, strategyParams],
      queryFn: () =>
        signalsApi.check({
          symbol: ticker.symbol,
          interval: ticker.interval,
          strategy_name: strategyName,
          strategy_params: strategyParams,
        }),
      // Matches the backend Poller's own 30s tick cadence -- each check
      // triggers a real multi-second Tastytrade historical-bar fetch
      // server-side, so this shouldn't poll more aggressively than that.
      refetchInterval: 30000,
    })),
  })
}
