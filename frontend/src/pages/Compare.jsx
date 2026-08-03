import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import MetricValue from '../components/MetricValue'
import { useMetricDefinitions } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import './Compare.css'

export default function Compare() {
  const navigate = useNavigate()
  const lastRunResults = useResearchStore((s) => s.lastRunResults)
  const compareSymbol = useResearchStore((s) => s.compareSymbol)
  const compareSelection = useResearchStore((s) => s.compareSelection)
  const { data: metricDefs } = useMetricDefinitions()

  const tickerResult = lastRunResults?.ticker_results.find((t) => t.symbol === compareSymbol)

  if (!tickerResult || compareSelection.length === 0) {
    return (
      <div>
        <PageHeader title="Compare Strategies" subtitle="Select strategies on the Results page to compare them side by side." />
        <Card>
          <EmptyState
            title="Nothing selected to compare"
            body="Go to Results and check the strategies you'd like to compare."
            action={
              <Button variant="primary" onClick={() => navigate('/results')}>
                Go to Results
              </Button>
            }
          />
        </Card>
      </div>
    )
  }

  const selected = tickerResult.results.filter((r) => compareSelection.includes(r.strategy_name))

  const bestForMetric = (metricName, higherIsBetter) => {
    const values = selected.map((r) => r.metrics[metricName]).filter((v) => v !== null && v !== undefined)
    if (values.length === 0) return null
    return higherIsBetter ? Math.max(...values) : Math.min(...values)
  }

  const bestScore = Math.max(...selected.map((s) => s.overall_score ?? -Infinity))

  return (
    <div>
      <PageHeader
        title="Compare Strategies"
        subtitle={`Comparing ${selected.length} strategies on ${tickerResult.symbol}. The best value in each row is highlighted.`}
      />

      <Card tight>
        <div className="data-table-scroll">
          <table className="data-table compare-table">
            <thead>
              <tr>
                <th className="compare-sticky-col">Metric</th>
                {selected.map((r) => (
                  <th key={r.strategy_name} className="align-right">
                    {r.strategy_display_name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="compare-sticky-col" style={{ fontWeight: 600 }}>
                  Overall Score
                </td>
                {selected.map((r) => {
                  const isBest = r.overall_score === bestScore && r.overall_score !== null
                  return (
                    <td key={r.strategy_name} className={`align-right${isBest ? ' best-cell' : ''}`}>
                      <span className="mono">{r.overall_score?.toFixed(1) ?? '—'}</span>
                    </td>
                  )
                })}
              </tr>

              {(metricDefs || []).map((def) => {
                const best = bestForMetric(def.name, def.higher_is_better)
                return (
                  <tr key={def.name}>
                    <td className="compare-sticky-col">{def.display_name}</td>
                    {selected.map((r) => {
                      const value = r.metrics[def.name]
                      const isBest = best !== null && value === best
                      return (
                        <td key={r.strategy_name} className={`align-right${isBest ? ' best-cell' : ''}`}>
                          <MetricValue value={value} format={def.format} />
                        </td>
                      )
                    })}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
