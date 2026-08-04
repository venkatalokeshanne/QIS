import { Link } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import { useStrategies, useRunScanner } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { formatDateTime } from '../utils/format'

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

  const runAll = selectedStrategyNames.length === 0
  const scanMutation = useRunScanner()

  const displayName = (strategyName) =>
    (strategies || []).find((s) => s.name === strategyName)?.display_name || strategyName

  const handleScan = () => {
    if (selectedSymbols.length === 0) return
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

  const signals = lastScanResults?.signals || []
  const failedSymbols = lastScanResults?.failed_symbols || []

  if (strategiesLoading) {
    return <div className="loading-text">Loading…</div>
  }

  return (
    <div>
      <PageHeader
        title="Scanner"
        subtitle="Run every selected strategy against every ticker selected in the header and see which ones just flashed a long or short signal."
      />

      <Card>
        <div className="section-label">
          Strategies
          <span className="section-label-hint">
            {runAll ? 'Scanning all strategies' : `${selectedStrategyNames.length} selected`}
          </span>
        </div>
        <p className="field-hint">
          Pick which strategies to scan on the{' '}
          <Link to="/run" style={{ color: 'var(--accent)' }}>
            Run Backtests
          </Link>{' '}
          page's strategy checklist — the same selection is reused here. Leave nothing selected to scan every
          registered strategy.
        </p>

        <label className="field" style={{ marginTop: 16, maxWidth: 320 }}>
          <span className="field-label">Signal recency (bars)</span>
          <input
            type="number"
            min={1}
            className="field-input"
            value={scannerLookbackBars}
            onChange={(e) => setScannerLookbackBars(Math.max(1, Number(e.target.value) || 1))}
          />
          <span className="field-hint">
            A signal counts as a match if its entry landed within this many of the freshest bars.
          </span>
        </label>

        {selectedSymbols.length === 0 && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            Select at least one ticker in the header before scanning.
          </div>
        )}

        {scanMutation.isError && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            {scanMutation.error.message}
          </div>
        )}

        <Button
          variant="primary"
          className="analyze-btn"
          disabled={selectedSymbols.length === 0 || scanMutation.isPending}
          onClick={handleScan}
          style={{ marginTop: 16 }}
        >
          {scanMutation.isPending ? 'Scanning…' : 'Scan →'}
        </Button>
      </Card>

      {lastScanResults && (
        <Card style={{ marginTop: 16 }}>
          <div className="section-label">
            Results
            <span className="section-label-hint">
              {signals.length} signal{signals.length === 1 ? '' : 's'}
            </span>
          </div>

          {failedSymbols.length > 0 && (
            <div className="field-hint" style={{ marginBottom: 12 }}>
              Couldn't fetch bars for: {failedSymbols.join(', ')}
            </div>
          )}

          {signals.length === 0 && (
            <EmptyState
              title="No recent signals"
              body="Nothing in your selected tickers/strategies fired a long or short entry within the recency window."
            />
          )}

          {signals.length > 0 && (
            <div className="data-table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Strategy</th>
                    <th>Signal</th>
                    <th>Signal Time</th>
                    <th>Bars Ago</th>
                    <th>Price</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {signals.map((sig, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600 }}>{sig.symbol}</td>
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
                      <td className="mono">{sig.bars_ago}</td>
                      <td className="mono">{sig.price.toFixed(2)}</td>
                      <td>
                        <span className={`signal-badge signal-badge-${sig.still_active ? 'positive' : 'neutral'}`}>
                          {sig.still_active ? 'Active' : 'Closed'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
