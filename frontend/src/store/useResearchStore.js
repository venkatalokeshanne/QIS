import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// YYYY-MM-DD, in local time -- matches the <input type="date"> value
// format the header's date pickers already use.
function toDateInputValue(date) {
  return date.toISOString().slice(0, 10)
}

function oneMonthAgo() {
  const d = new Date()
  d.setMonth(d.getMonth() - 1)
  return toDateInputValue(d)
}

function today() {
  return toDateInputValue(new Date())
}

// Holds state that needs to survive navigation across the research
// workflow: Upload -> Strategy Library -> Run Backtests -> Results ->
// Compare. Keeping this out of individual page components is what
// lets "Run All" on the Backtest page land you on Results with data
// already there, and lets Compare read the same last-run results
// Results is showing, with no prop drilling or re-fetching.
//
// The "configuration" fields (selectedSymbols, selectedStrategyNames,
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
      // Multiple tickers can be selected at once (see TickerSelect) --
      // every page that used to read a single selectedDatasetId now
      // runs against each symbol in this array. No fetch happens on
      // selection -- backtesting/Live Signal fetch bars live, on demand.
      selectedSymbols: [],
      setSelectedSymbols: (symbols) => set({ selectedSymbols: symbols }),
      toggleSymbol: (symbol) =>
        set((state) => ({
          selectedSymbols: state.selectedSymbols.includes(symbol)
            ? state.selectedSymbols.filter((x) => x !== symbol)
            : [...state.selectedSymbols, symbol],
        })),
      addSelectedSymbol: (symbol) =>
        set((state) => ({
          selectedSymbols: state.selectedSymbols.includes(symbol)
            ? state.selectedSymbols
            : [...state.selectedSymbols, symbol],
        })),
      // Bulk version of addSelectedSymbol -- used by the header's
      // Watchlists chips (see data/watchlists.js) to add every ticker
      // in a category at once, deduped against what's already selected.
      addSelectedSymbols: (symbols) =>
        set((state) => ({
          selectedSymbols: [...state.selectedSymbols, ...symbols.filter((s) => !state.selectedSymbols.includes(s))],
        })),

      // One global timeframe for the whole session (see TickerSelect) --
      // used both for backtesting (what interval to fetch bars at) and
      // by Live Signal (what interval to live-check every selected
      // ticker at), rather than each ticker carrying its own.
      selectedInterval: '5min',
      setSelectedInterval: (interval) => set({ selectedInterval: interval }),

      // Backtest fetch window, set in the header's Date Range section --
      // defaults to the last month; the backend's own default-lookback
      // heuristic only kicks in if these are explicitly cleared to null.
      backtestStartDate: oneMonthAgo(),
      backtestEndDate: today(),
      setBacktestStartDate: (date) => set({ backtestStartDate: date }),
      setBacktestEndDate: (date) => set({ backtestEndDate: date }),

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
        include_extended_hours: false, // pre-/after-market bars, same trading day
        include_overnight: false, // bars outside regular + extended hours (20:00-04:00 ET)
        atr_period: 14,
        stop_loss_atr_multiple: 2,
        stop_loss_pct: null, // flat % stop (e.g. 0.01 = 1%); off by default, alternative to ATR-based stop
        take_profit_atr_multiple: 4, // 2:1 reward:risk relative to the stop
        trailing_stop_atr_multiple: null, // mutually exclusive with stop_loss_atr_multiple; off by default
        risk_per_trade_pct: 0.01, // 1% of capital per trade
        max_position_value_pct: null, // cap position value at capital * this (1 = no leverage); off by default
      },
      setExecutionSettings: (settings) =>
        set((state) => ({ executionSettings: { ...state.executionSettings, ...settings } })),

      lastRunResults: null, // { ticker_results: [{ symbol, results: [...] }] }
      setLastRunResults: (results) => set({ lastRunResults: results }),

      // Compare (see Compare.jsx) is scoped to one ticker at a time --
      // comparing strategies only makes sense within the same symbol,
      // so the selection carries which symbol it belongs to and resets
      // itself if the Results page's compare click comes from a
      // different ticker's table.
      compareSymbol: null,
      compareSelection: [], // strategy_name[] chosen on the Results page for the Compare page
      setCompareSelection: (symbol, names) => set({ compareSymbol: symbol, compareSelection: names }),

      // Scanner (see Scanner.jsx) -- runs every selected strategy against
      // every selected symbol and keeps only the recent long/short
      // signal matches. Results are working state for the current
      // sitting (not persisted); lookback is a saved preference.
      scannerLookbackBars: 3,
      setScannerLookbackBars: (bars) => set({ scannerLookbackBars: bars }),
      lastScanResults: null, // { signals: [...], failed_symbols: [...] }
      setLastScanResults: (results) => set({ lastScanResults: results }),

      // Day Prep (see Scanner.jsx) -- ranks tickers worth concentrating
      // on today (activity + historical edge + today's gap), not just
      // ones with a signal in the last few bars. Working state only.
      lastDayPrepResults: null, // { tickers: [...], failed_symbols: [...] }
      setLastDayPrepResults: (results) => set({ lastDayPrepResults: results }),
    }),
    {
      name: 'quant-platform-research-store',
      partialize: (state) => ({
        selectedSymbols: state.selectedSymbols,
        selectedInterval: state.selectedInterval,
        backtestStartDate: state.backtestStartDate,
        backtestEndDate: state.backtestEndDate,
        selectedStrategyNames: state.selectedStrategyNames,
        executionSettings: state.executionSettings,
        strategyParamOverrides: state.strategyParamOverrides,
        breakdownByMonth: state.breakdownByMonth,
        scannerLookbackBars: state.scannerLookbackBars,
      }),
    }
  )
)
