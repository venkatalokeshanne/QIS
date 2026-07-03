import { useMemo, useRef, useState } from 'react'
import { formatMetricValue } from '../utils/format'
import './EquityCurve.css'

// Cumulative P&L across the trade sequence, rendered as an interactive
// SVG line with a gradient fill and a hover crosshair — the shape of
// the curve (steady climb vs. one lucky trade vs. a slow bleed) says
// more about a strategy's character than any single number, and being
// able to scrub across trades to see the exact running total is what
// makes it worth looking at twice.
export default function EquityCurve({ trades }) {
  const wrapRef = useRef(null)
  const [hoverIndex, setHoverIndex] = useState(null)

  const points = useMemo(() => {
    if (!trades || trades.length === 0) return []
    let cumulative = 0
    return trades.map((t) => (cumulative += t.pnl ?? 0))
  }, [trades])

  if (points.length === 0) {
    return <div className="equity-curve-empty">No trades to chart.</div>
  }

  const width = 100
  const height = 100
  const min = Math.min(0, ...points)
  const max = Math.max(0, ...points)
  const range = max - min || 1

  const toX = (i) => (points.length === 1 ? width / 2 : (i / (points.length - 1)) * width)
  const toY = (v) => height - ((v - min) / range) * height
  const zeroY = toY(0)

  const linePath = points.map((v, i) => `${i === 0 ? 'M' : 'L'} ${toX(i)} ${toY(v)}`).join(' ')
  const areaPath = `${linePath} L ${toX(points.length - 1)} ${zeroY} L ${toX(0)} ${zeroY} Z`

  const final = points[points.length - 1]
  const isPositive = final >= 0

  const handleMove = (e) => {
    const rect = wrapRef.current.getBoundingClientRect()
    const fraction = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width))
    setHoverIndex(Math.round(fraction * (points.length - 1)))
  }

  const hoverValue = hoverIndex !== null ? points[hoverIndex] : null
  const hoverX = hoverIndex !== null ? toX(hoverIndex) : null

  return (
    <div
      className="equity-curve"
      ref={wrapRef}
      onMouseMove={handleMove}
      onMouseLeave={() => setHoverIndex(null)}
    >
      <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="equity-curve-svg">
        <defs>
          <linearGradient id="equity-fill-positive" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" className="equity-gradient-positive-start" />
            <stop offset="100%" className="equity-gradient-positive-end" />
          </linearGradient>
          <linearGradient id="equity-fill-negative" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" className="equity-gradient-negative-start" />
            <stop offset="100%" className="equity-gradient-negative-end" />
          </linearGradient>
        </defs>

        <line
          x1="0"
          y1={zeroY}
          x2={width}
          y2={zeroY}
          className="equity-curve-zero"
          vectorEffect="non-scaling-stroke"
        />

        <path
          d={areaPath}
          fill={isPositive ? 'url(#equity-fill-positive)' : 'url(#equity-fill-negative)'}
          className="equity-curve-area"
        />

        <path
          d={linePath}
          vectorEffect="non-scaling-stroke"
          className={`equity-curve-line ${isPositive ? 'positive' : 'negative'}`}
        />

        {hoverIndex !== null && (
          <>
            <line
              x1={hoverX}
              y1="0"
              x2={hoverX}
              y2={height}
              className="equity-curve-crosshair"
              vectorEffect="non-scaling-stroke"
            />
            <circle
              cx={hoverX}
              cy={toY(hoverValue)}
              r="2.2"
              vectorEffect="non-scaling-stroke"
              className={`equity-curve-dot ${hoverValue >= 0 ? 'positive' : 'negative'}`}
            />
          </>
        )}
      </svg>

      {hoverIndex !== null && (
        <div className="equity-curve-tooltip" style={{ left: `${(hoverX / width) * 100}%` }}>
          <div className="equity-curve-tooltip-label">Trade {hoverIndex + 1}</div>
          <div className={`equity-curve-tooltip-value ${hoverValue >= 0 ? 'positive' : 'negative'}`}>
            {formatMetricValue(hoverValue, 'currency')}
          </div>
        </div>
      )}

      <div className="equity-curve-footline">
        <span>Trade 1</span>
        <span>Trade {points.length}</span>
      </div>
    </div>
  )
}
