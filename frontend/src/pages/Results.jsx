import { useMemo, useState, Fragment } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import ScoreBar from '../components/ScoreBar'
import MetricValue from '../components/MetricValue'
import TradesTable from '../components/TradesTable'
import { useMetricDefinitions } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
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
  const compareDatasetId = useResearchStore((s) => s.compareDatasetId)
  const compareSelection = useResearchStore((s) => s.compareSelection)
  const setCompareSelection = useResearchStore((s) => s.setCompareSelection)
  const { data: metricDefs } = useMetricDefinitions()
  const [expandedKey, setExpandedKey] = useState(null)
  const [view, setView] = useState('grouped') // 'grouped' | 'matrix' -- matrix only shown for 2+ tickers

  const metricFormatByName = useMemo(() => {
    const map = {}
    for (const m of metricDefs || []) map[m.name] = m
    return map
  }, [metricDefs])

  if (!lastRunResults) {
    return (
      <div>
        <PageHeader title="Results" subtitle="Run a backtest to see ranked results here." />
        <Card>
          <EmptyState
            title="No results yet"
            body="Run backtests against a dataset to see strategies ranked by overall score."
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

  const { dataset_results: datasetResults } = lastRunResults
  const isMultiTicker = datasetResults.length > 1

  const toggleCompare = (datasetId, strategyName) => {
    const current = datasetId === compareDatasetId ? compareSelection : []
    setCompareSelection(
      datasetId,
      current.includes(strategyName) ? current.filter((n) => n !== strategyName) : [...current, strategyName]
    )
  }

  return (
    <div>
      <PageHeader
        title="Results"
        subtitle={
          isMultiTicker
            ? `${datasetResults.length} tickers × ${datasetResults[0].results.length} strategies.`
            : `${datasetResults[0]?.results.length ?? 0} strategies ranked by overall score. Click a row for full metrics.`
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

      {(!isMultiTicker || view === 'grouped') &&
        datasetResults.map((d) => (
          <div key={d.dataset_id} style={{ marginBottom: isMultiTicker ? 24 : 0 }}>
            {isMultiTicker && <div className="section-label">{d.dataset_name}</div>}
            <StrategyRankTable
              results={d.results}
              datasetId={d.dataset_id}
              compareDatasetId={compareDatasetId}
              compareSelection={compareSelection}
              toggleCompare={toggleCompare}
              metricDefs={metricDefs}
              metricFormatByName={metricFormatByName}
              expandedKey={expandedKey}
              setExpandedKey={setExpandedKey}
            />
          </div>
        ))}

      {isMultiTicker && view === 'matrix' && (
        <MatrixView datasetResults={datasetResults} />
      )}
    </div>
  )
}

function StrategyRankTable({
  results,
  datasetId,
  compareDatasetId,
  compareSelection,
  toggleCompare,
  metricDefs,
  metricFormatByName,
  expandedKey,
  setExpandedKey,
}) {
  return (
    <Card tight>
      <div className="data-table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: 36 }}></th>
              <th>Rank</th>
              <th>Strategy</th>
              {SUMMARY_METRIC_ORDER.map((name) => (
                <th key={name} className="align-right">
                  {metricFormatByName[name]?.display_name || name}
                </th>
              ))}
              <th>Overall Score</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r) => {
              const key = `${datasetId}:${r.strategy_name}`
              const checked = datasetId === compareDatasetId && compareSelection.includes(r.strategy_name)
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
                        onChange={() => toggleCompare(datasetId, r.strategy_name)}
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
                    <td>
                      <ScoreBar score={r.overall_score} />
                    </td>
                  </tr>
                  {expandedKey === key && (
                    <tr>
                      <td colSpan={SUMMARY_METRIC_ORDER.length + 4} style={{ padding: 0, background: 'var(--bg-base)' }}>
                        <DetailPanel metrics={r.metrics} metricDefs={metricDefs} trades={r.trades} />
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

function MatrixView({ datasetResults }) {
  // The same strategy_names were requested for every ticker in one run, so
  // the first ticker's own result order is a stable row order for all of them.
  const strategyOrder = datasetResults[0]?.results.map((r) => ({
    name: r.strategy_name,
    display_name: r.strategy_display_name,
  })) || []

  const scoreFor = (datasetId, strategyName) => {
    const dataset = datasetResults.find((d) => d.dataset_id === datasetId)
    return dataset?.results.find((r) => r.strategy_name === strategyName)?.overall_score ?? null
  }

  const bestScoreByStrategy = {}
  for (const s of strategyOrder) {
    const scores = datasetResults.map((d) => scoreFor(d.dataset_id, s.name)).filter((v) => v !== null)
    bestScoreByStrategy[s.name] = scores.length ? Math.max(...scores) : null
  }

  return (
    <Card tight>
      <div className="data-table-scroll">
        <table className="data-table compare-table">
          <thead>
            <tr>
              <th className="compare-sticky-col">Strategy</th>
              {datasetResults.map((d) => (
                <th key={d.dataset_id} className="align-right">
                  {d.dataset_name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {strategyOrder.map((s) => (
              <tr key={s.name}>
                <td className="compare-sticky-col" style={{ fontWeight: 600 }}>
                  {s.display_name}
                </td>
                {datasetResults.map((d) => {
                  const score = scoreFor(d.dataset_id, s.name)
                  const isBest = score !== null && score === bestScoreByStrategy[s.name]
                  return (
                    <td key={d.dataset_id} className={`align-right${isBest ? ' best-cell' : ''}`}>
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

function DetailPanel({ metrics, metricDefs, trades }) {
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
      <TradesTable trades={trades} />
    </div>
  )
}
