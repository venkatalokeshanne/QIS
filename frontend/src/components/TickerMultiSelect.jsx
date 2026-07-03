import { useEffect, useMemo, useRef, useState } from 'react'
import { useDatasets } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import './TickerMultiSelect.css'

// Trigger + panel dropdown, same interaction pattern as TwelvedataFetchMenu /
// LiveIndicator, but for choosing one or more datasets ("tickers") at once --
// every strategy/backtest run now goes against every selected id. Mounted
// once in Header (desktop) and once in StrategySidebar's mobile drawer;
// both read/write the same store, so selection stays in sync between them.
export default function TickerMultiSelect() {
  const containerRef = useRef(null)
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')

  const { data: datasets } = useDatasets()
  const selectedDatasetIds = useResearchStore((s) => s.selectedDatasetIds)
  const toggleDatasetId = useResearchStore((s) => s.toggleDatasetId)
  const setSelectedDatasetIds = useResearchStore((s) => s.setSelectedDatasetIds)

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

  const filtered = useMemo(() => {
    if (!datasets) return []
    const q = search.trim().toLowerCase()
    if (!q) return datasets
    return datasets.filter((d) => d.name.toLowerCase().includes(q))
  }, [datasets, search])

  const selectedDatasets = useMemo(
    () => (datasets || []).filter((d) => selectedDatasetIds.includes(d.id)),
    [datasets, selectedDatasetIds]
  )

  const triggerLabel =
    selectedDatasets.length === 0
      ? 'Select tickers…'
      : selectedDatasets.length === 1
        ? selectedDatasets[0].name
        : `${selectedDatasets.length} tickers`

  return (
    <div className="ticker-select" ref={containerRef}>
      <button
        type="button"
        className="ticker-select-trigger"
        onClick={() => setOpen((o) => !o)}
        title={selectedDatasets.map((d) => d.name).join(', ') || 'Select tickers…'}
      >
        <span className="ticker-select-trigger-label">{triggerLabel}</span>
        <span className="ticker-select-chevron" />
      </button>

      {open && (
        <div className="ticker-select-panel">
          <input
            type="text"
            className="field-input ticker-select-search"
            placeholder="Search tickers…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
          />

          {selectedDatasetIds.length > 0 && (
            <button type="button" className="ticker-select-clear" onClick={() => setSelectedDatasetIds([])}>
              Clear all ({selectedDatasetIds.length})
            </button>
          )}

          <div className="ticker-select-list">
            {(datasets || []).length === 0 ? (
              <div className="ticker-select-empty">No datasets yet.</div>
            ) : filtered.length === 0 ? (
              <div className="ticker-select-empty">No matches.</div>
            ) : (
              filtered.map((d) => (
                <label key={d.id} className="ticker-select-item">
                  <input
                    type="checkbox"
                    checked={selectedDatasetIds.includes(d.id)}
                    onChange={() => toggleDatasetId(d.id)}
                  />
                  <span className="ticker-select-item-name">{d.name}</span>
                  <span className="ticker-select-item-rows">{d.row_count.toLocaleString()} rows</span>
                </label>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
