// Mobile-only display adjustments (no web equivalent, no backend
// change) -- applied wherever a full metric-definitions list from
// /api/catalog/metrics is rendered as a grid/table.
//
// sortino_ratio and sharpe_ratio excluded per user feedback --
// sortino_ratio's per-trade, unannualized calculation can blow up to
// an absurd magnitude when downside deviation is near zero over a
// short sample (seen in testing: a value in the hundreds-of-billions
// range), and sharpe_ratio was dropped alongside it for the same
// "risk-adjusted ratio nobody reads on a phone" reason. Streak metric
// names shortened to fit narrow columns without truncating.
const EXCLUDED_METRICS = new Set(['sortino_ratio', 'sharpe_ratio'])

const LABEL_OVERRIDES = {
  consecutive_winners: 'Win Streak',
  consecutive_losers: 'Loss Streak',
}

export function displayMetricDefs(metricDefs) {
  return (metricDefs || [])
    .filter((def) => !EXCLUDED_METRICS.has(def.name))
    .map((def) => (LABEL_OVERRIDES[def.name] ? { ...def, display_name: LABEL_OVERRIDES[def.name] } : def))
}
