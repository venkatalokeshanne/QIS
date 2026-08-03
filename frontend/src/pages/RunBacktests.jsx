import { Link, useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import { useStrategies, useRunBacktest } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import './RunBacktests.css'

export default function RunBacktests() {
  const navigate = useNavigate()
  const { data: strategies, isLoading: strategiesLoading } = useStrategies()

  const selectedSymbols = useResearchStore((s) => s.selectedSymbols)
  const selectedInterval = useResearchStore((s) => s.selectedInterval)
  const backtestStartDate = useResearchStore((s) => s.backtestStartDate)
  const backtestEndDate = useResearchStore((s) => s.backtestEndDate)
  const selectedStrategyNames = useResearchStore((s) => s.selectedStrategyNames)
  const toggleStrategyName = useResearchStore((s) => s.toggleStrategyName)
  const setSelectedStrategyNames = useResearchStore((s) => s.setSelectedStrategyNames)
  const executionSettings = useResearchStore((s) => s.executionSettings)
  const setLastRunResults = useResearchStore((s) => s.setLastRunResults)
  const strategyParamOverrides = useResearchStore((s) => s.strategyParamOverrides)
  const breakdownByMonth = useResearchStore((s) => s.breakdownByMonth)
  const setBreakdownByMonth = useResearchStore((s) => s.setBreakdownByMonth)

  const runMutation = useRunBacktest()

  const runAll = selectedStrategyNames.length === 0

  const handleAnalyze = () => {
    if (selectedSymbols.length === 0) return
    const namesToRun = runAll ? (strategies || []).map((s) => s.name) : selectedStrategyNames
    const strategyParams = Object.fromEntries(
      namesToRun.filter((n) => strategyParamOverrides[n]).map((n) => [n, strategyParamOverrides[n]])
    )
    runMutation.mutate(
      {
        symbols: selectedSymbols,
        interval: selectedInterval,
        start_date: backtestStartDate,
        end_date: backtestEndDate,
        strategy_names: runAll ? null : selectedStrategyNames,
        strategy_params: strategyParams,
        execution: executionSettings,
        breakdown_by_month: breakdownByMonth,
      },
      {
        onSuccess: (data) => {
          setLastRunResults(data)
          navigate('/results')
        },
      }
    )
  }

  if (strategiesLoading) {
    return <div className="loading-text">Loading…</div>
  }

  return (
    <div>
      <PageHeader
        title="Run Backtests"
        subtitle="Choose which strategies to run as a batch against the ticker(s) selected in the header, then analyze."
      />

      <div className="run-layout">
        <div className="run-main">
          <Card>
            <div className="section-label">
              Strategies
              <span className="section-label-hint">
                {runAll ? 'Running all strategies' : `${selectedStrategyNames.length} selected`}
              </span>
            </div>

            <div className="strategy-select-row">
              <Button
                size="sm"
                variant={runAll ? 'primary' : 'secondary'}
                onClick={() => setSelectedStrategyNames([])}
              >
                Run All
              </Button>
            </div>

            <div className="strategy-checklist">
              {strategies.map((s) => (
                <label key={s.name} className="strategy-check-item">
                  <input
                    type="checkbox"
                    checked={selectedStrategyNames.includes(s.name)}
                    onChange={() => toggleStrategyName(s.name)}
                  />
                  <div>
                    <div className="strategy-check-name">{s.display_name}</div>
                    <div className="strategy-check-desc">{s.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </Card>

          {(backtestStartDate || backtestEndDate) && (
            <Card style={{ marginTop: 16 }}>
              <div className="section-label">
                Date Range
                <span className="section-label-hint">set in the header</span>
              </div>
              <p className="field-hint">
                {backtestStartDate || '…'} – {backtestEndDate || '…'}
              </p>
            </Card>
          )}
        </div>

        <div className="run-side">
          <Card>
            <div className="section-label">Execution Settings</div>
            <p className="field-hint">
              Capital, sizing, and risk settings are configured once for the whole app on the{' '}
              <Link to="/settings" style={{ color: 'var(--accent)' }}>
                Settings
              </Link>{' '}
              page.
            </p>
            <label className="checkbox-row" style={{ marginTop: 12 }}>
              <input
                type="checkbox"
                checked={breakdownByMonth}
                onChange={(e) => setBreakdownByMonth(e.target.checked)}
              />
              <span>Monthly breakdown</span>
            </label>
            <p className="field-hint">
              Also slice these same results by calendar month -- useful for seeing how a strategy holds up
              across different stretches of a longer lookback.
            </p>
          </Card>

          {selectedSymbols.length === 0 && (
            <div className="error-banner" style={{ marginTop: 16 }}>
              Select at least one ticker in the header before running.
            </div>
          )}

          {runMutation.isError && (
            <div className="error-banner" style={{ marginTop: 16 }}>
              {runMutation.error.message}
            </div>
          )}

          <Button
            variant="primary"
            className="analyze-btn"
            disabled={selectedSymbols.length === 0 || runMutation.isPending}
            onClick={handleAnalyze}
          >
            {runMutation.isPending ? 'Analyzing…' : 'Analyze →'}
          </Button>
        </div>
      </div>
    </div>
  )
}
