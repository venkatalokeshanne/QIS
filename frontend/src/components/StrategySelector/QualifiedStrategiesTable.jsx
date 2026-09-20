import { Fragment, useState } from 'react'
import { label, num, pct } from './shared'

export default function QualifiedStrategiesTable({ rows }) {
  const [open, setOpen] = useState(null)
  if (!rows.length) return null
  return (
    <div className="ss-table-wrap">
      <table className="ss-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Strategy</th>
            <th>Family</th>
            <th className="num">Trades</th>
            <th className="num">PF</th>
            <th className="num">OOS PF</th>
            <th className="num">Regime PF</th>
            <th className="num">Premarket PF</th>
            <th className="num">Walk-fwd</th>
            <th className="num">%/capital-day</th>
            <th className="num">Max DD</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <Fragment key={r.strategy_id}>
              <tr
                className="ss-row"
                tabIndex={0}
                onClick={() => setOpen(open === i ? null : i)}
                onKeyDown={(e) => e.key === 'Enter' && setOpen(open === i ? null : i)}
                aria-expanded={open === i}
              >
                <td className="ss-mono">{i + 1}</td>
                <td>{r.strategy}</td>
                <td>{label(r.family)}</td>
                <td className="num">{r.trade_count ?? '—'}</td>
                <td className="num">{num(r.profit_factor)}</td>
                <td className="num">{num(r.oos_pf)}</td>
                <td className="num" title={r.regime_level || r.regime_match || ''}>{num(r.regime_pf)}</td>
                <td className="num">{num(r.premarket_regime_pf)}</td>
                <td className="num">{pct(r.walk_forward_pass_rate, 0)}</td>
                <td className="num" title={r.mean_hold_days ? `typical hold ${r.mean_hold_days} days` : ''}>
                  {r.expectancy_per_capital_day == null ? '—' : `${(r.expectancy_per_capital_day * 100).toFixed(3)}%`}
                </td>
                <td className="num">{pct(r.max_drawdown)}</td>
              </tr>
              {open === i && (
                <tr className="ss-detail">
                  <td colSpan={11}>
                    <ul>
                      {(r.why || []).map((w, j) => (
                        <li key={j} className={w.startsWith('Warning:') ? 'ss-warn' : undefined}>{w}</li>
                      ))}
                    </ul>
                  </td>
                </tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  )
}
