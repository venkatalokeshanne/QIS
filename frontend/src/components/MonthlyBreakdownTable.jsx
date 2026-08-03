import MetricValue from './MetricValue'
import SortableTh from './SortableTh'
import { useSortableData } from '../hooks/useSortableData'
import './DataTable.css'

// Curated subset of the full metrics suite -- the same continuous
// backtest's results just sliced by month, so a compact row per month
// reads better than repeating every metric from the overall panel.
const COLUMNS = [
  { name: 'total_trades', label: 'Trades', format: 'count' },
  { name: 'win_rate', label: 'Win Rate', format: 'percent' },
  { name: 'profit_factor', label: 'Profit Factor', format: 'ratio' },
  { name: 'sharpe_ratio', label: 'Sharpe', format: 'ratio' },
  { name: 'max_drawdown', label: 'Max Drawdown', format: 'percent' },
  { name: 'net_profit', label: 'Net Profit', format: 'currency' },
]

function formatMonthLabel(key) {
  const [year, month] = key.split('-')
  const d = new Date(Number(year), Number(month) - 1, 1)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long' })
}

// monthlyMetrics: { "2026-04": { metric_name: value, ... }, ... } from
// the backtest response's monthly_metrics field -- same backtest as
// the overall result, just bucketed by the calendar month each trade
// closed in, with each month's own starting capital carried over from
// the running equity at the end of the prior month (real compounding,
// not a reset-to-zero re-run).
function getRowValue(row, key) {
  if (key === 'month') return row.month
  return row.metrics[key]
}

export default function MonthlyBreakdownTable({ monthlyMetrics }) {
  const rows = Object.keys(monthlyMetrics || {})
    .sort()
    .map((month) => ({ month, metrics: monthlyMetrics[month] }))
  const { sorted, sortKey, sortDir, toggleSort } = useSortableData(rows, getRowValue, 'month', 'asc')

  if (rows.length === 0) {
    return <div className="trades-empty">No monthly data (dataset may span less than one calendar month).</div>
  }

  return (
    <div className="data-table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            <SortableTh label="Month" sortKey="month" activeKey={sortKey} dir={sortDir} onSort={toggleSort} />
            {COLUMNS.map((col) => (
              <SortableTh
                key={col.name}
                label={col.label}
                sortKey={col.name}
                activeKey={sortKey}
                dir={sortDir}
                onSort={toggleSort}
                align="right"
              />
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr key={row.month}>
              <td>{formatMonthLabel(row.month)}</td>
              {COLUMNS.map((col) => (
                <td key={col.name} className="align-right">
                  <MetricValue value={row.metrics[col.name]} format={col.format} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
