import { Fragment, useState } from 'react'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import MetricValue from '../components/MetricValue'
import { useDailyLevels, useLevelsBacktest, useLevelsDayReports } from '../api/hooks'
import { formatDate, formatDateTime } from '../utils/format'
import './DailyLevels.css'

function formatOutcome(outcome) {
  return outcome.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

const POSITIVE_OUTCOMES = new Set(['held', 'contained'])
const NEGATIVE_OUTCOMES = new Set(['broken', 'exceeded_upside', 'exceeded_downside', 'exceeded_both'])

function OutcomeBadge({ outcome }) {
  const cls = POSITIVE_OUTCOMES.has(outcome) ? 'outcome-positive' : NEGATIVE_OUTCOMES.has(outcome) ? 'outcome-negative' : 'outcome-neutral'
  return <span className={`outcome-badge ${cls}`}>{formatOutcome(outcome)}</span>
}

function DirectionalBadge({ closedAbove }) {
  return <span className={`outcome-badge ${closedAbove ? 'outcome-accent' : 'outcome-neutral'}`}>{closedAbove ? 'Above' : 'Below'}</span>
}

function DetailLevelRow({ label, outcome }) {
  if (!outcome) {
    return (
      <div className="level-row">
        <span className="level-row-label">{label}</span>
        <span className="field-hint">no data</span>
      </div>
    )
  }
  return (
    <div className="level-row">
      <span className="level-row-label">{label}</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <MetricValue value={outcome.level} format="currency" />
        <OutcomeBadge outcome={outcome.outcome} />
      </div>
    </div>
  )
}

function DetailDirectionalRow({ label, outcome }) {
  if (!outcome) {
    return (
      <div className="level-row">
        <span className="level-row-label">{label}</span>
        <span className="field-hint">no data</span>
      </div>
    )
  }
  return (
    <div className="level-row">
      <span className="level-row-label">{label}</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <MetricValue value={outcome.level} format="currency" />
        <DirectionalBadge closedAbove={outcome.closed_above} />
      </div>
    </div>
  )
}

function DayDetail({ day }) {
  return (
    <div className="levels-grid" style={{ marginTop: 12, marginBottom: 16 }}>
      <Card>
        <div className="section-label">Session</div>
        <LevelRow label="Open" value={day.session_open} />
        <LevelRow label="High" value={day.session_high} />
        <LevelRow label="Low" value={day.session_low} />
        <LevelRow label="Close" value={day.session_close} highlight />
        {day.gap_pct !== null && (
          <div className={`level-row ${day.gap_pct >= 0 ? 'metric-positive' : 'metric-negative'}`}>
            <span className="level-row-label">Gap</span>
            <span>
              {day.gap_pct >= 0 ? '+' : ''}
              {day.gap_pct.toFixed(2)}%
            </span>
          </div>
        )}
      </Card>

      <Card>
        <div className="section-label">Prior Day / Pivot / VWAP</div>
        <DetailLevelRow label="Prior Day High" outcome={day.prior_day_high} />
        <DetailLevelRow label="Prior Day Low" outcome={day.prior_day_low} />
        <DetailDirectionalRow label="Classic Pivot" outcome={day.pivot_point} />
        <DetailDirectionalRow label="VWAP (EOD)" outcome={day.vwap} />
      </Card>

      <Card>
        <div className="section-label">Pivot Points (Classic)</div>
        <DetailLevelRow label="R3" outcome={day.pivot_r3} />
        <DetailLevelRow label="R2" outcome={day.pivot_r2} />
        <DetailLevelRow label="R1" outcome={day.pivot_r1} />
        <DetailLevelRow label="S1" outcome={day.pivot_s1} />
        <DetailLevelRow label="S2" outcome={day.pivot_s2} />
        <DetailLevelRow label="S3" outcome={day.pivot_s3} />
      </Card>

      <Card>
        <div className="section-label">Camarilla Pivots</div>
        <DetailLevelRow label="R4" outcome={day.camarilla_r4} />
        <DetailLevelRow label="R3" outcome={day.camarilla_r3} />
        <DetailLevelRow label="R2" outcome={day.camarilla_r2} />
        <DetailLevelRow label="R1" outcome={day.camarilla_r1} />
        <DetailLevelRow label="S1" outcome={day.camarilla_s1} />
        <DetailLevelRow label="S2" outcome={day.camarilla_s2} />
        <DetailLevelRow label="S3" outcome={day.camarilla_s3} />
        <DetailLevelRow label="S4" outcome={day.camarilla_s4} />
      </Card>

      <Card>
        <div className="section-label">DeMark Pivots</div>
        <DetailDirectionalRow label="Pivot" outcome={day.demark_pivot} />
        <DetailLevelRow label="Resistance" outcome={day.demark_resistance} />
        <DetailLevelRow label="Support" outcome={day.demark_support} />
      </Card>

      <Card>
        <div className="section-label">Average Daily Range</div>
        {day.adr ? (
          <>
            <LevelRow label="Expected High" value={day.adr.expected_high} />
            <LevelRow label="ADR" value={day.adr.adr} />
            <LevelRow label="Expected Low" value={day.adr.expected_low} />
            <div className="level-row">
              <span className="level-row-label">Outcome</span>
              <OutcomeBadge outcome={day.adr.outcome} />
            </div>
          </>
        ) : (
          <div className="field-hint">Not enough prior sessions yet.</div>
        )}
      </Card>

      <Card>
        <div className="section-label">Opening Range (15 min)</div>
        {day.opening_range ? (
          <>
            <LevelRow label="High" value={day.opening_range.high} />
            <LevelRow label="Low" value={day.opening_range.low} />
            <div className="level-row">
              <span className="level-row-label">Outcome</span>
              <OutcomeBadge outcome={day.opening_range.outcome} />
            </div>
          </>
        ) : (
          <div className="field-hint">No data.</div>
        )}
      </Card>
    </div>
  )
}

function DayByDaySection({ symbol }) {
  const [dateInput, setDateInput] = useState('')
  const [selectedDates, setSelectedDates] = useState([])
  const [expandedDate, setExpandedDate] = useState(null)
  const dayReportsMutation = useLevelsDayReports()

  const addDate = () => {
    if (!dateInput) return
    setSelectedDates((prev) => (prev.includes(dateInput) ? prev : [...prev, dateInput].sort()))
    setDateInput('')
  }

  const removeDate = (date) => {
    setSelectedDates((prev) => prev.filter((d) => d !== date))
  }

  const handleRun = () => {
    if (selectedDates.length === 0) return
    dayReportsMutation.mutate({ symbol, dates: selectedDates })
    setExpandedDate(null)
  }

  const reports = dayReportsMutation.data?.reports || []
  const datesNotFound = dayReportsMutation.data?.dates_not_found || []

  return (
    <Card style={{ marginTop: 16 }}>
      <div className="section-label">Day-by-Day</div>
      <p className="field-hint" style={{ marginBottom: 12 }}>
        Pick any specific date(s) and fetch fresh data to see exactly what happened against every level that day —
        not just the aggregate rate.
      </p>

      <div className="levels-search-row">
        <input
          type="date"
          className="field-input"
          value={dateInput}
          onChange={(e) => setDateInput(e.target.value)}
        />
        <Button variant="secondary" onClick={addDate} disabled={!dateInput}>
          Add Date
        </Button>
      </div>

      {selectedDates.length > 0 && (
        <div className="date-chip-row">
          {selectedDates.map((date) => (
            <span key={date} className="date-chip">
              {formatDate(date)}
              <button type="button" onClick={() => removeDate(date)} aria-label={`Remove ${date}`}>
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginTop: 12 }}>
        <Button
          variant="primary"
          onClick={handleRun}
          disabled={selectedDates.length === 0 || dayReportsMutation.isPending}
        >
          {dayReportsMutation.isPending ? 'Fetching…' : `Get Reports (${selectedDates.length})`}
        </Button>
        {selectedDates.length > 0 && (
          <Button variant="ghost" size="sm" onClick={() => setSelectedDates([])}>
            Clear
          </Button>
        )}
      </div>

      {dayReportsMutation.isError && (
        <div className="error-banner" style={{ marginTop: 16 }}>
          {dayReportsMutation.error.message}
        </div>
      )}

      {datesNotFound.length > 0 && (
        <div className="field-hint" style={{ marginTop: 12 }}>
          No data for: {datesNotFound.map((d) => formatDate(d)).join(', ')} — outside the freshest fetched window or
          not a trading day.
        </div>
      )}

      {reports.length > 0 && (
        <div className="data-table-scroll" style={{ marginTop: 16 }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th className="align-right">Open</th>
                <th className="align-right">Close</th>
                <th className="align-right">Gap</th>
                <th className="align-right">Touched</th>
                <th className="align-right">Held</th>
                <th className="align-right">Broken</th>
                <th>ADR</th>
                <th>Opening Range</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((day) => (
                <Fragment key={day.date}>
                  <tr
                    className="clickable"
                    onClick={() => setExpandedDate(expandedDate === day.date ? null : day.date)}
                  >
                    <td>{formatDate(day.date)}</td>
                    <td className="align-right">
                      <MetricValue value={day.session_open} format="currency" />
                    </td>
                    <td className="align-right">
                      <MetricValue value={day.session_close} format="currency" />
                    </td>
                    <td className="align-right">{day.gap_pct === null ? '—' : `${day.gap_pct.toFixed(2)}%`}</td>
                    <td className="align-right">{day.levels_touched_count}</td>
                    <td className="align-right">{day.levels_held_count}</td>
                    <td className="align-right">{day.levels_broken_count}</td>
                    <td>{day.adr ? <OutcomeBadge outcome={day.adr.outcome} /> : '—'}</td>
                    <td>{day.opening_range ? <OutcomeBadge outcome={day.opening_range.outcome} /> : '—'}</td>
                  </tr>
                  {expandedDate === day.date && (
                    <tr>
                      <td colSpan={9} style={{ padding: 0 }}>
                        <DayDetail day={day} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}

function LevelRow({ label, value, highlight, format = 'currency' }) {
  return (
    <div className={`level-row${highlight ? ' level-row-highlight' : ''}`}>
      <span className="level-row-label">{label}</span>
      <MetricValue value={value} format={format} />
    </div>
  )
}

function pct(value) {
  return value === null || value === undefined ? '—' : `${value.toFixed(1)}%`
}

function HitRateTableRow({ label, stats }) {
  return (
    <tr>
      <td>{label}</td>
      <td className="align-right">{pct(stats.touched_pct)}</td>
      <td className="align-right">{pct(stats.held_pct)}</td>
      <td className="align-right">{pct(stats.broken_pct)}</td>
      <td className="align-right">{stats.sample_days}</td>
    </tr>
  )
}

function HitRateTable({ title, rows }) {
  return (
    <Card tight style={{ marginBottom: 16 }}>
      <div className="section-label" style={{ padding: '16px 16px 0' }}>
        {title}
      </div>
      <div className="field-hint" style={{ padding: '4px 16px 12px' }}>
        Touched = day's range reached the level. Held/Broken are % OF DAYS TOUCHED — held means price rejected off
        it, broken means the close ended up past it.
      </div>
      <div className="data-table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>Level</th>
              <th className="align-right">Touched</th>
              <th className="align-right">Held</th>
              <th className="align-right">Broken</th>
              <th className="align-right">Days</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([label, stats]) => (
              <HitRateTableRow key={label} label={label} stats={stats} />
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

function LiveLevelsTab() {
  const [symbolInput, setSymbolInput] = useState('')
  const levelsMutation = useDailyLevels()
  const levels = levelsMutation.data

  const handleSubmit = (e) => {
    e.preventDefault()
    const symbol = symbolInput.trim().toUpperCase()
    if (!symbol) return
    levelsMutation.mutate(symbol)
  }

  const srBelow = levels ? levels.auto_support_resistance.filter((v) => v < levels.current_price).reverse() : []
  const srAbove = levels ? levels.auto_support_resistance.filter((v) => v >= levels.current_price) : []

  return (
    <>
      <Card>
        <form className="levels-search-row" onSubmit={handleSubmit}>
          <input
            className="field-input mono"
            placeholder="Symbol (e.g. AAPL)"
            value={symbolInput}
            onChange={(e) => setSymbolInput(e.target.value)}
            autoFocus
          />
          <Button type="submit" variant="primary" disabled={levelsMutation.isPending || !symbolInput.trim()}>
            {levelsMutation.isPending ? 'Loading…' : 'Get Levels'}
          </Button>
        </form>

        {levelsMutation.isError && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            {levelsMutation.error.message}
          </div>
        )}
      </Card>

      {levels && (
        <>
          <Card style={{ marginTop: 16 }}>
            <div className="levels-header-row">
              <div>
                <div className="levels-symbol">{levels.symbol}</div>
                <div className="field-hint">Data as of {formatDateTime(levels.as_of)}</div>
              </div>
              <div className="levels-price-block">
                <div className="levels-current-price mono">
                  <MetricValue value={levels.current_price} format="currency" />
                </div>
                <div className={`levels-gap ${levels.gap_pct >= 0 ? 'metric-positive' : 'metric-negative'}`}>
                  Gap {levels.gap_pct >= 0 ? '+' : ''}
                  {levels.gap_pct.toFixed(2)}% vs prior close
                </div>
              </div>
            </div>
          </Card>

          <div className="levels-grid">
            <Card>
              <div className="section-label">Prior Session</div>
              <LevelRow label="High" value={levels.prior_high} />
              <LevelRow label="Close" value={levels.prior_close} />
              <LevelRow label="Low" value={levels.prior_low} />
            </Card>

            <Card>
              <div className="section-label">Today</div>
              <LevelRow label="Open" value={levels.session_open} />
              <LevelRow label="VWAP" value={levels.vwap} highlight />
              <LevelRow label="Opening Range High" value={levels.opening_range_high} />
              <LevelRow label="Opening Range Low" value={levels.opening_range_low} />
            </Card>

            <Card>
              <div className="section-label">Average Daily Range (14)</div>
              <LevelRow label="Expected High" value={levels.adr_expected_high} />
              <LevelRow label="ADR" value={levels.adr} />
              <LevelRow label="Expected Low" value={levels.adr_expected_low} />
            </Card>

            <Card>
              <div className="section-label">Pivot Points (Classic)</div>
              <LevelRow label="R3" value={levels.pivot_points.r3} />
              <LevelRow label="R2" value={levels.pivot_points.r2} />
              <LevelRow label="R1" value={levels.pivot_points.r1} />
              <LevelRow label="Pivot" value={levels.pivot_points.pivot} highlight />
              <LevelRow label="S1" value={levels.pivot_points.s1} />
              <LevelRow label="S2" value={levels.pivot_points.s2} />
              <LevelRow label="S3" value={levels.pivot_points.s3} />
            </Card>

            <Card>
              <div className="section-label">Camarilla Pivots</div>
              <LevelRow label="R4" value={levels.camarilla_pivots.r4} />
              <LevelRow label="R3" value={levels.camarilla_pivots.r3} />
              <LevelRow label="R2" value={levels.camarilla_pivots.r2} />
              <LevelRow label="R1" value={levels.camarilla_pivots.r1} />
              <LevelRow label="S1" value={levels.camarilla_pivots.s1} />
              <LevelRow label="S2" value={levels.camarilla_pivots.s2} />
              <LevelRow label="S3" value={levels.camarilla_pivots.s3} />
              <LevelRow label="S4" value={levels.camarilla_pivots.s4} />
            </Card>

            <Card>
              <div className="section-label">DeMark Pivots</div>
              <LevelRow label="Resistance" value={levels.demark_pivots.resistance} />
              <LevelRow label="Pivot" value={levels.demark_pivots.pivot} highlight />
              <LevelRow label="Support" value={levels.demark_pivots.support} />
            </Card>

            <Card>
              <div className="section-label">Auto Support / Resistance</div>
              {srAbove.length === 0 && srBelow.length === 0 && (
                <div className="field-hint">Not enough swing history yet.</div>
              )}
              {srAbove.map((v, i) => (
                <LevelRow key={`above-${i}`} label="Resistance" value={v} />
              ))}
              {srBelow.map((v, i) => (
                <LevelRow key={`below-${i}`} label="Support" value={v} />
              ))}
            </Card>

            <Card>
              <div className="section-label">Fibonacci Retracement (50-bar swing)</div>
              <LevelRow label="23.6%" value={levels.fibonacci_retracement['236']} />
              <LevelRow label="38.2%" value={levels.fibonacci_retracement['382']} />
              <LevelRow label="50%" value={levels.fibonacci_retracement['50']} />
              <LevelRow label="61.8%" value={levels.fibonacci_retracement['618']} />
              <LevelRow label="78.6%" value={levels.fibonacci_retracement['786']} />
            </Card>
          </div>
        </>
      )}
    </>
  )
}

function BacktestLevelsTab() {
  const [symbolInput, setSymbolInput] = useState('')
  const symbol = symbolInput.trim().toUpperCase()
  const backtestMutation = useLevelsBacktest()
  const report = backtestMutation.data

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!symbol) return
    backtestMutation.mutate(symbol)
  }

  return (
    <>
      <Card>
        <form className="levels-search-row" onSubmit={handleSubmit}>
          <input
            className="field-input mono"
            placeholder="Symbol (e.g. AAPL)"
            value={symbolInput}
            onChange={(e) => setSymbolInput(e.target.value)}
            autoFocus
          />
          <Button type="submit" variant="primary" disabled={!symbol || backtestMutation.isPending}>
            {backtestMutation.isPending ? 'Running…' : 'Run Backtest'}
          </Button>
        </form>
        <p className="field-hint" style={{ marginTop: 12 }}>
          Fetches the freshest available bars for this symbol live (same path as the Live tab). Every level is
          computed from data known strictly BEFORE the session it applies to (prior-session pivots, trailing ADR) —
          so there's no lookahead. This measures how often price actually respected or broke each level across every
          session fetched.
        </p>
        {backtestMutation.isError && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            {backtestMutation.error.message}
          </div>
        )}
      </Card>

      {report && (
        <>
          <Card style={{ marginTop: 16 }}>
            <div className="levels-header-row">
              <div>
                <div className="levels-symbol">{report.symbol}</div>
                <div className="field-hint">{report.total_sessions} sessions analyzed</div>
              </div>
              <div className="levels-price-block">
                <div className="levels-current-price mono">{pct(report.overall_success_rate_pct)}</div>
                <div className="field-hint">
                  Overall Success Rate ({report.overall_levels_held}/{report.overall_levels_touched} touches held)
                </div>
              </div>
            </div>
          </Card>

          <div style={{ marginTop: 16 }}>
            <HitRateTable
              title="Prior-Day High/Low"
              rows={[
                ['Prior Day High', report.prior_day_high],
                ['Prior Day Low', report.prior_day_low],
              ]}
            />

            <HitRateTable
              title="Pivot Points (Classic)"
              rows={[
                ['R3', report.pivot_r3],
                ['R2', report.pivot_r2],
                ['R1', report.pivot_r1],
                ['S1', report.pivot_s1],
                ['S2', report.pivot_s2],
                ['S3', report.pivot_s3],
              ]}
            />

            <HitRateTable
              title="Camarilla Pivots"
              rows={[
                ['R4', report.camarilla_r4],
                ['R3', report.camarilla_r3],
                ['R2', report.camarilla_r2],
                ['R1', report.camarilla_r1],
                ['S1', report.camarilla_s1],
                ['S2', report.camarilla_s2],
                ['S3', report.camarilla_s3],
                ['S4', report.camarilla_s4],
              ]}
            />

            <HitRateTable
              title="DeMark Pivots"
              rows={[
                ['Resistance', report.demark_resistance],
                ['Support', report.demark_support],
              ]}
            />

            <div className="levels-grid">
              <Card>
                <div className="section-label">Directional Bias</div>
                <div className="field-hint" style={{ marginBottom: 8 }}>
                  % of sessions that closed above this reference level.
                </div>
                <LevelRow label="Classic Pivot" value={report.pivot_point.closed_above_pct} format="percent" />
                <LevelRow label="DeMark Pivot" value={report.demark_pivot.closed_above_pct} format="percent" />
                <LevelRow label="VWAP (end of day)" value={report.vwap.closed_above_pct} format="percent" />
              </Card>

              <Card>
                <div className="section-label">Average Daily Range</div>
                <div className="field-hint" style={{ marginBottom: 8 }}>
                  {report.adr.sample_days} sessions with an established ADR.
                </div>
                <LevelRow label="Contained within ADR" value={report.adr.contained_pct} format="percent" />
                <LevelRow label="Exceeded upside" value={report.adr.exceeded_upside_pct} format="percent" />
                <LevelRow label="Exceeded downside" value={report.adr.exceeded_downside_pct} format="percent" />
              </Card>

              <Card>
                <div className="section-label">Opening Range (15 min)</div>
                <div className="field-hint" style={{ marginBottom: 8 }}>
                  {report.opening_range.sample_days} sessions.
                </div>
                <LevelRow
                  label="Closed above range"
                  value={report.opening_range.closed_above_range_pct}
                  format="percent"
                />
                <LevelRow
                  label="Closed below range"
                  value={report.opening_range.closed_below_range_pct}
                  format="percent"
                />
                <LevelRow
                  label="Stayed inside all day"
                  value={report.opening_range.stayed_inside_range_pct}
                  format="percent"
                />
              </Card>
            </div>
          </div>
        </>
      )}

      {symbol && <DayByDaySection symbol={symbol} />}
    </>
  )
}

export default function DailyLevels() {
  const [tab, setTab] = useState('live')

  return (
    <div>
      <PageHeader
        title="Daily Levels"
        subtitle="Select a stock to get its key levels for today, or backtest how reliable those levels have actually been historically."
      />

      <div className="tab-bar">
        <button className={`tab-item${tab === 'live' ? ' active' : ''}`} onClick={() => setTab('live')}>
          Live
        </button>
        <button className={`tab-item${tab === 'backtest' ? ' active' : ''}`} onClick={() => setTab('backtest')}>
          Backtest
        </button>
      </div>

      {tab === 'live' ? <LiveLevelsTab /> : <BacktestLevelsTab />}
    </div>
  )
}
