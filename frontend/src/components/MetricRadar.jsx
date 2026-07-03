import './MetricRadar.css'

function clamp(v, lo, hi) {
  return Math.min(hi, Math.max(lo, v))
}

// Fixed, hand-picked domains per metric so six wildly different units
// (a percentage, three unbounded ratios, a 0-1 score) share one 0-100
// radar scale. Not statistically rigorous — just "what a trader would
// call good" — but that's the point: this chart is a shape to
// recognize at a glance, not a precise readout (the numbers next to it
// still are).
const RADAR_METRICS = [
  { name: 'win_rate', label: 'Win Rate', score: (v) => clamp(v, 0, 100) },
  { name: 'profit_factor', label: 'Profit Factor', score: (v) => (clamp(v, 0, 3) / 3) * 100 },
  { name: 'sharpe_ratio', label: 'Sharpe', score: (v) => ((clamp(v, -1, 3) + 1) / 4) * 100 },
  { name: 'recovery_factor', label: 'Recovery', score: (v) => (clamp(v, 0, 5) / 5) * 100 },
  { name: 'consistency', label: 'Consistency', score: (v) => clamp(v, 0, 1) * 100 },
  { name: 'max_drawdown', label: 'Low Drawdown', score: (v) => 100 - clamp(v, 0, 100) },
]

// "Strategy Fingerprint": a radar/spider chart plotting six normalized
// metrics as a polygon, so two strategies with the same overall score
// but very different risk/reward shapes (e.g. high win rate + weak
// payoff vs. low win rate + huge payoff) are visually distinguishable
// at a glance, not just as a rank number.
export default function MetricRadar({ metrics }) {
  const size = 100
  const center = size / 2
  const maxRadius = 36
  const axisCount = RADAR_METRICS.length
  const angleStep = (Math.PI * 2) / axisCount

  const axisPoint = (i, radius) => {
    const angle = angleStep * i - Math.PI / 2
    return [center + radius * Math.cos(angle), center + radius * Math.sin(angle)]
  }

  const values = RADAR_METRICS.map((axis) => {
    const raw = metrics?.[axis.name]
    if (raw === null || raw === undefined) return null
    return clamp(axis.score(raw), 0, 100)
  })

  const hasData = values.some((v) => v !== null)

  const polygonPoints = values
    .map((v, i) => axisPoint(i, ((v ?? 0) / 100) * maxRadius).join(','))
    .join(' ')

  return (
    <div className="metric-radar">
      <svg viewBox={`0 0 ${size} ${size}`} className="metric-radar-svg">
        {[0.25, 0.5, 0.75, 1].map((r) => (
          <polygon
            key={r}
            points={RADAR_METRICS.map((_, i) => axisPoint(i, maxRadius * r).join(',')).join(' ')}
            className="metric-radar-ring"
          />
        ))}

        {RADAR_METRICS.map((axis, i) => {
          const [x, y] = axisPoint(i, maxRadius)
          return (
            <line
              key={axis.name}
              x1={center}
              y1={center}
              x2={x}
              y2={y}
              className="metric-radar-axis"
            />
          )
        })}

        {hasData && <polygon points={polygonPoints} className="metric-radar-shape" />}

        {hasData &&
          values.map((v, i) => {
            if (v === null) return null
            const [x, y] = axisPoint(i, (v / 100) * maxRadius)
            return <circle key={RADAR_METRICS[i].name} cx={x} cy={y} r="1.8" className="metric-radar-point" />
          })}
      </svg>

      <div className="metric-radar-labels">
        {RADAR_METRICS.map((axis, i) => {
          const [x, y] = axisPoint(i, maxRadius + 12)
          return (
            <span
              key={axis.name}
              className="metric-radar-label"
              style={{ left: `${x}%`, top: `${y}%` }}
            >
              {axis.label}
            </span>
          )
        })}
      </div>

      {!hasData && <div className="metric-radar-empty">Not enough data for a fingerprint yet.</div>}
    </div>
  )
}
