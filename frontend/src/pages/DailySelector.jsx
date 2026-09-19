import { useState } from 'react'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import MetricValue from '../components/MetricValue'
import TradesTable from '../components/TradesTable'
import { useStrategies, useCalibrateTickers, useRunDailySelection, useRunSelectionBacktest } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { formatDate, formatDateTime } from '../utils/format'

// Backend regime bucket keys look like
// "ticker=trending/high_vol|market=ranging/low_vol", or the literal
// string "unclassified" for a backtest segment whose day couldn't be
// classified -- parse the former into readable badges, fall back to
// showing the raw string for anything that doesn't match (including
// "unclassified" and null).
function formatRegimeBucket(bucket) {
  if (!bucket) return null
  const match = bucket.match(/^ticker=([a-z_]+)\/([a-z_]+)\|market=([a-z_]+)\/([a-z_]+)$/)
  if (!match) return null
  const [, tTrend, tVol, mTrend, mVol] = match
  const label = (s) => s.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())
  return { ticker: `${label(tTrend)}, ${label(tVol)}`, market: `${label(mTrend)}, ${label(mVol)}` }
}

function RegimeBadges({ bucket }) {
  const parsed = formatRegimeBucket(bucket)
  if (!parsed) return <span className="badge">{bucket || '—'}</span>
  return (
    <span style={{ display: 'inline-flex', gap: 6, flexWrap: 'wrap' }}>
      <span className="badge">Ticker: {parsed.ticker}</span>
      <span className="badge">Market: {parsed.market}</span>
    </span>
  )
}

export default function DailySelector() {
  const { data: strategies } = useStrategies()
  const displayName = (name) => (strategies || []).find((s) => s.name === name)?.display_name || name

  const selectedSymbols = useResearchStore((s) => s.selectedSymbols)
  const selectedInterval = useResearchStore((s) => s.selectedInterval)
  // Backtest's test window reuses the SAME header date range every
  // other action page (Run Backtests, Results' Previous/Next) already
  // reads from -- one date range for the whole session, not asked for
  // again per page. The backend clamps the start up to the playbook's
  // own calibration cutoff if this predates it (see the field-hint
  // below), so an out-of-date header selection can't silently break
  // the out-of-sample guarantee.
  const backtestStartDate = useResearchStore((s) => s.backtestStartDate)
  const backtestEndDate = useResearchStore((s) => s.backtestEndDate)
  const lastCalibrationResults = useResearchStore((s) => s.lastCalibrationResults)
  const setLastCalibrationResults = useResearchStore((s) => s.setLastCalibrationResults)
  const lastDailySelectionResults = useResearchStore((s) => s.lastDailySelectionResults)
  const setLastDailySelectionResults = useResearchStore((s) => s.setLastDailySelectionResults)
  const lastSelectionBacktestResults = useResearchStore((s) => s.lastSelectionBacktestResults)
  const setLastSelectionBacktestResults = useResearchStore((s) => s.setLastSelectionBacktestResults)

  const [mode, setMode] = useState('calibrate') // 'calibrate' | 'today' | 'backtest'
  const [startDate, setStartDate] = useState('')
  const [cutoffDate, setCutoffDate] = useState('2026-04-30')
  const [backtestSymbol, setBacktestSymbol] = useState('')

  const calibrateMutation = useCalibrateTickers()
  const runMutation = useRunDailySelection()
  const backtestMutation = useRunSelectionBacktest()
  const activeMutation = mode === 'calibrate' ? calibrateMutation : mode === 'today' ? runMutation : backtestMutation

  const effectiveBacktestSymbol = backtestSymbol || selectedSymbols[0] || ''

  const handleCalibrate = () => {
    if (selectedSymbols.length === 0 || !startDate || !cutoffDate) return
    calibrateMutation.mutate(
      { symbols: selectedSymbols, interval: selectedInterval, start_date: startDate, cutoff_date: cutoffDate },
      { onSuccess: (data) => setLastCalibrationResults(data) }
    )
  }

  const handleRunToday = () => {
    if (selectedSymbols.length === 0) return
    runMutation.mutate(
      { symbols: selectedSymbols, interval: selectedInterval },
      { onSuccess: (data) => setLastDailySelectionResults(data) }
    )
  }

  const handleRunBacktest = () => {
    if (!effectiveBacktestSymbol || !backtestStartDate || !backtestEndDate) return
    backtestMutation.mutate(
      {
        symbol: effectiveBacktestSymbol,
        interval: selectedInterval,
        start_date: backtestStartDate,
        test_end_date: backtestEndDate,
      },
      { onSuccess: (data) => setLastSelectionBacktestResults(data) }
    )
  }

  const profiles = lastCalibrationResults?.profiles || []
  const failedCalibrationSymbols = lastCalibrationResults?.failed_symbols || []
  const selections = lastDailySelectionResults?.selections || []
  const failedSelectionSymbols = lastDailySelectionResults?.failed_symbols || []

  return (
    <div>
      <PageHeader
        title="Daily Strategy Selector"
        subtitle="Regime-aware strategy + parameter switching -- build a playbook per ticker, see today's pick, or test whether switching actually beats a static baseline."
        actions={
          <div className="chip-row">
            <button type="button" className={`chip${mode === 'calibrate' ? ' active' : ''}`} onClick={() => setMode('calibrate')}>
              Calibrate
            </button>
            <button type="button" className={`chip${mode === 'today' ? ' active' : ''}`} onClick={() => setMode('today')}>
              Today's Picks
            </button>
            <button type="button" className={`chip${mode === 'backtest' ? ' active' : ''}`} onClick={() => setMode('backtest')}>
              Backtest
            </button>
          </div>
        }
      />

      <Card>
        {mode === 'calibrate' && (
          <>
            <div className="section-label">
              Build the Playbook
              <span className="section-label-hint">{selectedSymbols.length} ticker{selectedSymbols.length === 1 ? '' : 's'} selected</span>
            </div>
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginTop: 16 }}>
              <div className="field-group" style={{ maxWidth: 220 }}>
                <label className="field-label">Start date</label>
                <input
                  type="text"
                  placeholder="YYYY-MM-DD"
                  className="field-input"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="field-group" style={{ maxWidth: 220 }}>
                <label className="field-label">Cutoff date</label>
                <input
                  type="text"
                  placeholder="YYYY-MM-DD"
                  className="field-input"
                  value={cutoffDate}
                  onChange={(e) => setCutoffDate(e.target.value)}
                />
                <span className="field-hint">Calibration uses ONLY data up to this date.</span>
              </div>
            </div>
          </>
        )}

        {mode === 'today' && (
          <div className="section-label">
            Today's Picks
            <span className="section-label-hint">{selectedSymbols.length} ticker{selectedSymbols.length === 1 ? '' : 's'} selected</span>
          </div>
        )}

        {mode === 'backtest' && (
          <>
            <div className="section-label">Backtest the Switching System</div>
            <span className="field-hint">
              Tests the ticker's already-calibrated playbook (from the Calibrate tab) -- it isn't recalibrated
              here. If it hasn't been calibrated yet, running this will fail with a clear error. Tests{' '}
              <strong>{backtestStartDate || '—'}</strong> – <strong>{backtestEndDate || '—'}</strong> (the header's
              date range) -- change it there, not here. If that start predates the playbook's own calibration
              cutoff, it's pulled forward to the cutoff automatically, so the test never sees data the playbook
              was calibrated on.
            </span>
            <div className="chip-row" style={{ marginTop: 12 }}>
              {selectedSymbols.map((sym) => (
                <button
                  key={sym}
                  type="button"
                  className={`chip${effectiveBacktestSymbol === sym ? ' active' : ''}`}
                  onClick={() => setBacktestSymbol(sym)}
                >
                  {sym}
                </button>
              ))}
            </div>
          </>
        )}

        {(mode === 'calibrate' || mode === 'today') && selectedSymbols.length === 0 && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            Select at least one ticker in the header first.
          </div>
        )}
        {mode === 'backtest' && !effectiveBacktestSymbol && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            Select at least one ticker in the header first.
          </div>
        )}

        {activeMutation.isError && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            {activeMutation.error.message}
          </div>
        )}

        <Button
          variant="primary"
          disabled={activeMutation.isPending}
          onClick={mode === 'calibrate' ? handleCalibrate : mode === 'today' ? handleRunToday : handleRunBacktest}
          style={{ marginTop: 16 }}
        >
          {activeMutation.isPending
            ? 'Working…'
            : mode === 'calibrate'
              ? 'Calibrate →'
              : mode === 'today'
                ? "Get Today's Picks →"
                : 'Run Backtest →'}
        </Button>
      </Card>

      {mode === 'calibrate' && lastCalibrationResults && (
        <Card style={{ marginTop: 16 }}>
          <div className="section-label">
            Calibrated Profiles
            <span className="section-label-hint">{profiles.length} ticker{profiles.length === 1 ? '' : 's'}</span>
          </div>

          {failedCalibrationSymbols.length > 0 && (
            <div className="field-hint" style={{ marginBottom: 12 }}>
              Couldn't calibrate: {failedCalibrationSymbols.join(', ')}
            </div>
          )}

          {profiles.length === 0 && (
            <EmptyState title="Nothing calibrated" body="None of the requested tickers produced enough trades to build a playbook." />
          )}

          {profiles.map((profile) => (
            <div key={profile.symbol} style={{ marginTop: 16 }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 10, flexWrap: 'wrap' }}>
                <span style={{ fontSize: 16, fontWeight: 700 }}>{profile.symbol}</span>
                <span className="badge">Calibrated through {profile.calibrated_through}</span>
                <span className="badge">Proxies: {profile.market_proxies.join(', ')}</span>
              </div>

              <div className="detail-panel">
                <div className="detail-metric">
                  <div className="detail-metric-label">Default Strategy</div>
                  <span className="mono metric-value">{displayName(profile.default_strategy)}</span>
                </div>
                <div className="detail-metric">
                  <div className="detail-metric-label">Stop Loss (× ATR)</div>
                  <MetricValue value={profile.stop_loss_atr_multiple} format="ratio" />
                </div>
                <div className="detail-metric">
                  <div className="detail-metric-label">Take Profit (× ATR)</div>
                  <MetricValue value={profile.take_profit_atr_multiple} format="ratio" />
                </div>
                <div className="detail-metric">
                  <div className="detail-metric-label">Entry Window</div>
                  <span className="mono metric-value">
                    {profile.entry_time_start ? `${profile.entry_time_start} – ${profile.entry_time_end}` : 'Full session'}
                  </span>
                </div>
              </div>

              <div className="data-table-scroll" style={{ marginTop: 12 }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Regime</th>
                      <th>Strategy</th>
                      <th>Params</th>
                      <th className="align-right">Trades</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(profile.strategy_by_regime).map(([bucket, strategyName]) => {
                      const override = profile.regime_params?.[bucket]
                      return (
                        <tr key={bucket}>
                          <td>
                            <RegimeBadges bucket={bucket} />
                          </td>
                          <td>{displayName(strategyName)}</td>
                          <td className="mono">
                            {override ? (
                              <>
                                <span className="badge badge-accent" style={{ marginRight: 6 }}>
                                  Tuned
                                </span>
                                SL {override.stop_loss_atr_multiple}× / TP {override.take_profit_atr_multiple}×
                                {override.entry_time_start ? ` / ${override.entry_time_start}–${override.entry_time_end}` : ' / Full session'}
                              </>
                            ) : (
                              <span className="field-hint">Ticker-wide</span>
                            )}
                          </td>
                          <td className="align-right mono">{profile.regime_trade_counts[bucket]}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </Card>
      )}

      {mode === 'today' && lastDailySelectionResults && (
        <Card style={{ marginTop: 16 }}>
          <div className="section-label">
            Today's Picks
            <span className="section-label-hint">{selections.length} ticker{selections.length === 1 ? '' : 's'}</span>
          </div>

          {failedSelectionSymbols.length > 0 && (
            <div className="field-hint" style={{ marginBottom: 12 }}>
              Not calibrated (or couldn't fetch bars): {failedSelectionSymbols.join(', ')} — try Calibrate first.
            </div>
          )}

          {selections.length === 0 && <EmptyState title="No picks yet" body="Every requested ticker failed -- calibrate it first." />}

          {selections.length > 0 && (
            <div className="data-table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th className="align-right">Price</th>
                    <th>As Of</th>
                    <th>Regime</th>
                    <th>Strategy</th>
                    <th>Live Signal</th>
                    <th>Params</th>
                  </tr>
                </thead>
                <tbody>
                  {selections.map((sel) => (
                    <tr key={sel.symbol}>
                      <td style={{ fontWeight: 600 }}>{sel.symbol}</td>
                      <td className="align-right mono">{sel.price != null ? sel.price.toFixed(2) : '—'}</td>
                      <td>{formatDateTime(sel.as_of)}</td>
                      <td>
                        <RegimeBadges bucket={sel.regime_bucket} />
                      </td>
                      <td>
                        {displayName(sel.selected_strategy)}
                        {sel.used_fallback && (
                          <span className="badge" style={{ marginLeft: 6 }} title="No regime-specific pick -- using the ticker's unconditional-best strategy.">
                            fallback
                          </span>
                        )}
                      </td>
                      <td>
                        {sel.has_live_signal ? (
                          <span className={`signal-badge signal-badge-${sel.signal_direction === 'long' ? 'positive' : 'negative'}`}>
                            {sel.signal_direction === 'long' ? 'LONG' : 'SHORT'} · {sel.bars_ago} bars ago
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-tertiary)' }}>—</span>
                        )}
                      </td>
                      <td className="mono" style={{ fontSize: 12, whiteSpace: 'nowrap' }}>
                        SL {sel.stop_loss_atr_multiple}× / TP {sel.take_profit_atr_multiple}×
                        {sel.entry_time_start && ` · ${sel.entry_time_start}–${sel.entry_time_end}`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {mode === 'backtest' && lastSelectionBacktestResults && (
        <Card style={{ marginTop: 16 }}>
          <div className="section-label">
            {lastSelectionBacktestResults.symbol} — Switching vs. Baseline
            <span className="section-label-hint">
              {lastSelectionBacktestResults.test_start} – {lastSelectionBacktestResults.test_end} (out of sample)
            </span>
          </div>

          <div className="data-table-scroll" style={{ marginTop: 12 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th className="align-right">Switching</th>
                  <th className="align-right">Baseline ({displayName(lastSelectionBacktestResults.baseline_strategy)})</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Net Profit</td>
                  <td className="align-right">
                    <MetricValue value={lastSelectionBacktestResults.switching_metrics.net_profit} format="currency" />
                  </td>
                  <td className="align-right">
                    <MetricValue value={lastSelectionBacktestResults.baseline_metrics.net_profit} format="currency" />
                  </td>
                </tr>
                <tr>
                  <td>Profit Factor</td>
                  <td className="align-right">
                    <MetricValue value={lastSelectionBacktestResults.switching_metrics.profit_factor} format="ratio" />
                  </td>
                  <td className="align-right">
                    <MetricValue value={lastSelectionBacktestResults.baseline_metrics.profit_factor} format="ratio" />
                  </td>
                </tr>
                <tr>
                  <td>Win Rate</td>
                  <td className="align-right">
                    <MetricValue value={lastSelectionBacktestResults.switching_metrics.win_rate} format="percent" />
                  </td>
                  <td className="align-right">
                    <MetricValue value={lastSelectionBacktestResults.baseline_metrics.win_rate} format="percent" />
                  </td>
                </tr>
                <tr>
                  <td>Trades</td>
                  <td className="align-right mono">{lastSelectionBacktestResults.switching_trade_count}</td>
                  <td className="align-right mono">{lastSelectionBacktestResults.baseline_trade_count}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="section-label" style={{ marginTop: 24 }}>
            Regime Segments
            <span className="section-label-hint">
              {lastSelectionBacktestResults.segments.length} segment{lastSelectionBacktestResults.segments.length === 1 ? '' : 's'}
            </span>
          </div>

          {lastSelectionBacktestResults.segments.length === 0 && (
            <EmptyState title="No segments" body="No classifiable trading days in the test window." />
          )}

          {lastSelectionBacktestResults.segments.length > 0 && (
            <div className="data-table-scroll" style={{ marginTop: 12 }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Period</th>
                    <th>Regime</th>
                    <th>Strategy</th>
                    <th>Params</th>
                    <th className="align-right">Trades</th>
                    <th className="align-right">Net Profit</th>
                    <th className="align-right">Win Rate</th>
                    <th className="align-right">Profit Factor</th>
                  </tr>
                </thead>
                <tbody>
                  {lastSelectionBacktestResults.segments.map((seg, idx) => (
                    <tr key={idx}>
                      <td>
                        {formatDate(seg.start_date)} – {formatDate(seg.end_date)}
                      </td>
                      <td>
                        <RegimeBadges bucket={seg.regime_bucket} />
                      </td>
                      <td>{displayName(seg.strategy_used)}</td>
                      <td className="mono" style={{ fontSize: 12, whiteSpace: 'nowrap' }}>
                        SL {seg.stop_loss_atr_multiple}× / TP {seg.take_profit_atr_multiple}×
                        {seg.entry_time_start && ` · ${seg.entry_time_start}–${seg.entry_time_end}`}
                      </td>
                      <td className="align-right mono">{seg.trade_count}</td>
                      <td className="align-right">
                        <MetricValue value={seg.metrics.net_profit} format="currency" />
                      </td>
                      <td className="align-right">
                        <MetricValue value={seg.metrics.win_rate} format="percent" />
                      </td>
                      <td className="align-right">
                        <MetricValue value={seg.metrics.profit_factor} format="ratio" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="section-label" style={{ marginTop: 24 }}>
            Trades
            <span className="section-label-hint">
              {lastSelectionBacktestResults.switching_trades.length} trade
              {lastSelectionBacktestResults.switching_trades.length === 1 ? '' : 's'}
            </span>
          </div>
          <div style={{ marginTop: 12 }}>
            <TradesTable
              trades={lastSelectionBacktestResults.switching_trades}
              extraColumnLabel="Strategy"
              getExtraColumnValue={(t) => displayName(t.strategy_name)}
            />
          </div>
        </Card>
      )}
    </div>
  )
}
