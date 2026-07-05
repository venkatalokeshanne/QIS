import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import AsyncStorage from '@react-native-async-storage/async-storage'

// Ported from frontend/src/store/useResearchStore.js -- identical
// shape/logic, only the persist middleware's storage engine changes
// (localStorage -> AsyncStorage, since RN has no localStorage).
//
// Holds state that needs to survive navigation across the research
// workflow: Upload -> Datasets -> Run Backtests -> Results -> Compare.
// Keeping this out of individual screens is what lets "Run All" on the
// Backtest screen land you on Results with data already there, and
// lets Compare read the same last-run results Results is showing, with
// no prop drilling or re-fetching.
//
// The "configuration" fields (selectedDatasetIds, selectedStrategyNames,
// executionSettings) are also persisted via `persist` below, so picking
// tickers or tuning risk settings survives an app restart -- only those
// fields are persisted (`partialize`), not lastRunResults/compareSelection,
// since those are working state for the current sitting, not a saved
// preference, and trade lists can get large enough that stashing them
// in AsyncStorage on every run isn't worth it.
export const useResearchStore = create(
  persist(
    (set) => ({
      // Multiple tickers/datasets can be selected at once -- every
      // screen that used to read a single selectedDatasetId now runs
      // against each id in this array.
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

      selectedStrategyNames: [], // empty array = "run all" semantics on the Backtest screen
      setSelectedStrategyNames: (names) => set({ selectedStrategyNames: names }),
      toggleStrategyName: (name) =>
        set((state) => ({
          selectedStrategyNames: state.selectedStrategyNames.includes(name)
            ? state.selectedStrategyNames.filter((n) => n !== name)
            : [...state.selectedStrategyNames, name],
        })),

      // Per-strategy parameter overrides (see the Configure tab on
      // Strategy Detail) -- keyed by strategy name, only the keys the
      // user has actually changed. Merged over each strategy's own
      // default_params both when auto-running and in the batch Run
      // Backtests screen, so "default should be your current values"
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

      // Compare is scoped to one ticker at a time -- comparing
      // strategies only makes sense within the same dataset, so the
      // selection carries which dataset_id it belongs to and resets
      // itself if the Results screen's compare tap comes from a
      // different ticker's table.
      compareDatasetId: null,
      compareSelection: [], // strategy_name[] chosen on the Results screen for the Compare screen
      setCompareSelection: (datasetId, names) => set({ compareDatasetId: datasetId, compareSelection: names }),

      // Expo push token for this device, registered once on app start
      // (see src/utils/notifications.js) and persisted so it doesn't
      // need to be re-requested every launch -- the Alerts tab sends it
      // with every watch it creates so the backend poller knows where
      // to deliver that watch's signal notifications.
      pushToken: null,
      setPushToken: (token) => set({ pushToken: token }),
    }),
    {
      name: 'quant-platform-research-store',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        selectedDatasetIds: state.selectedDatasetIds,
        selectedStrategyNames: state.selectedStrategyNames,
        executionSettings: state.executionSettings,
        strategyParamOverrides: state.strategyParamOverrides,
        breakdownByMonth: state.breakdownByMonth,
        pushToken: state.pushToken,
      }),
    }
  )
)
