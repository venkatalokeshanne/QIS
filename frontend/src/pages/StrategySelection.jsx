import { useState } from 'react'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import { useStrategySelection } from '../api/hooks'
import {
  MarketRegimePanel,
  TickerRegimePanel,
  PremarketRegimePanel,
  TimeframePanel,
  StrategyFamilyPanel,
  QualifiedStrategiesTable,
  StrategySelectionFlow,
  WhyNotSection,
} from '../components/StrategySelector'
import '../components/StrategySelector/StrategySelector.css'

const TIMEFRAMES = ['1m', '5m', '15m', '30m', '65m', '1h', '2h', '4h', '1D', '1W', '1M']

const STATUS_TEXT = {
  QUALIFIED_STRATEGIES_AVAILABLE: 'Qualified strategies available',
  NO_QUALIFIED_STRATEGY: 'No strategy qualifies right now',
  DATA_INSUFFICIENT: 'Not enough data to decide',
}

export default function StrategySelection() {
  const [ticker, setTicker] = useState('AAPL')
  const [timeframe, setTimeframe] = useState('5m')
  const [timestamp, setTimestamp] = useState('')
  const [includePremarket, setIncludePremarket] = useState(true)
  const select = useStrategySelection()
  const result = select.data

  const run = (e) => {
    e.preventDefault()
    if (!ticker.trim()) return
    select.mutate({ ticker: ticker.trim().toUpperCase(), timeframe, timestamp: timestamp || undefined, includePremarket })
  }

  const errorText =
    select.error && (select.error.response?.data?.detail || select.error.message || 'Request failed')

  return (
    <div className="ss-root">
      <PageHeader
        title="Strategy Selection"
        subtitle="Which strategies have historically held up in conditions like now — market, ticker and premarket regime — and why the rest don't. No trade signals."
      />

      <Card>
        <form className="ss-form" onSubmit={run}>
          <div className="field-group">
            <label className="field-label" htmlFor="ss-ticker">Ticker</label>
            <input id="ss-ticker" className="field-input ss-ticker" value={ticker} onChange={(e) => setTicker(e.target.value)} />
          </div>
          <div className="field-group">
            <label className="field-label" htmlFor="ss-tf">Timeframe</label>
            <select id="ss-tf" className="field-input" value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
              {TIMEFRAMES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div className="field-group">
            <label className="field-label" htmlFor="ss-ts">Decision time (New York, optional)</label>
            <input
              id="ss-ts"
              type="datetime-local"
              className="field-input"
              value={timestamp}
              onChange={(e) => setTimestamp(e.target.value)}
            />
          </div>
          <label className="ss-check">
            <input type="checkbox" checked={includePremarket} onChange={(e) => setIncludePremarket(e.target.checked)} />
            Include premarket
          </label>
          <Button variant="primary" type="submit" disabled={select.isPending}>
            {select.isPending ? 'Selecting…' : 'Select strategies'}
          </Button>
        </form>
      </Card>

      {errorText && <div className="error-banner">{String(errorText)}</div>}

      {!result && !select.isPending && !errorText && (
        <EmptyState
          title="Pick a ticker and timeframe"
          body="Leave the time empty for now, or set a past time to replay what the engine would have said then."
        />
      )}

      {result && (
        <>
          <div className="ss-status">
            <span className="ss-status-title">{STATUS_TEXT[result.status] || result.status}</span>
            <span className="ss-status-meta">
              {result.ticker} · {result.timeframe} · decision {result.decision_ts}
              {result.log_id != null && ` · log #${result.log_id}`}
            </span>
          </div>

          <StrategySelectionFlow result={result} />

          <div className="ss-grid">
            <MarketRegimePanel regime={result.market_regime} />
            <TickerRegimePanel ticker={result.ticker} regime={result.ticker_regime} />
            <PremarketRegimePanel regime={result.premarket_regime} included={includePremarket} />
            <TimeframePanel
              timeframe={result.timeframe}
              rejected={result.rejected_strategies || []}
              qualifiedCount={(result.qualified_strategies || []).length}
            />
            <StrategyFamilyPanel
              eligible={result.eligible_families}
              lowerPriority={result.lower_priority_families}
              rules={result.family_rules}
              notes={result.family_notes}
            />
          </div>

          <Card className="ss-panel">
            <h3 className="ss-title">Qualified strategies ({(result.qualified_strategies || []).length})</h3>
            {(result.qualified_strategies || []).length ? (
              <>
                <QualifiedStrategiesTable rows={result.qualified_strategies} />
                <p className="ss-meta">Ranked by regime-matched PF, then out-of-sample PF. Click a row for the full reasoning.</p>
              </>
            ) : (
              <p className="ss-meta">
                None passed every check for this ticker, timeframe and regime. Standing aside is a valid outcome — see below
                for what each strategy was missing.
              </p>
            )}
          </Card>

          <WhyNotSection rejected={result.rejected_strategies || []} />

          {(result.notes || []).length > 0 && (
            <Card className="ss-panel">
              <h3 className="ss-title">Notes</h3>
              <ul className="ss-notes">
                {result.notes.map((n, i) => (
                  <li key={i}>{n}</li>
                ))}
              </ul>
            </Card>
          )}

          {result.versions && (
            <p className="ss-meta ss-mono">
              {Object.entries(result.versions)
                .map(([k, v]) => `${k}=${typeof v === 'object' ? JSON.stringify(v) : v}`)
                .join(' · ')}
            </p>
          )}
        </>
      )}
    </div>
  )
}
