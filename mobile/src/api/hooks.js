import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { datasetsApi } from './datasets'
import { catalogApi } from './catalog'
import { backtestsApi } from './backtests'
import { levelsApi } from './levels'
import { watchesApi } from './watches'

// --- Datasets ---

export function useDatasets() {
  return useQuery({ queryKey: ['datasets'], queryFn: datasetsApi.list })
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

export function useLevelsDayReports() {
  return useMutation({ mutationFn: levelsApi.dayReports })
}

// --- Signal Alerts (Watches) ---

export function useWatches(pushToken) {
  return useQuery({
    queryKey: ['watches', pushToken],
    queryFn: () => watchesApi.list(pushToken),
    enabled: !!pushToken,
  })
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
    mutationFn: (id) => watchesApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watches'] }),
  })
}

export function useSendTestNotification() {
  return useMutation({ mutationFn: (pushToken) => watchesApi.sendTestNotification(pushToken) })
}
