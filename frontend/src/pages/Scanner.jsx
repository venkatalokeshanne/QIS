import { useMemo, useState } from 'react'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import MetricValue from '../components/MetricValue'
import { useStrategies, useRunScanner, useRunDayPrep } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { formatDateTime } from '../utils/format'

// Groups the flat signal list into one row per TICKER -- "what should
// I watch today" reads as a ticker-first list, not a strategy-signal
// log. Sorted by whichever ticker's freshest match is most recent,
// then symbol, so the most actionable tickers land at the top.
function groupBySymbol(signals) {
  const bySymbol = new Map()
  for (const sig of signals) {
    if (!bySymbol.has(sig.symbol)) bySymbol.set(sig.symbol, [])
    bySymbol.get(sig.symbol).push(sig)
  }
  return Array.from(bySymbol.entries())
    .map(([symbol, sigs]) => ({
      symbol,
      price: sigs[0].price,
      minBarsAgo: Math.min(...sigs.map((s) => s.bars_ago)),
      signals: [...sigs].sort((a, b) => a.bars_ago - b.bars_ago),
    }))
    .sort((a, b) => a.minBarsAgo - b.minBarsAgo || a.symbol.localeCompare(b.symbol))
}

export default function Scanner() {
  const { data: strategies, isLoading: strategiesLoading } = useStrategies()

  const selectedSymbols = useResearchStore((s) => s.selectedSymbols)
  const selectedInterval = useResearchStore((s) => s.selectedInterval)
  const selectedStrategyNames = useResearchStore((s) => s.selectedStrategyNames)
  const executionSettings = useResearchStore((s) => s.executionSettings)
  const scannerLookbackBars = useResearchStore((s) => s.scannerLookbackBars)
  const setScannerLookbackBars = useResearchStore((s) => s.setScannerLookbackBars)
  const lastScanResults = useResearchStore((s) => s.lastScanResults)
  const setLastScanResults = useResearchStore((s) => s.setLastScanResults)
  const lastDayPrepResults = useResearchStore((s) => s.lastDayPrepResults)
  const setLastDayPrepResults = useResearchStore((s) => s.setLastDayPrepResults)

  const [mode, setMode] = useState('day-prep') // 'day-prep' | 'live-signals'

  const runAll = selectedStrategyNames.length === 0
  const scanMutation = useRunScanner()
  const dayPrepMutation = useRunDayPrep()
  const activeMutation = mode === 'day-prep' ? dayPrepMutation : scanMutation

  const displayName = (strategyName) =>
    (strategies || []).find((s) => s.name === strategyName)?.display_name || strategyName

  const handleRun = () => {
    if (selectedSymbols.length === 0) return
    if (mode === 'day-prep') {
      dayPrepMutation.mutate(
        {
          symbols: selectedSymbols,
          interval: selectedInterval,
          strategy_names: runAll ? null : selectedStrategyNames,
          execution: executionSettings,
        },
        { onSuccess: (data) => setLastDayPrepResults(data) }
      )
    } else {
      scanMutation.mutate(
        {
          symbols: selectedSymbols,
          interval: selectedInterval,
          strategy_names: runAll ? null : selectedStrategyNames,
          execution: executionSettings,
          lookback_bars: scannerLookbackBars,
        },
        { onSuccess: (data) => setLastScanResults(data) }
      )
    }
  }

  const signals = lastScanResults?.signals || []
  const failedScanSymbols = lastScanResults?.failed_symbols || []
  const watchlist = useMemo(() => groupBySymbol(signals), [signals])

  const dayPrepTickers = lastDayPrepResults?.tickers || []
  const failedDayPrepSymbols = lastDayPrepResults?.failed_symbols || []

  if (strategiesLoading) {
    return <div className="loading-text">Loading…</div>
  }

  return (
    <div>
      <PageHeader
        title="Scanner"
        actions={
          <div className="chip-row">
            <button
              type="button"
              className={`chip${mode === 'day-prep' ? ' active' : ''}`}
              onClick={() => setMode('day-prep')}
            >
              Day Prep
            </button>
            <button
              type="button"
              className={`chip${mode === 'live-signals' ? ' active' : ''}`}
              onClick={() => setMode('live-signals')}
            >
              Live Signals
            </button>
          </div>
        }
      />

      <Card>
        <div className="section-label">
          Strategies
          <span className="section-label-hint">
            {runAll ? 'Scanning all strategies' : `${selectedStrategyNames.length} selected`}
          </span>
        </div>

        {mode === 'live-signals' && (
          <label className="field" style={{ marginTop: 16, maxWidth: 320 }}>
            <span className="field-label">Signal recency (bars)</span>
            <input
              type="number"
              min={1}
              className="field-input"
              value={scannerLookbackBars}
              onChange={(e) => setScannerLookbackBars(Math.max(1, Number(e.target.value) || 1))}
            />
          </label>
        )}

        {selectedSymbols.length === 0 && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            Select at least one ticker in the header before scanning.
          </div>
        )}

        {activeMutation.isError && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            {activeMutation.error.message}
          </div>
        )}

        <Button
          variant="primary"
          className="analyze-btn"
          disabled={selectedSymbols.length === 0 || activeMutation.isPending}
          onClick={handleRun}
          style={{ marginTop: 16 }}
        >
          {activeMutation.isPending ? 'Scanning…' : 'Scan →'}
        </Button>
      </Card>

      {mode === 'day-prep' && lastDayPrepResults && (
        <Card style={{ marginTop: 16 }}>
          <div className="section-label">
            Tickers to Concentrate On
            <span className="section-label-hint">
              {dayPrepTickers.length} ticker{dayPrepTickers.length === 1 ? '' : 's'}
            </span>
          </div>

          {failedDayPrepSymbols.length > 0 && (
            <div className="field-hint" style={{ marginBottom: 12 }}>
              Couldn't fetch bars for: {failedDayPrepSymbols.join(', ')}
            </div>
          )}

          {dayPrepTickers.length === 0 && (
            <EmptyState title="Nothing worth watching" body="None of the requested strategies have a trading history on these tickers." />
          )}

          {dayPrepTickers.map((ticker) => (
            <div key={ticker.symbol} style={{ marginTop: 16 }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6, flexWrap: 'wrap' }}>
                <span style={{ fontSize: 16, fontWeight: 700 }}>{ticker.symbol}</span>
                <span className="mono" style={{ color: 'var(--text-secondary)' }}>
                  {ticker.price.toFixed(2)}
                </span>
                <span className="badge badge-accent">Score {ticker.concentration_score.toFixed(0)}</span>
                <span className="badge">
                  {ticker.activity_count} recent trade{ticker.activity_count === 1 ? '' : 's'}
                </span>
                {ticker.gap_pct != null && (
                  <span className="badge">
                    {ticker.gap_pct > 0 ? '+' : ''}
                    {(ticker.gap_pct * 100).toFixed(2)}% vs. yesterday's close
                  </span>
                )}
              </div>
              <div className="data-table-scroll">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Strategy</th>
                      <th>Live Signal</th>
                      <th className="align-right">Trades</th>
                      <th className="align-right">Win Rate</th>
                      <th className="align-right">Profit Factor</th>
                      <th className="align-right">Net Profit</th>
                      <th className="align-right">Recent Trades</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ticker.top_strategies.map((edge, idx) => (
                      <tr key={idx}>
                        <td>{displayName(edge.strategy_name) || edge.strategy_display_name}</td>
                        <td>
                          {edge.has_live_signal ? (
                            <span
                              className={`signal-badge signal-badge-${
                                edge.signal_direction === 'long' ? 'positive' : 'negative'
                              }`}
                            >
                              {edge.signal_direction === 'long' ? 'LONG' : 'SHORT'} · {edge.signal_bars_ago} bars ago
                            </span>
                          ) : (
                            <span style={{ color: 'var(--text-tertiary)' }}>—</span>
                          )}
                        </td>
                        <td className="align-right mono">{edge.trade_count}</td>
                        <td className="align-right">
                          <MetricValue value={edge.win_rate} format="percent" />
                        </td>
                        <td className="align-right">
                          <MetricValue value={edge.profit_factor} format="ratio" />
                        </td>
                        <td className="align-right">
                          <MetricValue value={edge.net_profit} format="currency" />
                        </td>
                        <td className="align-right mono">{edge.recent_trade_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </Card>
      )}

      {mode === 'live-signals' && lastScanResults && (
        <Card style={{ marginTop: 16 }}>
          <div className="section-label">
            Tickers to Watch
            <span className="section-label-hint">
              {watchlist.length} ticker{watchlist.length === 1 ? '' : 's'} · {signals.length} setup
              {signals.length === 1 ? '' : 's'}
            </span>
          </div>

          {failedScanSymbols.length > 0 && (
            <div className="field-hint" style={{ marginBottom: 12 }}>
              Couldn't fetch bars for: {failedScanSymbols.join(', ')}
            </div>
          )}

          {watchlist.length === 0 && <EmptyState title="No recent signals" />}

          {watchlist.map((ticker) => (
            <div key={ticker.symbol} style={{ marginTop: 16 }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 6 }}>
                <span style={{ fontSize: 16, fontWeight: 700 }}>{ticker.symbol}</span>
                <span className="mono" style={{ color: 'var(--text-secondary)' }}>
                  {ticker.price.toFixed(2)}
                </span>
                <span className="badge badge-accent">
                  {ticker.signals.length} setup{ticker.signals.length === 1 ? '' : 's'}
                </span>
              </div>
              <div className="data-table-scroll">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Strategy</th>
                      <th>Signal</th>
                      <th>Signal Time</th>
                      <th className="align-right">Bars Ago</th>
                      <th>Status</th>
                      <th className="align-right">Hist. Trades</th>
                      <th className="align-right">Hist. Win Rate</th>
                      <th className="align-right">Hist. Profit Factor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ticker.signals.map((sig, idx) => (
                      <tr key={idx}>
                        <td>{displayName(sig.strategy_name) || sig.strategy_display_name}</td>
                        <td>
                          <span
                            className={`signal-badge signal-badge-${
                              sig.signal_direction === 'long' ? 'positive' : 'negative'
                            }`}
                          >
                            {sig.signal_direction === 'long' ? 'LONG' : 'SHORT'}
                          </span>
                        </td>
                        <td>{formatDateTime(sig.signal_time)}</td>
                        <td className="align-right mono">{sig.bars_ago}</td>
                        <td>
                          <span className={`signal-badge signal-badge-${sig.still_active ? 'positive' : 'neutral'}`}>
                            {sig.still_active ? 'Active' : 'Closed'}
                          </span>
                        </td>
                        <td className="align-right mono">{sig.historical_trade_count ?? '—'}</td>
                        <td className="align-right">
                          <MetricValue value={sig.historical_win_rate} format="percent" />
                        </td>
                        <td className="align-right">
                          <MetricValue value={sig.historical_profit_factor} format="ratio" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </Card>
      )}
    </div>
  )
}
