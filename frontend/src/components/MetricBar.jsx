import './ScoreBar.css'

// Same visual language as ScoreBar (single accent color, width-only
// variable), reused for any percent-format metric (win rate, max
// drawdown) so "metrics shown visually" doesn't invent a second bar style.
export default function MetricBar({ value }) {
  if (value === null || value === undefined) {
    return <span className="score-bar-empty mono">—</span>
  }
  const pct = Math.max(0, Math.min(100, value))
  return (
    <div className="score-bar-wrap">
      <span className="score-bar-value mono">{value.toFixed(1)}%</span>
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
