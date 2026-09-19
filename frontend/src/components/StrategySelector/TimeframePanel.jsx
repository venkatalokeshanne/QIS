import { Panel } from './shared'

// How many strategies the timeframe gate kept vs. dropped.
export default function TimeframePanel({ timeframe, rejected, qualifiedCount }) {
  const count = (s) => rejected.filter((r) => r.status === s).length
  const mismatch = count('TIMEFRAME_MISMATCH')
  const dataMismatch = count('DATA_MISMATCH')
  const compatible =
    rejected.length + qualifiedCount - mismatch - dataMismatch - count('NOT_RUNNABLE') - count('NOT_APPLICABLE')
  return (
    <Panel title="Timeframe">
      <div className="ss-headline ss-mono">{timeframe}</div>
      <dl className="ss-fields">
        <div className="ss-field"><dt>Compatible strategies</dt><dd className="ss-mono">{compatible}</dd></div>
        <div className="ss-field"><dt>Timeframe mismatch</dt><dd className="ss-mono">{mismatch}</dd></div>
        <div className="ss-field"><dt>Data mismatch</dt><dd className="ss-mono">{dataMismatch}</dd></div>
      </dl>
      <p className="ss-meta">Each strategy runs only on the timeframes it was built and validated for.</p>
    </Panel>
  )
}
