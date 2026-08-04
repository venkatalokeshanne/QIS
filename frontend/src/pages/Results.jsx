import { useEffect, useMemo, useState, Fragment } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import ScoreBar from '../components/ScoreBar'
import MetricValue from '../components/MetricValue'
import TradesTable from '../components/TradesTable'
import SortableTh from '../components/SortableTh'
import { useSortableData } from '../hooks/useSortableData'
import { useMetricDefinitions } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { formatDate } from '../utils/format'
import './Compare.css' // shares .compare-table / .compare-sticky-col / .best-cell with MatrixView below

const SUMMARY_METRIC_ORDER = [
  'net_profit',
  'win_rate',
  'profit_factor',
  'sharpe_ratio',
  'max_drawdown',
  'total_trades',
]

export default function Results() {
  const navigate = useNavigate()
  const lastRunResults = useResearchStore((s) => s.lastRunResults)
  const compareSymbol = useResearchStore((s) => s.compareSymbol)
  const compareSelection = useResearchStore((s) => s.compareSelection)
  const setCompareSelection = useResearchStore((s) => s.setCompareSelection)
  const { data: metricDefs } = useMetricDefinitions()
  const [expandedKey, setExpandedKey] = useState(null)
  const [view, setView] = useState('grouped') // 'grouped' | 'matrix' -- matrix only shown for 2+ tickers
  const [focusedSymbol, setFocusedSymbol] = useState(null)

  const metricFormatByName = useMemo(() => {
    const map = {}
    for (const m of metricDefs || []) map[m.name] = m
    return map
  }, [metricDefs])

  const tickerResults = lastRunResults?.ticker_results || []

  useEffect(() => {
    if (tickerResults.length === 0) return
    if (!tickerResults.some((t) => t.symbol === focusedSymbol)) {
      setFocusedSymbol(tickerResults[0].symbol)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tickerResults])

  if (!lastRunResults) {
    return (
      <div>
        <PageHeader title="Results" subtitle="Run a backtest to see ranked results here." />
        <Card>
          <EmptyState
            title="No results yet"
            body="Run backtests against a ticker to see strategies ranked by overall score."
            action={
              <Button variant="primary" onClick={() => navigate('/run')}>
                Run Backtests
              </Button>
            }
          />
        </Card>
      </div>
    )
  }

  const isMultiTicker = tickerResults.length > 1
  const focusedResult = tickerResults.find((t) => t.symbol === focusedSymbol)

  const toggleCompare = (symbol, strategyName) => {
    const current = symbol === compareSymbol ? compareSelection : []
    setCompareSelection(
      symbol,
      current.includes(strategyName) ? current.filter((n) => n !== strategyName) : [...current, strategyName]
    )
  }

  return (
    <div>
      <PageHeader
        title="Results"
        subtitle={
          isMultiTicker
            ? `${tickerResults.length} tickers × ${tickerResults[0].results.length} strategies.`
            : `${tickerResults[0]?.results.length ?? 0} strategies ranked by overall score. Click a row for full metrics.`
        }
        actions={
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            {isMultiTicker && (
              <div className="chip-row">
                <button
                  type="button"
                  className={`chip${view === 'grouped' ? ' active' : ''}`}
                  onClick={() => setView('grouped')}
                >
                  Grouped by Ticker
                </button>
                <button
                  type="button"
                  className={`chip${view === 'matrix' ? ' active' : ''}`}
                  onClick={() => setView('matrix')}
                >
                  Matrix
                </button>
              </div>
            )}
            {compareSelection.length > 0 && (
              <Button variant="primary" onClick={() => navigate('/compare')}>
                Compare {compareSelection.length} Selected →
              </Button>
            )}
          </div>
        }
      />

      {(!isMultiTicker || view === 'grouped') && (
        <>
          {isMultiTicker && (
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

          {focusedResult && (
            <StrategyRankTable
              results={focusedResult.results}
              symbol={focusedResult.symbol}
              compareSymbol={compareSymbol}
              compareSelection={compareSelection}
              toggleCompare={toggleCompare}
              metricDefs={metricDefs}
              metricFormatByName={metricFormatByName}
              expandedKey={expandedKey}
              setExpandedKey={setExpandedKey}
            />
          )}
        </>
      )}

      {isMultiTicker && view === 'matrix' && (
        <MatrixView tickerResults={tickerResults} />
      )}
    </div>
  )
}

function getStrategyRowValue(r, key) {
  if (key === 'rank') return r.rank
  if (key === 'strategy') return r.strategy_display_name
  if (key === 'overall_score') return r.overall_score
  if (key === 'wins') return winLossCounts(r.metrics).wins
  return r.metrics[key]
}

function winLossCounts(metrics) {
  const total = metrics.total_trades ?? 0
  const winRate = metrics.win_rate
  if (!total || winRate == null) return { wins: null, losses: null }
  const wins = Math.round((winRate / 100) * total)
  return { wins, losses: total - wins }
}

const HISTORICAL_METRIC_ORDER = ['average_holding_time', 'max_drawdown', 'profit_factor', 'win_rate']

function StrategyRankTable({
  results,
  symbol,
  compareSymbol,
  compareSelection,
  toggleCompare,
  metricDefs,
  metricFormatByName,
  expandedKey,
  setExpandedKey,
}) {
  const { sorted, sortKey, sortDir, toggleSort } = useSortableData(results, getStrategyRowValue, 'rank', 'asc')

  return (
    <Card tight>
      <div className="data-table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: 36 }}></th>
              <SortableTh label="Rank" sortKey="rank" activeKey={sortKey} dir={sortDir} onSort={toggleSort} />
              <SortableTh label="Strategy" sortKey="strategy" activeKey={sortKey} dir={sortDir} onSort={toggleSort} />
              {SUMMARY_METRIC_ORDER.map((name) => (
                <SortableTh
                  key={name}
                  label={metricFormatByName[name]?.display_name || name}
                  sortKey={name}
                  activeKey={sortKey}
                  dir={sortDir}
                  onSort={toggleSort}
                  align="right"
                />
              ))}
              <SortableTh
                label="Wins / Losses"
                sortKey="wins"
                activeKey={sortKey}
                dir={sortDir}
                onSort={toggleSort}
                align="right"
              />
              <th className="align-right">Historical W/L</th>
              <SortableTh
                label="Overall Score"
                sortKey="overall_score"
                activeKey={sortKey}
                dir={sortDir}
                onSort={toggleSort}
              />
            </tr>
          </thead>
          <tbody>
            {sorted.map((r) => {
              const key = `${symbol}:${r.strategy_name}`
              const checked = symbol === compareSymbol && compareSelection.includes(r.strategy_name)
              return (
                <Fragment key={key}>
                  <tr
                    className={`clickable${expandedKey === key ? ' selected' : ''}`}
                    onClick={() => setExpandedKey(expandedKey === key ? null : key)}
                  >
                    <td onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleCompare(symbol, r.strategy_name)}
                        style={{ accentColor: 'var(--accent)' }}
                      />
                    </td>
                    <td>
                      {r.rank ? (
                        <span className={`rank-badge${r.rank === 1 ? ' rank-1' : ''}`}>
                          {String(r.rank).padStart(2, '0')}
                        </span>
                      ) : (
                        <span className="rank-badge">—</span>
                      )}
                    </td>
                    <td style={{ fontWeight: 600 }}>{r.strategy_display_name}</td>
                    {SUMMARY_METRIC_ORDER.map((name) => (
                      <td key={name} className="align-right">
                        <MetricValue value={r.metrics[name]} format={metricFormatByName[name]?.format} />
                      </td>
                    ))}
                    <td className="align-right mono">
                      {(() => {
                        const { wins, losses } = winLossCounts(r.metrics)
                        return wins == null ? '—' : `${wins} / ${losses}`
                      })()}
                    </td>
                    <td className="align-right mono">
                      {(() => {
                        if (!r.historical_metrics) return '—'
                        const { wins, losses } = winLossCounts(r.historical_metrics)
                        return wins == null ? '—' : `${wins} / ${losses}`
                      })()}
                    </td>
                    <td>
                      <ScoreBar score={r.overall_score} />
                    </td>
                  </tr>
                  {expandedKey === key && (
                    <tr>
                      <td colSpan={SUMMARY_METRIC_ORDER.length + 6} style={{ padding: 0, background: 'var(--bg-base)' }}>
                        <DetailPanel
                          metrics={r.metrics}
                          metricDefs={metricDefs}
                          metricFormatByName={metricFormatByName}
                          trades={r.trades}
                          historicalMetrics={r.historical_metrics}
                          historicalTradeCount={r.historical_trade_count}
                          historicalPeriodStart={r.historical_period_start}
                          historicalPeriodEnd={r.historical_period_end}
                        />
                      </td>
                    </tr>
                  )}
                </Fragment>
              )
            })}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

function MatrixView({ tickerResults }) {
  // The same strategy_names were requested for every ticker in one run, so
  // the first ticker's own result order is a stable row order for all of them.
  const strategyOrder = tickerResults[0]?.results.map((r) => ({
    name: r.strategy_name,
    display_name: r.strategy_display_name,
  })) || []

  const scoreFor = (symbol, strategyName) => {
    const ticker = tickerResults.find((t) => t.symbol === symbol)
    return ticker?.results.find((r) => r.strategy_name === strategyName)?.overall_score ?? null
  }

  const bestScoreByStrategy = {}
  for (const s of strategyOrder) {
    const scores = tickerResults.map((t) => scoreFor(t.symbol, s.name)).filter((v) => v !== null)
    bestScoreByStrategy[s.name] = scores.length ? Math.max(...scores) : null
  }

  const getMatrixValue = (s, key) => (key === 'strategy' ? s.display_name : scoreFor(key, s.name))
  const { sorted, sortKey, sortDir, toggleSort } = useSortableData(strategyOrder, getMatrixValue)

  return (
    <Card tight>
      <div className="data-table-scroll">
        <table className="data-table compare-table">
          <thead>
            <tr>
              <SortableTh
                label="Strategy"
                sortKey="strategy"
                activeKey={sortKey}
                dir={sortDir}
                onSort={toggleSort}
                className="compare-sticky-col"
              />
              {tickerResults.map((t) => (
                <SortableTh
                  key={t.symbol}
                  label={t.symbol}
                  sortKey={t.symbol}
                  activeKey={sortKey}
                  dir={sortDir}
                  onSort={toggleSort}
                  align="right"
                />
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((s) => (
              <tr key={s.name}>
                <td className="compare-sticky-col" style={{ fontWeight: 600 }}>
                  {s.display_name}
                </td>
                {tickerResults.map((t) => {
                  const score = scoreFor(t.symbol, s.name)
                  const isBest = score !== null && score === bestScoreByStrategy[s.name]
                  return (
                    <td key={t.symbol} className={`align-right${isBest ? ' best-cell' : ''}`}>
                      <span className="mono">{score?.toFixed(1) ?? '—'}</span>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

function DetailPanel({
  metrics,
  metricDefs,
  metricFormatByName,
  trades,
  historicalMetrics,
  historicalTradeCount,
  historicalPeriodStart,
  historicalPeriodEnd,
}) {
  return (
    <div>
      <div className="detail-panel">
        {(metricDefs || []).map((def) => (
          <div key={def.name} className="detail-metric">
            <div className="detail-metric-label">{def.display_name}</div>
            <MetricValue value={metrics[def.name]} format={def.format} />
          </div>
        ))}
      </div>

      {historicalMetrics && (
        <div style={{ marginTop: 16 }}>
          <div className="detail-metric-label" style={{ marginBottom: 8 }}>
            Historical Performance
            <span
              title='How this same ticker+strategy has performed over the trailing year, not just the date range requested above -- use this to tell "worked well this month" apart from "has actually held up over time."'
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 14,
                height: 14,
                marginLeft: 6,
                borderRadius: '50%',
                border: '1px solid var(--text-muted)',
                color: 'var(--text-muted)',
                fontSize: 10,
                fontWeight: 700,
                cursor: 'help',
              }}
            >
              i
            </span>
            <span style={{ fontWeight: 400, marginLeft: 8 }}>
              {formatDate(historicalPeriodStart)} – {formatDate(historicalPeriodEnd)} · {historicalTradeCount} trades
            </span>
          </div>
          <div className="detail-panel">
            {HISTORICAL_METRIC_ORDER.map((name) => (
              <div key={name} className="detail-metric">
                <div className="detail-metric-label">{metricFormatByName[name]?.display_name || name}</div>
                <MetricValue value={historicalMetrics[name]} format={metricFormatByName[name]?.format} />
              </div>
            ))}
            <div className="detail-metric">
              <div className="detail-metric-label">Wins / Losses</div>
              <span className="mono">
                {(() => {
                  const { wins, losses } = winLossCounts(historicalMetrics)
                  return wins == null ? '—' : `${wins} / ${losses}`
                })()}
              </span>
            </div>
          </div>
        </div>
      )}

      <TradesTable trades={trades} />
    </div>
  )
}
