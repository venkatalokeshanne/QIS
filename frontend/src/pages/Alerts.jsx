import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import {
  useStrategies,
  useWatches,
  useDeleteWatch,
  useLevelWatches,
  useCreateLevelWatch,
  useDeleteLevelWatch,
} from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { formatDateTime } from '../utils/format'

function StrategySignalsSection() {
  const { data: strategies } = useStrategies()
  const { data: watches, isLoading } = useWatches()
  const deleteWatch = useDeleteWatch()

  const displayName = (strategyName) =>
    (strategies || []).find((s) => s.name === strategyName)?.display_name || strategyName

  return (
    <Card>
      <div className="section-label">Strategy Signals</div>
      <p className="field-hint" style={{ marginBottom: 16 }}>
        Get a Telegram message the moment any of these fire a new entry or exit. Turn these on from a
        strategy's Live Signal tab.
      </p>

      {isLoading && <div className="loading-text">Loading…</div>}

      {!isLoading && (watches || []).length === 0 && (
        <EmptyState
          title="No signal alerts yet"
          body="Open a strategy's Live Signal tab and click Notify next to a ticker to add one."
        />
      )}

      {(watches || []).length > 0 && (
        <div className="data-table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Strategy</th>
                <th>Interval</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {watches.map((w) => (
                <tr key={w.id}>
                  <td style={{ fontWeight: 600 }}>{w.symbol}</td>
                  <td>{displayName(w.strategy_name)}</td>
                  <td className="mono">{w.interval}</td>
                  <td>{formatDateTime(w.created_at)}</td>
                  <td>
                    <Button size="sm" variant="ghost" onClick={() => deleteWatch.mutate(w.id)}>
                      Remove
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}

function DailyLevelsSection() {
  const selectedSymbols = useResearchStore((s) => s.selectedSymbols)
  const { data: levelWatches, isLoading } = useLevelWatches()
  const createLevelWatch = useCreateLevelWatch()
  const deleteLevelWatch = useDeleteLevelWatch()

  const watchedSymbols = new Set((levelWatches || []).map((w) => w.symbol))
  const quickAddSymbols = selectedSymbols.filter((s) => !watchedSymbols.has(s))

  return (
    <Card style={{ marginTop: 16 }}>
      <div className="section-label">Daily Levels</div>
      <p className="field-hint" style={{ marginBottom: 16 }}>
        Get a Telegram message whenever a symbol's Auto Support/Resistance levels change.
      </p>

      {quickAddSymbols.length > 0 && (
        <div className="chip-row" style={{ marginBottom: 16 }}>
          {quickAddSymbols.map((s) => (
            <button
              key={s}
              type="button"
              className="chip"
              onClick={() => createLevelWatch.mutate(s)}
              title={`Add a level watch for ${s}`}
            >
              + {s}
            </button>
          ))}
        </div>
      )}

      {isLoading && <div className="loading-text">Loading…</div>}

      {!isLoading && (levelWatches || []).length === 0 && (
        <EmptyState
          title="No level alerts yet"
          body="Select a ticker in the header, then click one of the quick-add chips above, or use the Notify button on Daily Levels."
        />
      )}

      {(levelWatches || []).length > 0 && (
        <div className="data-table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Last Levels</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {levelWatches.map((w) => (
                <tr key={w.id}>
                  <td style={{ fontWeight: 600 }}>{w.symbol}</td>
                  <td className="mono">{w.last_levels ? w.last_levels.join(', ') : '—'}</td>
                  <td>{formatDateTime(w.created_at)}</td>
                  <td>
                    <Button size="sm" variant="ghost" onClick={() => deleteLevelWatch.mutate(w.id)}>
                      Remove
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}

export default function Alerts() {
  return (
    <div>
      <PageHeader
        title="Alerts"
        subtitle="Everything sending you a Telegram message right now — strategy buy/sell signals and Daily Levels support/resistance changes."
      />
      <StrategySignalsSection />
      <DailyLevelsSection />
    </div>
  )
}
