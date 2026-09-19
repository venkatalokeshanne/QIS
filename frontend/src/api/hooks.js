import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { catalogApi } from './catalog'
import { backtestsApi } from './backtests'
import { dailySelectionApi } from './dailySelection'
import { levelsApi } from './levels'
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

// --- Scanner ---

export function useRunScanner() {
  return useMutation({ mutationFn: scannerApi.run })
}

export function useRunDayPrep() {
  return useMutation({ mutationFn: scannerApi.dayPrep })
}

// --- Daily Strategy Selector ---

export function useCalibrateTickers() {
  return useMutation({ mutationFn: dailySelectionApi.calibrate })
}

export function useRunDailySelection() {
  return useMutation({ mutationFn: dailySelectionApi.run })
}

export function useRunSelectionBacktest() {
  return useMutation({ mutationFn: dailySelectionApi.backtest })
}
