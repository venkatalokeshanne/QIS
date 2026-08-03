import MetricValue from './MetricValue'
import SortableTh from './SortableTh'
import { useSortableData } from '../hooks/useSortableData'
import { formatDateTime } from '../utils/format'
import './TradesTable.css'

function getTradeValue(t, key) {
  switch (key) {
    case 'index':
      return t.__index
    case 'direction':
      return t.direction
    case 'entry_time':
      return t.entry_time ? new Date(t.entry_time).getTime() : null
    case 'entry_price':
      return t.entry_price
    case 'exit_time':
      return t.exit_time ? new Date(t.exit_time).getTime() : null
    case 'exit_price':
      return t.exit_price
    case 'pnl':
      return t.pnl
    case 'return_pct':
      return pnlPct(t)
    case 'result':
      return resultLabel(t.pnl)
    case 'exit_reason':
      return t.exit_reason
    default:
      return null
  }
}

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

export default function TradesTable({ trades }) {
  const indexed = (trades || []).map((t, i) => ({ ...t, __index: i + 1 }))
  const { sorted, sortKey, sortDir, toggleSort } = useSortableData(indexed, getTradeValue, 'index', 'asc')

  if (!trades || trades.length === 0) {
    return <div className="trades-empty">No trades.</div>
  }

  const th = (label, key, align) => (
    <SortableTh label={label} sortKey={key} activeKey={sortKey} dir={sortDir} onSort={toggleSort} align={align} />
  )

  return (
    <div className="trades-table-wrap">
      <table className="data-table trades-table">
        <thead>
          <tr>
            {th('#', 'index')}
            {th('Direction', 'direction')}
            {th('Entry Time', 'entry_time')}
            {th('Entry Price', 'entry_price', 'right')}
            {th('Exit Time', 'exit_time')}
            {th('Exit Price', 'exit_price', 'right')}
            {th('P&L', 'pnl', 'right')}
            {th('Return %', 'return_pct', 'right')}
            {th('Result', 'result')}
            {th('Exit Reason', 'exit_reason')}
          </tr>
        </thead>
        <tbody>
          {sorted.map((t) => {
            const pct = pnlPct(t)
            const result = resultLabel(t.pnl)
            return (
              <tr key={t.__index}>
                <td>{t.__index}</td>
                <td className={`trade-direction trade-${t.direction}`}>{t.direction}</td>
                <td>{formatDateTime(t.entry_time)}</td>
                <td className="align-right"><MetricValue value={t.entry_price} format="currency" /></td>
                <td>{formatDateTime(t.exit_time)}</td>
                <td className="align-right"><MetricValue value={t.exit_price} format="currency" /></td>
                <td className="align-right"><MetricValue value={t.pnl} format="currency" /></td>
                <td className={`align-right trade-return trade-return-${result.toLowerCase()}`}>
                  {pct === null ? '—' : `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`}
                </td>
                <td>
                  <span className={`trade-result-badge trade-result-${result.toLowerCase()}`}>{result}</span>
                </td>
                <td className={`exit-reason exit-${t.exit_reason}`}>{t.exit_reason || '—'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
