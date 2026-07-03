import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { datasetsApi } from './datasets'
import { catalogApi } from './catalog'
import { backtestsApi } from './backtests'
import { levelsApi } from './levels'

// --- Datasets ---

export function useDatasets() {
  return useQuery({ queryKey: ['datasets'], queryFn: datasetsApi.list })
}

export function useDataset(id) {
  return useQuery({
    queryKey: ['datasets', id],
    queryFn: () => datasetsApi.get(id),
    enabled: Boolean(id),
  })
}

export function useDatasetPreview(id, rows = 20) {
  return useQuery({
    queryKey: ['datasets', id, 'preview', rows],
    queryFn: () => datasetsApi.preview(id, rows),
    enabled: Boolean(id),
  })
}

export function useUploadDataset() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ file, name, onProgress }) => datasetsApi.upload(file, name, onProgress),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['datasets'] }),
  })
}

export function useFetchFromTwelvedata() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (params) => datasetsApi.fetchFromTwelvedata(params),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['datasets'] }),
  })
}

export function useDeleteDataset() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id) => datasetsApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['datasets'] }),
  })
}

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
