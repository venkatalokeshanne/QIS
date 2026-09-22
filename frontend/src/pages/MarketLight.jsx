import { useState } from 'react'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import EmptyState from '../components/EmptyState'
import { useMarketLight } from '../api/hooks'
import './MarketLight.css'

const TIMEFRAMES = [
  { id: '1D', label: 'Daily' },
  { id: '1h', label: '1 hour' },
  { id: '15m', label: '15 min' },
]

const NAMES = { green: 'Green', yellow: 'Yellow', red: 'Red' }
const MEANING = {
  green: 'Good weather — press',
  yellow: 'Conflicting — be selective',
  red: 'Capital preservation',
}

// What each light changes in the Desk Protocol: size, which setups, how fast to take profit.
const PLAYBOOK = {
  green: [
    'Full size on setups scoring 8+',
    'Buy ORB breaks and breakouts — momentum entries allowed',
    'Hold a runner to the final target; add as the position works',
  ],
  yellow: [
    'Half size; only setups scoring 9–10',
    'Enter near support or invalidation — retests and pullbacks, not chases',
    'Take the first target quickly and demand 2:1 or better',
  ],
  red: [
    'Longs mostly off — cash is a position',
    'Breakouts fail more often; skip them',
    'If you short, flip the same rules: shorts below a falling 21 EMA',
  ],
}

const pct = (v, digits = 2) => (v == null ? '—' : `${v > 0 ? '+' : ''}${Number(v).toFixed(digits)}%`)
const barsWord = (tf, n) => {
  const unit = tf === '1D' ? 'day' : 'bar'
  return `${n} ${unit}${n === 1 ? '' : 's'}`
}
const shortTime = (iso, tf) => (tf === '1D' ? iso.slice(0, 10) : iso.slice(0, 16).replace('T', ' '))

function Signal({ light, size = 'lg' }) {
  return (
    <div className={`ml-signal ml-signal-${size}`} role="img" aria-label={`${NAMES[light]} light`}>
      {['red', 'yellow', 'green'].map((l) => (
        <span key={l} className={`ml-lamp ml-lamp-${l}${l === light ? ' is-on' : ''}`} />
      ))}
    </div>
  )
}

function Hero({ data }) {
  return (
    <Card className={`ml-hero ml-tone-${data.light}`}>
      <Signal light={data.light} />
      <div className="ml-hero-body">
        <div className="ml-eyebrow">Market environment · SPY · QQQ · IWM</div>
        <div className={`ml-hero-light ml-text-${data.light}`}>{NAMES[data.light]} light</div>
        <div className="ml-hero-meaning">{MEANING[data.light]}</div>
        <p className="ml-hero-reason">{data.reason}</p>
        <ul className="ml-playbook-list">
          {PLAYBOOK[data.light].map((line) => <li key={line}>{line}</li>)}
        </ul>
      </div>
    </Card>
  )
}

function IndexCard({ idx, timeframe }) {
  return (
    <Card className={`ml-index ml-tone-${idx.light}`}>
      <div className="ml-index-head">
        <Signal light={idx.light} size="sm" />
        <div>
          <div className="ml-index-symbol">{idx.symbol}</div>
          <div className={`ml-index-light ml-text-${idx.light}`}>
            {NAMES[idx.light]} · {barsWord(timeframe, idx.streak)}
          </div>
        </div>
        <div className="ml-index-close ml-mono">{idx.close.toFixed(2)}</div>
      </div>
      <dl className="ml-kv">
        <dt>9 EMA</dt><dd className="ml-mono">{idx.ema9.toFixed(2)}</dd>
        <dt>21 EMA</dt><dd className="ml-mono">{idx.ema21.toFixed(2)}</dd>
        <dt>From 21 EMA</dt><dd className="ml-mono">{pct(idx.distance_from_21_pct)}</dd>
        <dt>21 EMA slope</dt><dd className="ml-mono">{idx.slope_atr > 0 ? '+' : ''}{idx.slope_atr.toFixed(2)} ATR</dd>
        <dt>Structure</dt><dd className="ml-mono">{idx.structure}</dd>
      </dl>
      <ul className="ml-reasons">
        {idx.reasons.map((r) => <li key={r}>{r}</li>)}
      </ul>
    </Card>
  )
}

function Strip({ label, history, timeframe }) {
  return (
    <div className="ml-strip-row">
      <div className="ml-strip-label">{label}</div>
      <div className="ml-strip">
        {history.map((h) => (
          <span
            key={h.t}
            className={`ml-cell ml-cell-${h.light}`}
            title={`${shortTime(h.t, timeframe)} · ${NAMES[h.light]}`}
          />
        ))}
      </div>
    </div>
  )
}

function History({ data }) {
  const first = data.history[0]?.t
  const last = data.history[data.history.length - 1]?.t
  return (
    <Card>
      <div className="ml-section-title">Last {data.history.length} {data.timeframe === '1D' ? 'sessions' : 'bars'}</div>
      <div className="ml-strips">
        <Strip label="Market" history={data.history} timeframe={data.timeframe} />
        {data.indices.map((i) => (
          <Strip key={i.symbol} label={i.symbol} history={i.history} timeframe={data.timeframe} />
        ))}
      </div>
      {first && (
        <div className="ml-strip-axis ml-mono">
          <span>{shortTime(first, data.timeframe)}</span>
          <span>{shortTime(last, data.timeframe)}</span>
        </div>
      )}
    </Card>
  )
}

function Stats({ data }) {
  const unit = data.timeframe === '1D' ? 'day' : 'bar'
  return (
    <Card>
      <div className="ml-section-title">How each index behaved under each light</div>
      <p className="ml-note">
        Descriptive, not a forecast: what followed each light over the fetched history. The light
        sets how aggressive to be — it doesn't predict the next {unit}. Learn how <em>your</em> setups
        behave under each one.
      </p>
      <div className="ml-table-wrap">
        <table className="ml-table">
          <thead>
            <tr>
              <th>Index</th>
              <th>Light</th>
              <th className="num">Share of time</th>
              <th className="num">Next {unit} avg</th>
              <th className="num">Next {unit} up</th>
              <th className="num">Next 5 avg</th>
            </tr>
          </thead>
          <tbody>
            {data.indices.flatMap((i) =>
              ['green', 'yellow', 'red'].map((l, k) => {
                const s = i.stats[l]
                return (
                  <tr key={`${i.symbol}-${l}`} className={k === 0 ? 'ml-group-start' : ''}>
                    <td>{k === 0 ? i.symbol : ''}</td>
                    <td><span className={`ml-dot ml-dot-${l}`} />{NAMES[l]}</td>
                    <td className="num ml-mono">{s.share_pct.toFixed(1)}%</td>
                    <td className="num ml-mono">{pct(s.next_bar_avg_pct, 3)}</td>
                    <td className="num ml-mono">{s.next_bar_up_pct == null ? '—' : `${s.next_bar_up_pct.toFixed(1)}%`}</td>
                    <td className="num ml-mono">{pct(s.next_5_avg_pct, 3)}</td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

function Rules({ rules }) {
  return (
    <Card>
      <div className="ml-section-title">Rules</div>
      <div className="ml-rules">
        <div><span className="ml-dot ml-dot-green" /><strong>Green</strong> — close above a rising {rules.slow} EMA and {rules.fast} EMA above the {rules.slow}</div>
        <div><span className="ml-dot ml-dot-yellow" /><strong>Yellow</strong> — anything conflicting or flat</div>
        <div><span className="ml-dot ml-dot-red" /><strong>Red</strong> — close below a declining {rules.slow} EMA and {rules.fast} EMA below the {rules.slow}</div>
      </div>
      <p className="ml-note">
        “Rising” means the {rules.slow} EMA moved more than {rules.flat_atr} ATR over the last {rules.slope_bars} bars,
        so the same bar means the same thing on SPY and IWM. Market light: two or more indices agree with none
        opposing, otherwise yellow. A great stock can still work in a red market, and a bad one doesn't become
        an A+ trade because QQQ is green.
      </p>
    </Card>
  )
}

export default function MarketLight() {
  const [timeframe, setTimeframe] = useState('1D')
  const { data, isLoading, isError, error, isFetching } = useMarketLight(timeframe)

  const tfPicker = (
    <div className="ml-tf" role="tablist" aria-label="Timeframe">
      {TIMEFRAMES.map((t) => (
        <button
          key={t.id}
          id={`ml-tf-${t.id}`}
          role="tab"
          aria-selected={timeframe === t.id}
          className={`ml-tf-btn${timeframe === t.id ? ' is-active' : ''}`}
          onClick={() => setTimeframe(t.id)}
        >
          {t.label}
        </button>
      ))}
    </div>
  )

  return (
    <div className="ml-page">
      <PageHeader
        title="Market Light"
        subtitle="Green, yellow or red — how much aggression today deserves, from SPY, QQQ and IWM with a 9 and 21 EMA."
        actions={tfPicker}
      />
      {isLoading && <Card><p className="ml-note">Reading SPY, QQQ and IWM…</p></Card>}
      {isError && <EmptyState title="Couldn't load the market light" body={error.message} />}
      {data && (
        <div className={`ml-grid${isFetching ? ' is-refreshing' : ''}`}>
          <Hero data={data} />
          <div className="ml-indices">
            {data.indices.map((i) => <IndexCard key={i.symbol} idx={i} timeframe={data.timeframe} />)}
          </div>
          <History data={data} />
          <Stats data={data} />
          <Rules rules={data.rules} />
          <p className="ml-asof ml-mono">
            As of {shortTime(data.indices[0].as_of, data.timeframe)}
            {data.timeframe === '1D' && ' · the latest daily bar is provisional until the close'} · refreshes every 5 minutes
          </p>
        </div>
      )}
    </div>
  )
}
