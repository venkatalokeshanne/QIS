import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Holds state that needs to survive navigation across the research
// workflow: Upload -> Strategy Library -> Run Backtests -> Results ->
// Compare. Keeping this out of individual page components is what
// lets "Run All" on the Backtest page land you on Results with data
// already there, and lets Compare read the same last-run results
// Results is showing, with no prop drilling or re-fetching.
//
// The "configuration" fields (selectedDatasetIds, selectedStrategyNames,
// executionSettings) are also persisted to localStorage via the
// `persist` middleware below, so picking tickers or tuning risk settings
// survives a page refresh -- only those fields are persisted
// (`partialize`), not lastRunResults/compareSelection, since those are
// working state for the current sitting, not a saved preference, and
// trade lists can get large enough that stashing them in localStorage
// on every run isn't worth it.
export const useResearchStore = create(
  persist(
    (set) => ({
      // Multiple tickers/datasets can be selected at once (see
      // TickerMultiSelect) -- every page that used to read a single
      // selectedDatasetId now runs against each id in this array.
      selectedDatasetIds: [],
      setSelectedDatasetIds: (ids) => set({ selectedDatasetIds: ids }),
      toggleDatasetId: (id) =>
        set((state) => ({
          selectedDatasetIds: state.selectedDatasetIds.includes(id)
            ? state.selectedDatasetIds.filter((x) => x !== id)
            : [...state.selectedDatasetIds, id],
        })),
      addSelectedDatasetId: (id) =>
        set((state) => ({
          selectedDatasetIds: state.selectedDatasetIds.includes(id)
            ? state.selectedDatasetIds
            : [...state.selectedDatasetIds, id],
        })),

      selectedStrategyNames: [], // empty array = "run all" semantics on the Backtest page
      setSelectedStrategyNames: (names) => set({ selectedStrategyNames: names }),
      toggleStrategyName: (name) =>
        set((state) => ({
          selectedStrategyNames: state.selectedStrategyNames.includes(name)
            ? state.selectedStrategyNames.filter((n) => n !== name)
            : [...state.selectedStrategyNames, name],
        })),

      // Per-strategy parameter overrides (see the Configure tab on
      // StrategyDetail) -- keyed by strategy name, only the keys the
      // user has actually changed. Merged over each strategy's own
      // default_params both when auto-running and in the batch Run
      // Backtests page, so "be default should be your current values"
      // means the backend's own defaults, not a frontend-side copy of
      // them that could drift.
      strategyParamOverrides: {},
      setStrategyParamOverride: (name, key, value) =>
        set((state) => ({
          strategyParamOverrides: {
            ...state.strategyParamOverrides,
            [name]: { ...(state.strategyParamOverrides[name] || {}), [key]: value },
          },
        })),
      resetStrategyParams: (name) =>
        set((state) => {
          const next = { ...state.strategyParamOverrides }
          delete next[name]
          return { strategyParamOverrides: next }
        }),

      // Slices the SAME backtest's results by calendar month in
      // addition to the overall aggregate -- see MonthlyBreakdownTable.
      breakdownByMonth: false,
      setBreakdownByMonth: (value) => set({ breakdownByMonth: value }),

      executionSettings: {
        capital: 10000,
        quantity: 1,
        commission_per_trade: 0,
        slippage_pct: 0,
        force_close_at_session_end: true,
        direction_filter: 'long_only', // 'long_only' | 'short_only' | 'both'
        atr_period: 14,
        stop_loss_atr_multiple: 2,
        stop_loss_pct: null, // flat % stop (e.g. 0.01 = 1%); off by default, alternative to ATR-based stop
        take_profit_atr_multiple: 4, // 2:1 reward:risk relative to the stop
        trailing_stop_atr_multiple: null, // mutually exclusive with stop_loss_atr_multiple; off by default
        risk_per_trade_pct: 0.01, // 1% of capital per trade
      },
      setExecutionSettings: (settings) =>
        set((state) => ({ executionSettings: { ...state.executionSettings, ...settings } })),

      lastRunResults: null, // { dataset_results: [{ dataset_id, dataset_name, results: [...] }] }
      setLastRunResults: (results) => set({ lastRunResults: results }),

      // Compare (see Compare.jsx) is scoped to one ticker at a time --
      // comparing strategies only makes sense within the same dataset,
      // so the selection carries which dataset_id it belongs to and
      // resets itself if the Results page's compare click comes from a
      // different ticker's table.
      compareDatasetId: null,
      compareSelection: [], // strategy_name[] chosen on the Results page for the Compare page
      setCompareSelection: (datasetId, names) => set({ compareDatasetId: datasetId, compareSelection: names }),
    }),
    {
      name: 'quant-platform-research-store',
      partialize: (state) => ({
        selectedDatasetIds: state.selectedDatasetIds,
        selectedStrategyNames: state.selectedStrategyNames,
        executionSettings: state.executionSettings,
        strategyParamOverrides: state.strategyParamOverrides,
        breakdownByMonth: state.breakdownByMonth,
      }),
    }
  )
)
