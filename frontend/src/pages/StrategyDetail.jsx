import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import ScoreBar from '../components/ScoreBar'
import MetricBar from '../components/MetricBar'
import MetricValue from '../components/MetricValue'
import TradesTable from '../components/TradesTable'
import MonthlyBreakdownTable from '../components/MonthlyBreakdownTable'
import {
  useStrategies,
  useRunBacktest,
  useMetricDefinitions,
  useSignalChecks,
  useWatches,
  useCreateWatch,
  useDeleteWatch,
} from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { formatDateTime } from '../utils/format'
import './StrategyDetail.css'

// These metrics are already 0-100 scale (format: "percent"), so they
// get a visual bar like the overall score; everything else (currency,
// ratio, count, duration) stays as plain formatted text.
const BAR_METRICS = new Set(['win_rate', 'max_drawdown'])

function signalBadgeTone(signal) {
  if (signal.event === 'entry') return signal.direction === 'long' ? 'positive' : 'negative'
  if (signal.position === 'long') return 'positive'
  if (signal.position === 'short') return 'negative'
  return 'neutral'
}

function signalBadgeText(signal) {
  if (signal.event === 'entry') return `New ${signal.direction === 'long' ? 'LONG' : 'SHORT'} entry`
  if (signal.event === 'exit') return `Exit (${signal.exit_reason || 'signal'})`
  if (signal.position === 'long') return 'Currently LONG'
  if (signal.position === 'short') return 'Currently SHORT'
  return 'Flat'
}

// Stable empty-object reference so "no override set for this strategy"
// doesn't produce a new {} every render -- that would break the
// useMemo/useEffect dependencies built on top of it (see effectiveParams).
const EMPTY_PARAMS = {}

function renderParamInput(key, value, onChange) {
  if (key === 'direction') {
    return (
      <select className="field-input" value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="both">Long &amp; Short</option>
        <option value="long_only">Long only</option>
        <option value="short_only">Short only</option>
      </select>
    )
  }
  if (typeof value === 'boolean') {
    return (
      <label className="checkbox-row">
        <input type="checkbox" checked={value} onChange={(e) => onChange(e.target.checked)} />
        <span>{value ? 'Enabled' : 'Disabled'}</span>
      </label>
    )
  }
  if (Array.isArray(value)) {
    return (
      <input
        type="text"
        className="field-input mono"
        value={value.join(', ')}
        onChange={(e) =>
          onChange(
            e.target.value
              .split(',')
              .map((s) => Number(s.trim()))
              .filter((n) => !Number.isNaN(n))
          )
        }
      />
    )
  }
  if (typeof value === 'number') {
    return (
      <input
        type="number"
        step="any"
        className="field-input"
        value={value}
        onChange={(e) => onChange(e.target.value === '' ? 0 : Number(e.target.value))}
      />
    )
  }
  return <input type="text" className="field-input" value={value} onChange={(e) => onChange(e.target.value)} />
}

export default function StrategyDetail() {
  const { name } = useParams()
  const navigate = useNavigate()
  const { data: strategies, isLoading: strategiesLoading } = useStrategies()
  const { data: metricDefs } = useMetricDefinitions()
  const selectedSymbols = useResearchStore((s) => s.selectedSymbols)
  const selectedInterval = useResearchStore((s) => s.selectedInterval)
  const backtestStartDate = useResearchStore((s) => s.backtestStartDate)
  const backtestEndDate = useResearchStore((s) => s.backtestEndDate)
  const executionSettings = useResearchStore((s) => s.executionSettings)
  const strategyParamOverrides = useResearchStore((s) => s.strategyParamOverrides)
  const setStrategyParamOverride = useResearchStore((s) => s.setStrategyParamOverride)
  const resetStrategyParams = useResearchStore((s) => s.resetStrategyParams)
  const breakdownByMonth = useResearchStore((s) => s.breakdownByMonth)
  const setBreakdownByMonth = useResearchStore((s) => s.setBreakdownByMonth)
  const runMutation = useRunBacktest()

  const [tab, setTab] = useState('results')
  // Which selected ticker's Results are currently shown -- only matters
  // when more than one ticker is selected; defaults to the first.
  const [focusedSymbol, setFocusedSymbol] = useState(null)
  // Same idea for Live Signal's own ticker switcher -- independent of
  // focusedSymbol since Results/Live Signal aren't necessarily looking
  // at the same ticker at the same time.
  const [focusedSignalSymbol, setFocusedSignalSymbol] = useState(null)

  const strategy = strategies?.find((s) => s.name === name)
  const paramsOverride = strategyParamOverrides[name] || EMPTY_PARAMS
  const hasOverride = Object.keys(paramsOverride).length > 0
  const effectiveParams = useMemo(
    () => ({ ...(strategy?.default_params || {}), ...paramsOverride }),
    [strategy, paramsOverride]
  )

  // Same tickers selected in the header (TickerSelect) that every other
  // tab on this page already runs against, checked at the header's one
  // global timeframe.
  const signalTickers = useMemo(
    () => selectedSymbols.map((symbol) => ({ symbol, interval: selectedInterval })),
    [selectedSymbols, selectedInterval]
  )
  const signalQueries = useSignalChecks(signalTickers, name, effectiveParams, executionSettings)

  const { data: watches } = useWatches()
  const createWatch = useCreateWatch()
  const deleteWatch = useDeleteWatch()
  const findWatch = (symbol) =>
    (watches || []).find((w) => w.symbol === symbol && w.strategy_name === name && w.interval === selectedInterval)
  const toggleWatch = (symbol) => {
    const existing = findWatch(symbol)
    if (existing) {
      deleteWatch.mutate(existing.id)
    } else {
      createWatch.mutate({
        symbol,
        strategy_name: name,
        strategy_params: effectiveParams,
        interval: selectedInterval,
        execution: executionSettings,
      })
    }
  }

  useEffect(() => {
    if (signalTickers.length === 0) return
    if (!signalTickers.some((t) => t.symbol === focusedSignalSymbol)) {
      setFocusedSignalSymbol(signalTickers[0].symbol)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signalTickers])

  const runNow = () => {
    if (selectedSymbols.length === 0 || !strategy) return
    runMutation.mutate({
      symbols: selectedSymbols,
      interval: selectedInterval,
      start_date: backtestStartDate,
      end_date: backtestEndDate,
      strategy_names: [strategy.name],
      strategy_params: { [strategy.name]: effectiveParams },
      execution: executionSettings,
      breakdown_by_month: breakdownByMonth,
    })
  }

  useEffect(() => {
    setTab('results')
  }, [name])

  useEffect(() => {
    if (selectedSymbols.length === 0 || !strategy) return
    runMutation.mutate({
      symbols: selectedSymbols,
      interval: selectedInterval,
      start_date: backtestStartDate,
      end_date: backtestEndDate,
      strategy_names: [strategy.name],
      strategy_params: { [strategy.name]: effectiveParams },
      execution: executionSettings,
      breakdown_by_month: breakdownByMonth,
    })
    // Re-run when the strategy, ticker selection, or its own params
    // change, but not on every execution-settings/monthly-breakdown
    // tweak elsewhere -- use "Re-run" for that.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name, selectedSymbols, effectiveParams])

  const tickerResults = runMutation.data?.ticker_results || []

  useEffect(() => {
    if (tickerResults.length === 0) return
    if (!tickerResults.some((t) => t.symbol === focusedSymbol)) {
      setFocusedSymbol(tickerResults[0].symbol)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tickerResults])

  if (strategiesLoading) {
    return <div className="loading-text">Loading…</div>
  }

  if (!strategy) {
    return (
      <div>
        <PageHeader title="Strategy not found" />
        <Card>
          <EmptyState
            title="Unknown strategy"
            body="This strategy doesn't exist (it may have been removed)."
            action={
              <Button variant="primary" onClick={() => navigate('/run')}>
                Back to Run Backtests
              </Button>
            }
          />
        </Card>
      </div>
    )
  }

  const focusedResult = tickerResults.find((t) => t.symbol === focusedSymbol)
  const result = focusedResult?.results?.[0]

  return (
    <div>
      <div className="tab-bar">
        <button
          className={`tab-item${tab === 'results' ? ' active' : ''}`}
          onClick={() => setTab('results')}
        >
          Results
        </button>
        <button
          className={`tab-item${tab === 'configure' ? ' active' : ''}`}
          onClick={() => setTab('configure')}
        >
          Configure
        </button>
        <button
          className={`tab-item${tab === 'signal' ? ' active' : ''}`}
          onClick={() => setTab('signal')}
        >
          Live Signal
        </button>
      </div>

      {tab === 'configure' && (
        <Card style={{ maxWidth: 480 }}>
          <div className="result-header-row">
            <div className="section-label">Parameters</div>
            <Button size="sm" variant="ghost" onClick={() => resetStrategyParams(name)} disabled={!hasOverride}>
              Reset to Defaults
            </Button>
          </div>
          <p className="field-hint" style={{ marginBottom: 16 }}>
            Changes apply immediately -- Results re-runs using these values instead of the strategy's own defaults.
          </p>

          {Object.entries(strategy.default_params).map(([key, defaultValue]) => (
            <div className="field-group" key={key}>
              <label className="field-label mono">{key}</label>
              {renderParamInput(key, effectiveParams[key], (value) => setStrategyParamOverride(name, key, value))}
              {paramsOverride[key] !== undefined && (
                <span className="field-hint">Default: {String(defaultValue)}</span>
              )}
            </div>
          ))}
        </Card>
      )}

      {tab === 'signal' && (
        <>
          {signalTickers.length === 0 && (
            <Card>
              <EmptyState
                title="No tickers selected"
                body="Select ticker(s) using the header's ticker picker to live-check this strategy against them."
              />
            </Card>
          )}

          {signalTickers.length > 0 && (
            <div className="chip-row" style={{ marginBottom: 16 }}>
              {signalTickers.map((ticker) => (
                <button
                  key={ticker.symbol}
                  type="button"
                  className={`chip${focusedSignalSymbol === ticker.symbol ? ' active' : ''}`}
                  onClick={() => setFocusedSignalSymbol(ticker.symbol)}
                >
                  {ticker.symbol}
                </button>
              ))}
            </div>
          )}

          {signalTickers.map((ticker, i) => {
            if (ticker.symbol !== focusedSignalSymbol) return null
            const query = signalQueries[i]
            return (
              <Card key={`${ticker.symbol}-${ticker.interval}`} className="strategy-result-metrics">
                <div className="result-header-row">
                  <div className="detail-metric">
                    <div className="detail-metric-label">Price</div>
                    {query.data ? (
                      <MetricValue value={query.data.price} format="currency" />
                    ) : (
                      <span className="loading-text">—</span>
                    )}
                  </div>
                  {query.data && (
                    <div className="detail-metric">
                      <div className="detail-metric-label">As Of</div>
                      <div>{formatDateTime(query.data.as_of)}</div>
                    </div>
                  )}
                  <Button
                    size="sm"
                    variant={findWatch(ticker.symbol) ? 'primary' : 'secondary'}
                    onClick={() => toggleWatch(ticker.symbol)}
                    title={
                      findWatch(ticker.symbol)
                        ? 'Telegram alerts on for this signal — click to turn off'
                        : 'Get a Telegram message when this signal fires'
                    }
                  >
                    🔔 {findWatch(ticker.symbol) ? 'Alerting' : 'Notify'}
                  </Button>
                </div>

                {query.isError && <div className="error-banner">{query.error.message}</div>}
                {!query.isError && query.isPending && <div className="loading-text">Checking {ticker.symbol}…</div>}

                {query.data && (
                  <div className="detail-panel">
                    <div className="detail-metric">
                      <div className="detail-metric-label">Signal</div>
                      <div className={`signal-badge signal-badge-${signalBadgeTone(query.data)}`}>
                        {signalBadgeText(query.data)}
                      </div>
                    </div>
                  </div>
                )}

                {query.data && query.data.today_events.length > 0 && (
                  <div className="detail-panel" style={{ marginTop: 12 }}>
                    <div className="detail-metric-label" style={{ marginBottom: 8 }}>
                      Today's Signals
                    </div>
                    <div className="data-table-scroll">
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Time</th>
                            <th>Event</th>
                            <th>Detail</th>
                          </tr>
                        </thead>
                        <tbody>
                          {query.data.today_events.map((e, idx) => (
                            <tr key={idx}>
                              <td>{formatDateTime(e.time)}</td>
                              <td>
                                <span
                                  className={`signal-badge signal-badge-${
                                    e.event === 'entry' ? (e.direction === 'long' ? 'positive' : 'negative') : 'neutral'
                                  }`}
                                >
                                  {e.event === 'entry' ? `${e.direction === 'long' ? 'LONG' : 'SHORT'} entry` : 'Exit'}
                                </span>
                              </td>
                              <td>{e.event === 'exit' ? e.exit_reason || 'signal' : '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </Card>
            )
          })}
        </>
      )}

      {tab === 'results' && (
        <>
          {selectedSymbols.length === 0 && (
            <Card>
              <EmptyState
                title="Select ticker(s)"
                body="Choose one or more tickers from the header above to run this strategy."
              />
            </Card>
          )}

          {selectedSymbols.length > 0 && runMutation.isPending && (
            <Card>
              <div className="loading-text">Running {strategy.display_name}…</div>
            </Card>
          )}

          {selectedSymbols.length > 0 && runMutation.isError && (
            <Card>
              <div className="error-banner">{runMutation.error.message}</div>
              <Button size="sm" variant="secondary" onClick={runNow} style={{ marginTop: 12 }}>
                Retry
              </Button>
            </Card>
          )}

          {selectedSymbols.length > 0 && result && !runMutation.isPending && !runMutation.isError && (
            <>
              {tickerResults.length > 1 && (
                <div className="chip-row" style={{ marginBottom: 16 }}>
                  {tickerResults.map((t) => (
                    <button
                      key={t.symbol}
                      type="button"
                      className={`chip${focusedSymbol === t.symbol ? ' active' : ''}`}
                      onClick={() => setFocusedSymbol(t.symbol)}
                    >
                      {t.symbol}
                    </button>
                  ))}
                </div>
              )}

              <Card className="strategy-result-metrics">
                <div className="result-header-row">
                  <div className="detail-metric">
                    <div className="detail-metric-label">Overall Score</div>
                    <ScoreBar score={result.overall_score} />
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <label className="checkbox-row">
                      <input
                        type="checkbox"
                        checked={breakdownByMonth}
                        onChange={(e) => setBreakdownByMonth(e.target.checked)}
                      />
                      <span>Monthly breakdown</span>
                    </label>
                    <Button size="sm" variant="secondary" onClick={runNow}>
                      Re-run
                    </Button>
                  </div>
                </div>

                <div className="detail-panel">
                  {(metricDefs || []).map((def) => (
                    <div key={def.name} className="detail-metric">
                      <div className="detail-metric-label">{def.display_name}</div>
                      {BAR_METRICS.has(def.name) ? (
                        <MetricBar value={result.metrics[def.name]} />
                      ) : (
                        <MetricValue value={result.metrics[def.name]} format={def.format} />
                      )}
                    </div>
                  ))}
                </div>
              </Card>

              {result.monthly_metrics && (
                <Card tight style={{ marginTop: 16 }}>
                  <div className="section-label" style={{ padding: '16px 16px 0' }}>
                    Monthly Breakdown
                  </div>
                  <MonthlyBreakdownTable monthlyMetrics={result.monthly_metrics} />
                </Card>
              )}

              <Card tight style={{ marginTop: 16 }}>
                <TradesTable trades={result.trades} />
              </Card>
            </>
          )}
        </>
      )}
    </div>
  )
}
