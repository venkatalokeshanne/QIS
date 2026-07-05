import { View, Text, StyleSheet } from 'react-native'
import DataTable from './DataTable'
import { formatCompactDateTime } from '../utils/format'
import { colors, fonts, spacing } from '../styles/tokens'

// entry_price is per-unit, quantity is the position size -- the trade's
// cost basis is their product, so pnl / cost basis gives the % return
// regardless of direction (pnl is already signed correctly for shorts).
function pnlPct(trade) {
  const costBasis = trade.entry_price * trade.quantity
  if (!costBasis || trade.pnl === null || trade.pnl === undefined) return null
  return (trade.pnl / costBasis) * 100
}

function resultLabel(pnl) {
  if (pnl === null || pnl === undefined || pnl === 0) return 'Flat'
  return pnl > 0 ? 'Win' : 'Loss'
}

// e.g. "forced_session_close" -> "Forced Session Close" -- reads better
// and its column is sized to fit the longest real value (see below).
function formatExitReason(reason) {
  if (!reason) return '—'
  return reason.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

// Ported from frontend/src/components/TradesTable.jsx onto the generic
// DataTable horizontal-scroll primitive (genuinely matrix-shaped data,
// per the plan's dense-table split).
export default function TradesTable({ trades }) {
  if (!trades || trades.length === 0) {
    return <Text style={styles.empty}>No trades.</Text>
  }

  const columns = [
    { key: 'i', label: '#', width: 34, mono: true },
    { key: 'direction', label: 'Direction', width: 70 },
    { key: 'entry_time', label: 'Entry Time', width: 128, mono: true, render: (r) => formatCompactDateTime(r.entry_time) },
    { key: 'entry_price', label: 'Entry Price', width: 90, mono: true, render: (r) => r.entry_price?.toFixed(2) ?? '—' },
    { key: 'exit_time', label: 'Exit Time', width: 128, mono: true, render: (r) => formatCompactDateTime(r.exit_time) },
    { key: 'exit_price', label: 'Exit Price', width: 90, mono: true, render: (r) => r.exit_price?.toFixed(2) ?? '—' },
    {
      key: 'pnl',
      label: 'P&L',
      width: 150,
      mono: true,
      render: (r) => {
        if (r.pnl === null || r.pnl === undefined) return '—'
        const pct = pnlPct(r)
        const pctText = pct === null ? '' : ` (${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%)`
        return `${r.pnl.toFixed(2)}${pctText}`
      },
    },
    // Sized for the longest real exit_reason value from the backend
    // (execution.py): "forced_session_close" -> "Forced Session Close".
    { key: 'exit_reason', label: 'Exit Reason', width: 165, render: (r) => formatExitReason(r.exit_reason) },
  ]

  const rows = trades.map((t, i) => ({ ...t, i: i + 1, id: i }))

  const rowStyle = (row) => {
    const result = resultLabel(row.pnl)
    if (result === 'Win') return { backgroundColor: colors.positiveWash }
    if (result === 'Loss') return { backgroundColor: colors.negativeWash }
    return null
  }

  return (
    <View>
      <DataTable columns={columns} rows={rows} rowStyle={rowStyle} />
    </View>
  )
}

const styles = StyleSheet.create({
  empty: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textSecondary,
    paddingVertical: spacing[3],
  },
})
