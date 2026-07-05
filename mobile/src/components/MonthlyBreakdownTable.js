import { Text, StyleSheet } from 'react-native'
import DataTable from './DataTable'
import { formatMetricValue } from '../utils/format'
import { colors, fonts, spacing } from '../styles/tokens'

// Sharpe dropped for consistency with the rest of the app's metric
// grids (see utils/metricDisplay.js) -- excluded there too per user
// feedback.
const COLUMNS = [
  { name: 'total_trades', label: 'Trades', format: 'count' },
  { name: 'win_rate', label: 'Win Rate', format: 'percent' },
  { name: 'profit_factor', label: 'Profit Factor', format: 'ratio' },
  { name: 'max_drawdown', label: 'Max Drawdown', format: 'percent' },
  { name: 'net_profit', label: 'Net Profit', format: 'currency' },
]

function formatMonthLabel(key) {
  const [year, month] = key.split('-')
  const d = new Date(Number(year), Number(month) - 1, 1)
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long' })
}

// Ported from frontend/src/components/MonthlyBreakdownTable.jsx onto
// the generic DataTable horizontal-scroll primitive.
export default function MonthlyBreakdownTable({ monthlyMetrics }) {
  const months = Object.keys(monthlyMetrics || {}).sort()

  if (months.length === 0) {
    return <Text style={styles.empty}>No monthly data (dataset may span less than one calendar month).</Text>
  }

  const columns = [
    { key: 'month', label: 'Month', width: 130, render: (r) => formatMonthLabel(r.month) },
    ...COLUMNS.map((col) => ({
      key: col.name,
      label: col.label,
      width: 100,
      mono: true,
      render: (r) => formatMetricValue(r.metrics[col.name], col.format),
    })),
  ]

  const rows = months.map((month) => ({ id: month, month, metrics: monthlyMetrics[month] }))

  return <DataTable columns={columns} rows={rows} />
}

const styles = StyleSheet.create({
  empty: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textSecondary,
    paddingVertical: spacing[3],
  },
})
