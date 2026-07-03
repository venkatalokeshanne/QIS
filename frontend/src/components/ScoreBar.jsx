import './ScoreBar.css'

// The one deliberate visual flourish in the app: a thin, single-color
// bar whose width encodes the overall ranking score. It sits directly
// in the ranking table row rather than as a separate chart, so
// scanning "which strategy wins" is a glance down one column, not a
// context switch to a graph. No gradient, no shadow — width is the
// only variable, matching the "precise instrument, not a dashboard"
// brief.
export default function ScoreBar({ score }) {
  if (score === null || score === undefined) {
    return <span className="score-bar-empty mono">—</span>
  }
  const pct = Math.max(0, Math.min(100, score))
  return (
    <div className="score-bar-wrap">
      <span className="score-bar-value mono">{score.toFixed(1)}</span>
      <div className="score-bar-track">
        <div className="score-bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
