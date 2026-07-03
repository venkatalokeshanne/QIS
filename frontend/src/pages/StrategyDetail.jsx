import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Badge from '../components/Badge'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import ScoreBar from '../components/ScoreBar'
import MetricBar from '../components/MetricBar'
import MetricValue from '../components/MetricValue'
import TradesTable from '../components/TradesTable'
import MonthlyBreakdownTable from '../components/MonthlyBreakdownTable'
import EquityCurve from '../components/EquityCurve'
import DailyPnl from '../components/DailyPnl'
import MetricRadar from '../components/MetricRadar'
import { useStrategies, useRunBacktest, useMetricDefinitions } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import {
  trendspiderGuides,
  trendspiderCommonSteps,
  trendspiderRiskManagementSteps,
  buildRiskManagementSteps,
} from '../data/trendspiderGuides'
import './StrategyDetail.css'

// These metrics are already 0-100 scale (format: "percent"), so they
// get a visual bar like the overall score; everything else (currency,
// ratio, count, duration) stays as plain formatted text.
const BAR_METRICS = new Set(['win_rate', 'max_drawdown'])

const TICKER_COMPARE_METRICS = ['net_profit', 'win_rate', 'sharpe_ratio', 'total_trades']

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
  const selectedDatasetIds = useResearchStore((s) => s.selectedDatasetIds)
  const executionSettings = useResearchStore((s) => s.executionSettings)
  const selectedStrategyNames = useResearchStore((s) => s.selectedStrategyNames)
  const setSelectedStrategyNames = useResearchStore((s) => s.setSelectedStrategyNames)
  const strategyParamOverrides = useResearchStore((s) => s.strategyParamOverrides)
  const setStrategyParamOverride = useResearchStore((s) => s.setStrategyParamOverride)
  const resetStrategyParams = useResearchStore((s) => s.resetStrategyParams)
  const breakdownByMonth = useResearchStore((s) => s.breakdownByMonth)
  const setBreakdownByMonth = useResearchStore((s) => s.setBreakdownByMonth)
  const runMutation = useRunBacktest()

  const [tab, setTab] = useState('results')
  // Which selected ticker's Results/Charts are currently shown -- only
  // matters when more than one ticker is selected; defaults to the first.
  const [focusedDatasetId, setFocusedDatasetId] = useState(null)

  const strategy = strategies?.find((s) => s.name === name)
  const paramsOverride = strategyParamOverrides[name] || EMPTY_PARAMS
  const hasOverride = Object.keys(paramsOverride).length > 0
  const effectiveParams = useMemo(
    () => ({ ...(strategy?.default_params || {}), ...paramsOverride }),
    [strategy, paramsOverride]
  )

  const runNow = () => {
    if (selectedDatasetIds.length === 0 || !strategy) return
    runMutation.mutate({
      dataset_ids: selectedDatasetIds,
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
    if (selectedDatasetIds.length === 0 || !strategy) return
    runMutation.mutate({
      dataset_ids: selectedDatasetIds,
      strategy_names: [strategy.name],
      strategy_params: { [strategy.name]: effectiveParams },
      execution: executionSettings,
      breakdown_by_month: breakdownByMonth,
    })
    // Re-run when the strategy, ticker selection, or its own params
    // change, but not on every execution-settings/monthly-breakdown
    // tweak elsewhere -- use "Re-run" for that.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [name, selectedDatasetIds, effectiveParams])

  const datasetResults = runMutation.data?.dataset_results || []

  useEffect(() => {
    if (datasetResults.length === 0) return
    if (!datasetResults.some((d) => d.dataset_id === focusedDatasetId)) {
      setFocusedDatasetId(datasetResults[0].dataset_id)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [datasetResults])

  const metricFormatByName = useMemo(() => {
    const map = {}
    for (const m of metricDefs || []) map[m.name] = m
    return map
  }, [metricDefs])

  const addToBatch = () => {
    if (!selectedStrategyNames.includes(name)) {
      setSelectedStrategyNames([...selectedStrategyNames, name])
    }
    navigate('/run')
  }

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
              <Button variant="primary" onClick={() => navigate('/')}>
                Back to Dashboard
              </Button>
            }
          />
        </Card>
      </div>
    )
  }

  const focusedResult = datasetResults.find((d) => d.dataset_id === focusedDatasetId)
  const result = focusedResult?.results?.[0]
  const tsGuide = trendspiderGuides[name]
  const riskManagementLines = buildRiskManagementSteps(executionSettings)

  // Ranked by overall score across every selected ticker -- each dataset's
  // own `rank` field is meaningless here since only one strategy was
  // requested per ticker (it's always 1), so this is computed locally.
  const tickerRanking = [...datasetResults]
    .map((d) => ({ dataset_id: d.dataset_id, dataset_name: d.dataset_name, result: d.results?.[0] }))
    .filter((r) => r.result)
    .sort((a, b) => (b.result.overall_score ?? -Infinity) - (a.result.overall_score ?? -Infinity))

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
          className={`tab-item${tab === 'charts' ? ' active' : ''}`}
          onClick={() => setTab('charts')}
        >
          Charts
        </button>
        <button
          className={`tab-item${tab === 'tickers' ? ' active' : ''}`}
          onClick={() => setTab('tickers')}
        >
          Tickers
        </button>
        <button
          className={`tab-item${tab === 'configure' ? ' active' : ''}`}
          onClick={() => setTab('configure')}
        >
          Configure
        </button>
        <button
          className={`tab-item${tab === 'trendspider' ? ' active' : ''}`}
          onClick={() => setTab('trendspider')}
        >
          TrendSpider
        </button>
        <button className={`tab-item${tab === 'info' ? ' active' : ''}`} onClick={() => setTab('info')}>
          Info
        </button>
      </div>

      {tab === 'info' && (
        <Card>
          <Badge accent>{strategy.category.replace(/_/g, ' ')}</Badge>
          <p className="strategy-detail-desc">{strategy.description}</p>

          <div className="strategy-detail-indicators">
            {strategy.indicators_used.map((i) => (
              <span key={i} className="mono indicator-chip">
                {i}
              </span>
            ))}
          </div>

          {(strategy.entry_conditions || []).length > 0 && (
            <div className="strategy-detail-conditions">
              <div className="strategy-detail-condition-label">Entry Conditions</div>
              <ul className="strategy-detail-condition-list">
                {strategy.entry_conditions.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {(strategy.exit_conditions || []).length > 0 && (
            <div className="strategy-detail-conditions">
              <div className="strategy-detail-condition-label">Exit Conditions</div>
              <ul className="strategy-detail-condition-list">
                {strategy.exit_conditions.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="strategy-detail-params">
            {Object.entries(strategy.default_params).map(([k, v]) => (
              <div key={k} className="param-row">
                <span className="param-key mono">{k}</span>
                <span className="param-value mono">{String(v)}</span>
              </div>
            ))}
          </div>

          <div className="strategy-detail-actions">
            <Button variant="secondary" onClick={addToBatch}>
              Add to Batch
            </Button>
          </div>
        </Card>
      )}

      {tab === 'configure' && (
        <Card style={{ maxWidth: 480 }}>
          <div className="result-header-row">
            <div className="section-label">Parameters</div>
            <Button size="sm" variant="ghost" onClick={() => resetStrategyParams(name)} disabled={!hasOverride}>
              Reset to Defaults
            </Button>
          </div>
          <p className="field-hint" style={{ marginBottom: 16 }}>
            Changes apply immediately -- Results, Charts, and Tickers all re-run using these values instead of the
            strategy's own defaults.
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

      {tab === 'trendspider' && (
        <>
          <Card style={{ marginBottom: 16 }}>
            <div className="section-label">Setup Steps</div>
            <ol className="ts-guide-steps">
              {trendspiderCommonSteps.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          </Card>

          {tsGuide ? (
            <>
              {tsGuide.directionNote && <div className="field-hint" style={{ marginBottom: 16 }}>{tsGuide.directionNote}</div>}

              <Card style={{ marginBottom: 16 }}>
                <div className="section-label">Indicators to Add</div>
                <div className="ts-guide-list">
                  {tsGuide.indicators.map((ind, i) => (
                    <div key={i} className="ts-guide-row">
                      <span className="ts-guide-row-name mono">{ind.name}</span>
                      <span className="ts-guide-row-detail">{ind.settings}</span>
                    </div>
                  ))}
                </div>
              </Card>

              <Card style={{ marginBottom: 16 }}>
                <div className="section-label">Entry Rules -- Long</div>
                {tsGuide.entryLong.length > 0 ? (
                  <ul className="strategy-detail-condition-list">
                    {tsGuide.entryLong.map((rule, i) => (
                      <li key={i}>{rule}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="field-hint">Not supported by this strategy.</p>
                )}
              </Card>

              {tsGuide.entryShort.length > 0 && (
                <Card style={{ marginBottom: 16 }}>
                  <div className="section-label">Entry Rules -- Short</div>
                  <ul className="strategy-detail-condition-list">
                    {tsGuide.entryShort.map((rule, i) => (
                      <li key={i}>{rule}</li>
                    ))}
                  </ul>
                </Card>
              )}

              <Card style={{ marginBottom: 16 }}>
                <div className="section-label">Exit Rules</div>
                <ul className="strategy-detail-condition-list">
                  {tsGuide.exit.map((rule, i) => (
                    <li key={i}>{rule}</li>
                  ))}
                </ul>
              </Card>

              {riskManagementLines && (
                <Card style={{ marginBottom: 16 }}>
                  <div className="section-label">Risk Management -- Stop Loss / Take Profit</div>
                  <p className="field-hint" style={{ marginBottom: 12 }}>
                    Stops and targets aren't part of this strategy's own rules -- they come from your global{' '}
                    <Link to="/settings" style={{ color: 'var(--accent)' }}>
                      Execution Settings
                    </Link>{' '}
                    and apply the same way to every strategy. Here's what's currently active and how to match it in
                    TrendSpider:
                  </p>
                  <ul className="strategy-detail-condition-list" style={{ marginBottom: 12 }}>
                    {riskManagementLines.map((line, i) => (
                      <li key={i} className="mono">
                        {line}
                      </li>
                    ))}
                  </ul>
                  <ul className="strategy-detail-condition-list">
                    {trendspiderRiskManagementSteps.map((step, i) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ul>
                </Card>
              )}

              {tsGuide.notes.length > 0 && (
                <Card>
                  <div className="section-label">Notes</div>
                  {tsGuide.notes.map((note, i) => (
                    <p key={i} className={note.warning ? 'ts-guide-warning' : 'field-hint'}>
                      {note.warning ? '⚠ ' : ''}
                      {note.text}
                    </p>
                  ))}
                </Card>
              )}
            </>
          ) : (
            <Card>
              <EmptyState title="No guide yet" body="This strategy doesn't have a TrendSpider setup guide written yet." />
            </Card>
          )}
        </>
      )}

      {(tab === 'results' || tab === 'charts') && (
        <>
          {selectedDatasetIds.length === 0 && (
            <Card>
              <EmptyState
                title="Select ticker(s)"
                body="Choose one or more tickers from the header above to run this strategy."
              />
            </Card>
          )}

          {selectedDatasetIds.length > 0 && runMutation.isPending && (
            <Card>
              <div className="loading-text">Running {strategy.display_name}…</div>
            </Card>
          )}

          {selectedDatasetIds.length > 0 && runMutation.isError && (
            <div className="error-banner">{runMutation.error.message}</div>
          )}

          {selectedDatasetIds.length > 0 && result && !runMutation.isPending && (
            <>
              {datasetResults.length > 1 && (
                <div className="chip-row" style={{ marginBottom: 16 }}>
                  {datasetResults.map((d) => (
                    <button
                      key={d.dataset_id}
                      type="button"
                      className={`chip${focusedDatasetId === d.dataset_id ? ' active' : ''}`}
                      onClick={() => setFocusedDatasetId(d.dataset_id)}
                    >
                      {d.dataset_name}
                    </button>
                  ))}
                </div>
              )}

              {tab === 'results' && (
                <>
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

              {tab === 'charts' && (
                <div className="charts-tab">
                  <Card className="charts-main">
                    <div className="detail-metric-label">P&amp;L by Date</div>
                    <DailyPnl trades={result.trades} main />
                  </Card>

                  <div className="charts-row">
                    <Card>
                      <div className="detail-metric-label">Equity Curve</div>
                      <EquityCurve trades={result.trades} />
                    </Card>

                    <Card>
                      <div className="detail-metric-label">Strategy Fingerprint</div>
                      <MetricRadar metrics={result.metrics} />
                    </Card>
                  </div>

                  <Card style={{ marginTop: 16 }}>
                    <div className="detail-panel">
                      {(metricDefs || [])
                        .filter((def) => BAR_METRICS.has(def.name))
                        .map((def) => (
                          <div key={def.name} className="detail-metric">
                            <div className="detail-metric-label">{def.display_name}</div>
                            <MetricBar value={result.metrics[def.name]} />
                          </div>
                        ))}
                    </div>
                  </Card>
                </div>
              )}
            </>
          )}
        </>
      )}

      {tab === 'tickers' && (
        <>
          {selectedDatasetIds.length === 0 && (
            <Card>
              <EmptyState
                title="Select ticker(s)"
                body="Choose one or more tickers from the header above to compare this strategy across them."
              />
            </Card>
          )}

          {selectedDatasetIds.length > 0 && runMutation.isPending && (
            <Card>
              <div className="loading-text">Running {strategy.display_name}…</div>
            </Card>
          )}

          {selectedDatasetIds.length > 0 && runMutation.isError && (
            <div className="error-banner">{runMutation.error.message}</div>
          )}

          {selectedDatasetIds.length > 0 && tickerRanking.length > 0 && !runMutation.isPending && (
            <Card tight>
              <div className="data-table-scroll">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Ticker</th>
                      {TICKER_COMPARE_METRICS.map((metricName) => (
                        <th key={metricName} className="align-right">
                          {metricFormatByName[metricName]?.display_name || metricName}
                        </th>
                      ))}
                      <th>Overall Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tickerRanking.map((t, i) => (
                      <tr
                        key={t.dataset_id}
                        className="clickable"
                        onClick={() => {
                          setFocusedDatasetId(t.dataset_id)
                          setTab('results')
                        }}
                      >
                        <td>
                          <span className={`rank-badge${i === 0 ? ' rank-1' : ''}`}>
                            {String(i + 1).padStart(2, '0')}
                          </span>
                        </td>
                        <td style={{ fontWeight: 600 }}>{t.dataset_name}</td>
                        {TICKER_COMPARE_METRICS.map((metricName) => (
                          <td key={metricName} className="align-right">
                            <MetricValue
                              value={t.result.metrics[metricName]}
                              format={metricFormatByName[metricName]?.format}
                            />
                          </td>
                        ))}
                        <td>
                          <ScoreBar score={t.result.overall_score} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
