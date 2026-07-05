import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { useStrategies, useRunBacktest, useMetricDefinitions } from '../../api/hooks'
import { useResearchStore } from '../../store/useResearchStore'
import { buildRiskManagementSteps } from '../../data/trendspiderGuides'

const EMPTY_PARAMS = {}

const StrategyDetailCtx = createContext(null)

// React Navigation's nested top-tabs (Results/Charts/Tickers/Configure/
// TrendSpider/Info) are independently-mounted screens, unlike the web
// app's single StrategyDetail.jsx component that conditionally renders
// tab content with shared local `useState`. This context is the RN
// equivalent: one place holding the strategy, the shared backtest run,
// and focused-ticker state, so switching tabs doesn't lose or re-run
// anything -- exactly like the web version's single-mount behavior.
export function StrategyDetailProvider({ name, children }) {
  const { data: strategies, isLoading: strategiesLoading } = useStrategies()
  const { data: metricDefs } = useMetricDefinitions()
  const selectedDatasetIds = useResearchStore((s) => s.selectedDatasetIds)
  const executionSettings = useResearchStore((s) => s.executionSettings)
  const selectedStrategyNames = useResearchStore((s) => s.selectedStrategyNames)
  const setSelectedStrategyNames = useResearchStore((s) => s.setSelectedStrategyNames)
  const strategyParamOverrides = useResearchStore((s) => s.strategyParamOverrides)
  const setStrategyParamOverride = useResearchStore((s) => s.setStrategyParamOverride)
  const resetStrategyParams = useResearchStore((s) => s.resetStrategyParams)
  const breakdownByMonth = useResearchStore((s) => s.breakdownByMonth)
  const setBreakdownByMonth = useResearchStore((s) => s.setBreakdownByMonth)
  const runMutation = useRunBacktest()

  const [focusedDatasetId, setFocusedDatasetId] = useState(null)

  const strategy = strategies?.find((s) => s.name === name)
  const paramsOverride = strategyParamOverrides[name] || EMPTY_PARAMS
  const hasOverride = Object.keys(paramsOverride).length > 0
  const effectiveParams = useMemo(
    () => ({ ...(strategy?.default_params || {}), ...paramsOverride }),
    [strategy, paramsOverride]
  )

  const runNow = () => {
    if (selectedDatasetIds.length === 0 || !strategy) return
    runMutation.mutate({
      dataset_ids: selectedDatasetIds,
      strategy_names: [strategy.name],
      strategy_params: { [strategy.name]: effectiveParams },
      execution: executionSettings,
      breakdown_by_month: breakdownByMonth,
    })
  }

  useEffect(() => {
    if (selectedDatasetIds.length === 0 || !strategy) return
    runMutation.mutate({
      dataset_ids: selectedDatasetIds,
      strategy_names: [strategy.name],
      strategy_params: { [strategy.name]: effectiveParams },
      execution: executionSettings,
      breakdown_by_month: breakdownByMonth,
    })
    // Re-run when the strategy, ticker selection, or its own params
    // change, but not on every execution-settings/monthly-breakdown
    // tweak elsewhere -- use "Re-run" for that.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name, selectedDatasetIds, effectiveParams])

  const datasetResults = runMutation.data?.dataset_results || []

  useEffect(() => {
    if (datasetResults.length === 0) return
    if (!datasetResults.some((d) => d.dataset_id === focusedDatasetId)) {
      setFocusedDatasetId(datasetResults[0].dataset_id)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [datasetResults])

  const metricFormatByName = useMemo(() => {
    const map = {}
    for (const m of metricDefs || []) map[m.name] = m
    return map
  }, [metricDefs])

  const addToBatch = () => {
    if (!selectedStrategyNames.includes(name)) {
      setSelectedStrategyNames([...selectedStrategyNames, name])
    }
  }

  const focusedResult = datasetResults.find((d) => d.dataset_id === focusedDatasetId)
  const result = focusedResult?.results?.[0]
  const riskManagementLines = buildRiskManagementSteps(executionSettings)

  // Ranked by overall score across every selected ticker -- each dataset's
  // own `rank` field is meaningless here since only one strategy was
  // requested per ticker (it's always 1), so this is computed locally.
  const tickerRanking = [...datasetResults]
    .map((d) => ({ dataset_id: d.dataset_id, dataset_name: d.dataset_name, result: d.results?.[0] }))
    .filter((r) => r.result)
    .sort((a, b) => (b.result.overall_score ?? -Infinity) - (a.result.overall_score ?? -Infinity))

  const value = {
    name,
    strategiesLoading,
    strategy,
    metricDefs,
    metricFormatByName,
    selectedDatasetIds,
    executionSettings,
    hasOverride,
    effectiveParams,
    paramsOverride,
    setStrategyParamOverride,
    resetStrategyParams,
    breakdownByMonth,
    setBreakdownByMonth,
    runMutation,
    runNow,
    datasetResults,
    focusedDatasetId,
    setFocusedDatasetId,
    result,
    riskManagementLines,
    tickerRanking,
    addToBatch,
  }

  return <StrategyDetailCtx.Provider value={value}>{children}</StrategyDetailCtx.Provider>
}

export function useStrategyDetail() {
  const ctx = useContext(StrategyDetailCtx)
  if (!ctx) throw new Error('useStrategyDetail must be used within a StrategyDetailProvider')
  return ctx
}
