import { useEffect, useRef, useState } from 'react'
import { useFetchFromTwelvedata } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import Button from './Button'
import './TwelvedataFetchMenu.css'

const INTERVAL_PRESETS = [
  { label: '1m', value: '1min' },
  { label: '5m', value: '5min' },
  { label: '15m', value: '15min' },
  { label: '1h', value: '1h' },
  { label: '1D', value: '1day' },
]

const DURATION_PRESETS = [
  { label: '1D', value: '1D' },
  { label: '5D', value: '5D' },
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
  { label: '6M', value: '6M' },
  { label: '1Y', value: '1Y' },
]

export default function TwelvedataFetchMenu() {
  const containerRef = useRef(null)
  const [open, setOpen] = useState(false)
  const [symbol, setSymbol] = useState('')
  const [interval, setInterval_] = useState('1min')
  const [duration, setDuration] = useState('1M')
  const [rangeMode, setRangeMode] = useState('duration') // 'duration' | 'custom'
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [toast, setToast] = useState(null)

  const addSelectedDatasetId = useResearchStore((s) => s.addSelectedDatasetId)
  const fetchMutation = useFetchFromTwelvedata()

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

  useEffect(() => {
    if (!toast) return
    const timer = setTimeout(() => setToast(null), 4000)
    return () => clearTimeout(timer)
  }, [toast])

  const onFetch = () => {
    const trimmed = symbol.trim().toUpperCase()
    if (!trimmed) return
    if (rangeMode === 'custom' && !startDate) return

    const payload =
      rangeMode === 'custom'
        ? { symbol: trimmed, interval, duration: null, start_date: startDate, end_date: endDate || null, name: null }
        : { symbol: trimmed, interval, duration, name: null }

    fetchMutation.mutate(payload, {
      onSuccess: (data) => {
        addSelectedDatasetId(data.dataset.id)
        setToast(`Added “${data.dataset.name}” — ${data.dataset.row_count.toLocaleString()} rows`)
        setSymbol('')
        setOpen(false)
      },
    })
  }

  return (
    <div className="td-menu" ref={containerRef}>
      <Button
        variant="secondary"
        size="sm"
        className="td-menu-trigger"
        onClick={() => setOpen((o) => !o)}
      >
        <span className="td-menu-dot" />
        <span className="td-menu-label">Fetch from Twelve Data</span>
      </Button>

      {open && (
        <div className="td-menu-panel">
          <div className="td-menu-title">Fetch historical bars</div>

          <div className="field-group td-menu-symbol">
            <label className="field-label" htmlFor="td-menu-symbol">
              Symbol
            </label>
            <input
              id="td-menu-symbol"
              className="field-input mono"
              placeholder="AAPL"
              value={symbol}
              autoFocus
              onChange={(e) => setSymbol(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && onFetch()}
            />
          </div>

          <div className="chip-section-label">Interval</div>
          <div className="chip-row">
            {INTERVAL_PRESETS.map((p) => (
              <button
                key={p.value}
                type="button"
                className={`chip${interval === p.value ? ' active' : ''}`}
                onClick={() => setInterval_(p.value)}
              >
                {p.label}
              </button>
            ))}
          </div>

          <div className="chip-section-label">Range</div>
          <div className="chip-row">
            <button
              type="button"
              className={`chip${rangeMode === 'duration' ? ' active' : ''}`}
              onClick={() => setRangeMode('duration')}
            >
              Quick range
            </button>
            <button
              type="button"
              className={`chip${rangeMode === 'custom' ? ' active' : ''}`}
              onClick={() => setRangeMode('custom')}
            >
              Custom dates
            </button>
          </div>

          {rangeMode === 'duration' ? (
            <div className="chip-row">
              {DURATION_PRESETS.map((p) => (
                <button
                  key={p.value}
                  type="button"
                  className={`chip${duration === p.value ? ' active' : ''}`}
                  onClick={() => setDuration(p.value)}
                >
                  {p.label}
                </button>
              ))}
            </div>
          ) : (
            <div className="td-menu-date-row">
              <div className="field-group">
                <label className="field-label" htmlFor="td-menu-start">
                  Start date
                </label>
                <input
                  id="td-menu-start"
                  type="date"
                  className="field-input mono"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="field-group">
                <label className="field-label" htmlFor="td-menu-end">
                  End date <span className="field-hint">(optional, defaults to now)</span>
                </label>
                <input
                  id="td-menu-end"
                  type="date"
                  className="field-input mono"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
            </div>
          )}

          {fetchMutation.isError && (
            <div className="td-menu-error">
              {fetchMutation.error.message}
              {fetchMutation.error.issues?.length > 0 && (
                <ul>
                  {fetchMutation.error.issues.map((issue, i) => (
                    <li key={i}>{issue}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          <div className="td-menu-actions">
            <Button
              variant="primary"
              size="sm"
              onClick={onFetch}
              disabled={
                fetchMutation.isPending || !symbol.trim() || (rangeMode === 'custom' && !startDate)
              }
            >
              {fetchMutation.isPending ? 'Fetching…' : 'Fetch & Add Dataset'}
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setOpen(false)}>
              Cancel
            </Button>
          </div>
        </div>
      )}

      {toast && <div className="td-menu-toast">{toast}</div>}
    </div>
  )
}
