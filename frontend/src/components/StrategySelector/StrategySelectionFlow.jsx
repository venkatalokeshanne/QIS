// The pipeline as a strip of stages with how many strategies survive each
// gate -- mirrors the selector's gate order.
export default function StrategySelectionFlow({ result }) {
  const rej = result.rejected_strategies || []
  const qualified = (result.qualified_strategies || []).length
  const total = rej.length + qualified
  const out = (...s) => rej.filter((r) => s.includes(r.status)).length
  const stages = [
    ['Registry', total],
    ['Runnable for ticker', total - out('NOT_RUNNABLE', 'NOT_APPLICABLE')],
    ['Timeframe', total - out('NOT_RUNNABLE', 'NOT_APPLICABLE', 'TIMEFRAME_MISMATCH', 'DATA_MISMATCH')],
    ['Data', total - out('NOT_RUNNABLE', 'NOT_APPLICABLE', 'TIMEFRAME_MISMATCH', 'DATA_MISMATCH', 'DATA_UNAVAILABLE')],
    ['Family', out('NOT_EVALUATED', 'NOT_QUALIFIED') + qualified],
    ['Backtested', out('NOT_QUALIFIED') + qualified],
    ['Qualified', qualified],
  ]
  return (
    <ol className="ss-flow" aria-label="Selection pipeline">
      {stages.map(([name, n], i) => (
        <li key={name} className={i === stages.length - 1 ? 'ss-flow-last' : ''}>
          <span className="ss-flow-n">{n}</span>
          <span className="ss-flow-name">{name}</span>
        </li>
      ))}
    </ol>
  )
}
