import { useState } from 'react'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import { useDayReplay } from '../api/hooks'
import { Pill, label } from '../components/StrategySelector/shared'
import '../components/StrategySelector/StrategySelector.css'

const TIMEFRAMES = ['5m', '15m', '30m', '65m', '1h', '2h', '1D', '1W']
const DEFAULT_TF = ['15m', '30m', '65m', '1D']

const pct = (v) => (v == null ? '—' : `${v > 0 ? '+' : ''}${Number(v).toFixed(2)}%`)
const tone = (v) => (v == null ? '' : v > 0 ? 'pnl-pos' : v < 0 ? 'pnl-neg' : '')

function Outcome({ title, data, accent }) {
  if (!data) return null
  return (
    <div className={`ss-outcome${accent ? ' ss-outcome-accent' : ''}`}>
      <div className="ss-title">{title}</div>
      <div className={`ss-outcome-total ${tone(data.total_return_pct)}`}>{pct(data.total_return_pct)}</div>
      <div className="ss-meta">
        {data.trades} trade{data.trades === 1 ? '' : 's'} · {data.winners}W / {data.losers}L
        {data.return_per_capital_day_pct != null && ` · ${pct(data.return_per_capital_day_pct)} per capital-day`}
      </div>
      {data.best && (
        <div className="ss-meta">
          best {data.best.strategy} {pct(data.best.return_pct)} · worst {data.worst.strategy} {pct(data.worst.return_pct)}
        </div>
      )}
    </div>
  )
}

function TradesTable({ trades }) {
  if (!trades.length) return <p className="ss-meta">No strategy entered a trade on this day.</p>
  return (
    <div className="ss-table-wrap">
      <table className="ss-table">
        <thead>
          <tr>
            <th>Picked</th>
            <th>Strategy</th>
            <th>Direction</th>
            <th>Entry</th>
            <th>Exit</th>
            <th className="num">Entry px</th>
            <th className="num">Exit px</th>
            <th className="num">Hold</th>
            <th className="num">Return</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((t, i) => (
            <tr key={i} className={t.picked ? 'ss-row-picked' : 'ss-row-muted'}>
              <td>{t.picked ? <span className="ss-pill ss-pill-accent">#{t.rank}</span> : '—'}</td>
              <td>{t.strategy}</td>
              <td>{t.direction}</td>
              <td className="ss-mono">{t.entry.slice(11)}</td>
              <td className="ss-mono" title={t.exit}>
                {t.closed_same_day ? t.exit.slice(11) : t.exit}
              </td>
              <td className="num">{t.entry_price}</td>
              <td className="num">{t.exit_price}</td>
              <td className="num">{t.hold_hours < 24 ? `${t.hold_hours}h` : `${(t.hold_hours / 24).toFixed(1)}d`}</td>
              <td className={`num ${tone(t.return_pct)}`}>{pct(t.return_pct)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function DayReplay() {
  const [ticker, setTicker] = useState('AAPL')
  const [date, setDate] = useState('2026-09-14')
  const [tfs, setTfs] = useState(DEFAULT_TF)
  const replay = useDayReplay()
  const r = replay.data
  const err = replay.error && (replay.error.response?.data?.detail || replay.error.message)

  const toggle = (tf) => setTfs((cur) => (cur.includes(tf) ? cur.filter((x) => x !== tf) : [...cur, tf]))
  const run = (e) => {
    e.preventDefault()
    if (ticker.trim() && tfs.length) replay.mutate({ ticker: ticker.trim().toUpperCase(), date, timeframes: tfs.join(',') })
  }

  return (
    <div className="ss-root">
      <PageHeader
        title="Day Replay"
        subtitle="Pick a ticker and a past date. The engine runs as it would have that morning at 09:25 — only what was known then — and the day plays out against its picks."
      />

      <Card>
        <form className="ss-form" onSubmit={run}>
          <div className="field-group">
            <label className="field-label" htmlFor="dr-ticker">Ticker</label>
            <input id="dr-ticker" className="field-input ss-ticker" value={ticker} onChange={(e) => setTicker(e.target.value)} />
          </div>
          <div className="field-group">
            <label className="field-label" htmlFor="dr-date">Date</label>
            <input id="dr-date" type="date" className="field-input" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
          <div className="field-group">
            <span className="field-label">Timeframes</span>
            <div className="ss-chips">
              {TIMEFRAMES.map((tf) => (
                <button
                  type="button"
                  key={tf}
                  onClick={() => toggle(tf)}
                  className={`ss-pill ss-tf-chip${tfs.includes(tf) ? ' ss-pill-accent' : ' ss-pill-dim'}`}
                  aria-pressed={tfs.includes(tf)}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>
          <Button variant="primary" type="submit" disabled={replay.isPending || !tfs.length}>
            {replay.isPending ? 'Replaying…' : 'Replay this day'}
          </Button>
        </form>
      </Card>

      {err && <div className="error-banner">{String(err)}</div>}

      {!r && !replay.isPending && !err && (
        <EmptyState
          title="Choose a day to replay"
          body="Evaluated tickers: AAPL, TSLA, SPY, QQQ, INFQ. Data covers Oct 2024 to Sep 2026."
        />
      )}

      {r && r.status === 'DATA_INSUFFICIENT' && <div className="error-banner">{r.note}</div>}

      {r && r.status === 'OK' && (
        <>
          <Card className="ss-panel">
            <div className="ss-panel-head">
              <h3 className="ss-title">
                {r.ticker} · {r.date} · decided at {r.decision_time} ET
              </h3>
              <span className="ss-meta">statistics refreshed {r.refresh}</span>
            </div>
            <div className="ss-chips">
              <span className="ss-meta">Market</span> <Pill value={r.market_regime} />
              <span className="ss-meta">Ticker</span> <Pill value={r.ticker_regime} />
              <span className="ss-meta">Premarket</span> <Pill value={r.premarket_regime} />
            </div>
            <div className="ss-chips">
              <span className="ss-meta">Families</span>
              {(r.eligible_families || []).map((f) => (
                <span key={f} className="ss-pill ss-pill-accent">{label(f)}</span>
              ))}
              {(r.lower_priority_families || []).map((f) => (
                <span key={f} className="ss-pill ss-pill-dim">{label(f)}</span>
              ))}
            </div>
            <div className="ss-outcomes">
              <Outcome title="Engine picks" data={r.summary.engine} accent />
              <Outcome title="Every strategy (no selection)" data={r.summary.all_strategies} />
            </div>
            <p className="ss-meta">
              {r.summary.strategies_on_watchlist} strategies qualified that morning across the selected timeframes.
              Returns are after costs, one unit of capital per trade.
            </p>
          </Card>

          {r.timeframes.map((tf) => (
            <Card key={tf.timeframe} className="ss-panel">
              <div className="ss-panel-head">
                <h3 className="ss-title">{tf.timeframe}</h3>
                <span className="ss-meta">
                  {tf.picked.length ? `picked ${tf.picked.filter((p) => p.traded).length}/${tf.picked.length} traded` : 'nothing qualified'}
                </span>
              </div>
              <div className="ss-chips">
                {tf.picked.map((p) => (
                  <span key={p.strategy_id} className={`ss-pill ${p.traded ? 'ss-pill-accent' : 'ss-pill-dim'}`}>
                    #{p.rank} {p.strategy}
                    {!p.traded && ' (no signal)'}
                  </span>
                ))}
                {!tf.picked.length && <span className="ss-meta">the engine stood aside on this timeframe</span>}
              </div>
              <TradesTable trades={tf.trades} />
              {tf.rejected.length > 0 && (
                <details className="ss-reasons">
                  <summary>Why the others were not picked ({tf.rejected.length})</summary>
                  <ul>
                    {tf.rejected.map((x, i) => (
                      <li key={i}>
                        <span className="ss-strat">{x.strategy}</span> — {x.reason}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </Card>
          ))}
        </>
      )}
    </div>
  )
}
