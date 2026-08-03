import { useEffect, useRef, useState } from 'react'
import { useResearchStore } from '../store/useResearchStore'
import Button from './Button'
import './TickerSelect.css'

const INTERVAL_PRESETS = [
  { label: '1m', value: '1min' },
  { label: '5m', value: '5min' },
  { label: '15m', value: '15min' },
  { label: '1h', value: '1h' },
  { label: '1D', value: '1day' },
]

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

  const addSymbol = () => {
    const trimmed = symbol.trim().toUpperCase()
    if (trimmed) addSelectedSymbol(trimmed)
    setSymbol('')
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
          <input
            type="text"
            className="field-input mono ticker-select-search"
            placeholder="Type a symbol and press Enter…"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && addSymbol()}
            autoFocus
          />

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
