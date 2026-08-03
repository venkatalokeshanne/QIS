import { useEffect, useRef, useState } from 'react'
import { useResearchStore } from '../store/useResearchStore'
import { WATCHLISTS } from '../data/watchlists'
import Button from './Button'
import './TickerSelect.css'

const INTERVAL_PRESETS = [
  { label: '1m', value: '1min' },
  { label: '5m', value: '5min' },
  { label: '15m', value: '15min' },
  { label: '1h', value: '1h' },
  { label: '1D', value: '1day' },
]

// Every ticker across every watchlist, deduped, with which watchlist(s)
// it belongs to -- powers the search box's typeahead so picking one
// ticker out of a watchlist doesn't require expanding the whole group.
const WATCHLIST_TICKER_INDEX = (() => {
  const byTicker = new Map()
  for (const wl of WATCHLISTS) {
    for (const t of wl.tickers) {
      if (!byTicker.has(t)) byTicker.set(t, [])
      byTicker.get(t).push(wl.name)
    }
  }
  return byTicker
})()

const MAX_SUGGESTIONS = 8

// Single header control: a chip list of tickers plus the one global
// timeframe. Adding/removing a symbol is purely client-side (no
// backend fetch) -- backtesting and Live Signal fetch bars live, on
// demand, once a run/check is actually triggered. Mounted once in
// Header (desktop) and once in StrategySidebar's mobile drawer; both
// read/write the same store, so selection stays in sync.
export default function TickerSelect() {
  const containerRef = useRef(null)
  const [open, setOpen] = useState(false)
  const [symbol, setSymbol] = useState('')

  const selectedSymbols = useResearchStore((s) => s.selectedSymbols)
  const toggleSymbol = useResearchStore((s) => s.toggleSymbol)
  const setSelectedSymbols = useResearchStore((s) => s.setSelectedSymbols)
  const addSelectedSymbol = useResearchStore((s) => s.addSelectedSymbol)
  const addSelectedSymbols = useResearchStore((s) => s.addSelectedSymbols)
  const selectedInterval = useResearchStore((s) => s.selectedInterval)
  const setSelectedInterval = useResearchStore((s) => s.setSelectedInterval)
  const backtestStartDate = useResearchStore((s) => s.backtestStartDate)
  const backtestEndDate = useResearchStore((s) => s.backtestEndDate)
  const setBacktestStartDate = useResearchStore((s) => s.setBacktestStartDate)
  const setBacktestEndDate = useResearchStore((s) => s.setBacktestEndDate)

  useEffect(() => {
    if (!open) return
    const onClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [open])

  const triggerLabel =
    selectedSymbols.length === 0
      ? 'Select tickers…'
      : selectedSymbols.length === 1
        ? selectedSymbols[0]
        : `${selectedSymbols.length} tickers`

  const addSymbol = (value) => {
    const trimmed = (value ?? symbol).trim().toUpperCase()
    if (trimmed) addSelectedSymbol(trimmed)
    setSymbol('')
  }

  // Typeahead: as soon as the user types, suggest matching tickers from
  // every watchlist (prefix match, already-selected ones filtered out)
  // so picking one out of a watchlist doesn't require expanding a whole
  // group -- just type a couple letters and click it.
  const query = symbol.trim().toUpperCase()
  const suggestions = query
    ? Array.from(WATCHLIST_TICKER_INDEX.keys())
        .filter((t) => t.startsWith(query) && !selectedSymbols.includes(t))
        .sort()
        .slice(0, MAX_SUGGESTIONS)
    : []

  // A category chip is "active" once every one of its tickers is
  // already selected -- clicking it then removes them (toggle off);
  // otherwise clicking adds every ticker in that category at once.
  const isWatchlistActive = (tickers) => tickers.every((t) => selectedSymbols.includes(t))
  const toggleWatchlist = (tickers) => {
    if (isWatchlistActive(tickers)) {
      setSelectedSymbols(selectedSymbols.filter((s) => !tickers.includes(s)))
    } else {
      addSelectedSymbols(tickers)
    }
  }

  return (
    <div className="ticker-select" ref={containerRef}>
      <button
        type="button"
        className="ticker-select-trigger"
        onClick={() => setOpen((o) => !o)}
        title={selectedSymbols.join(', ') || 'Select tickers…'}
      >
        <span className="ticker-select-trigger-label">{triggerLabel}</span>
        <span className="ticker-select-chevron" />
      </button>

      {open && (
        <div className="ticker-select-panel">
          <div className="ticker-select-search-wrap">
            <input
              type="text"
              className="field-input mono ticker-select-search"
              placeholder="Type a symbol and press Enter…"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addSymbol()}
              autoFocus
            />
            {suggestions.length > 0 && (
              <div className="ticker-select-suggestions">
                {suggestions.map((t) => (
                  <button
                    key={t}
                    type="button"
                    className="ticker-select-suggestion"
                    onClick={() => addSymbol(t)}
                  >
                    <span className="mono">{t}</span>
                    <span className="ticker-select-suggestion-watchlists">
                      {WATCHLIST_TICKER_INDEX.get(t).join(', ')}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="chip-section-label">Watchlists</div>
          <div className="chip-row ticker-select-watchlist-row">
            {WATCHLISTS.map((wl) => (
              <button
                key={wl.name}
                type="button"
                className={`chip${isWatchlistActive(wl.tickers) ? ' active' : ''}`}
                title={`Select all ${wl.tickers.length} tickers in ${wl.name}`}
                onClick={() => toggleWatchlist(wl.tickers)}
              >
                {wl.name} ({wl.tickers.length})
              </button>
            ))}
          </div>

          <div className="chip-section-label">Timeframe</div>
          <div className="chip-row ticker-select-interval-row">
            {INTERVAL_PRESETS.map((p) => (
              <button
                key={p.value}
                type="button"
                className={`chip${selectedInterval === p.value ? ' active' : ''}`}
                onClick={() => setSelectedInterval(p.value)}
              >
                {p.label}
              </button>
            ))}
          </div>

          <div className="chip-section-label">Date Range</div>
          <div className="ticker-select-date-row">
            <input
              type="date"
              className="field-input"
              value={backtestStartDate || ''}
              onChange={(e) => setBacktestStartDate(e.target.value || null)}
            />
            <input
              type="date"
              className="field-input"
              value={backtestEndDate || ''}
              onChange={(e) => setBacktestEndDate(e.target.value || null)}
            />
          </div>
          {(backtestStartDate || backtestEndDate) && (
            <button
              type="button"
              className="ticker-select-clear"
              onClick={() => {
                setBacktestStartDate(null)
                setBacktestEndDate(null)
              }}
            >
              Clear date range
            </button>
          )}

          {selectedSymbols.length > 0 && (
            <button type="button" className="ticker-select-clear" onClick={() => setSelectedSymbols([])}>
              Clear all ({selectedSymbols.length})
            </button>
          )}

          <div className="chip-section-label">Tickers</div>
          <div className="chip-row ticker-select-symbol-row">
            {selectedSymbols.length === 0 ? (
              <div className="ticker-select-empty">No tickers yet — type a symbol above and press Enter.</div>
            ) : (
              selectedSymbols.map((s) => (
                <span key={s} className="ticker-select-symbol-chip">
                  {s}
                  <button
                    type="button"
                    className="ticker-select-symbol-remove"
                    onClick={() => toggleSymbol(s)}
                    aria-label={`Remove ${s}`}
                  >
                    ×
                  </button>
                </span>
              ))
            )}
          </div>

          <Button variant="primary" size="sm" onClick={() => setOpen(false)}>
            Save
          </Button>
        </div>
      )}
    </div>
  )
}
