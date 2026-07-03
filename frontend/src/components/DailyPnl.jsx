import { useMemo, useRef, useState } from 'react'
import { formatMetricValue } from '../utils/format'
import './DailyPnl.css'

function dateKey(iso) {
  if (!iso) return null
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return null
  return d.toISOString().slice(0, 10)
}

function formatDayLabel(key) {
  const d = new Date(`${key}T00:00:00`)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

// Aggregates trade P&L by the calendar date each trade closed on. This
// makes no assumption about how many days (or which ones) the run
// covers -- a single-day intraday dataset shows one bar, a multi-week
// run shows one bar per day it actually traded, entirely derived from
// the trades themselves rather than a fixed date range.
export default function DailyPnl({ trades, main = false }) {
  const wrapRef = useRef(null)
  const [hoverIndex, setHoverIndex] = useState(null)

  const days = useMemo(() => {
    if (!trades || trades.length === 0) return []
    const totals = new Map()
    for (const t of trades) {
      const key = dateKey(t.exit_time ?? t.entry_time)
      if (!key) continue
      totals.set(key, (totals.get(key) ?? 0) + (t.pnl ?? 0))
    }
    return Array.from(totals.entries())
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
      .map(([date, pnl]) => ({ date, pnl }))
  }, [trades])

  if (days.length === 0) {
    return <div className="daily-pnl-empty">No trades to chart.</div>
  }

  const width = 100
  const height = 100
  const midY = height / 2
  const maxAbs = Math.max(1, ...days.map((d) => Math.abs(d.pnl)))
  const slot = width / days.length
  const gap = Math.min(slot * 0.3, 1.2)
  const barWidth = Math.max(slot - gap, 0.3)

  const handleMove = (e) => {
    const rect = wrapRef.current.getBoundingClientRect()
    const fraction = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width))
    setHoverIndex(Math.min(days.length - 1, Math.floor(fraction * days.length)))
  }

  const hovered = hoverIndex !== null ? days[hoverIndex] : null

  return (
    <div
      className={`daily-pnl${main ? ' daily-pnl-main' : ''}`}
      ref={wrapRef}
      onMouseMove={handleMove}
      onMouseLeave={() => setHoverIndex(null)}
    >
      <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="daily-pnl-svg">
        <line
          x1="0"
          y1={midY}
          x2={width}
          y2={midY}
          className="daily-pnl-zero"
          vectorEffect="non-scaling-stroke"
        />
        {days.map((d, i) => {
          const barHeight = Math.max((Math.abs(d.pnl) / maxAbs) * midY, 0.6)
          const x = i * slot + gap / 2
          const isPositive = d.pnl >= 0
          const y = isPositive ? midY - barHeight : midY
          return (
            <rect
              key={d.date}
              x={x}
              y={y}
              width={barWidth}
              height={barHeight}
              className={`daily-pnl-bar ${isPositive ? 'positive' : 'negative'}${
                hoverIndex === i ? ' active' : ''
              }`}
            />
          )
        })}
      </svg>

      {hovered && (
        <div className="daily-pnl-tooltip" style={{ left: `${((hoverIndex + 0.5) / days.length) * 100}%` }}>
          <div className="daily-pnl-tooltip-label">{formatDayLabel(hovered.date)}</div>
          <div className={`daily-pnl-tooltip-value ${hovered.pnl >= 0 ? 'positive' : 'negative'}`}>
            {formatMetricValue(hovered.pnl, 'currency')}
          </div>
        </div>
      )}

      <div className="daily-pnl-footline">
        <span>{formatDayLabel(days[0].date)}</span>
        {days.length > 1 && <span>{formatDayLabel(days[days.length - 1].date)}</span>}
      </div>
    </div>
  )
}
