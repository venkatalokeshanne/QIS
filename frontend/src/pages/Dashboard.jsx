import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import { useDatasets, useStrategies } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import './Dashboard.css'

const WORKFLOW_STEPS = [
  { label: 'Upload Dataset', to: '/upload' },
  { label: 'Run All Strategies', to: '/run' },
  { label: 'Rank Results', to: '/results' },
  { label: 'Compare Best', to: '/compare' },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const { data: datasets } = useDatasets()
  const { data: strategies } = useStrategies()
  const lastRunResults = useResearchStore((s) => s.lastRunResults)

  // Best strategy/ticker pairing across the whole last run, not just within
  // one dataset -- each dataset's own `rank === 1` only means "best for that
  // ticker," so the global best needs comparing overall_score across all of them.
  const topResult = (lastRunResults?.dataset_results || [])
    .flatMap((d) => d.results)
    .reduce((best, r) => (r.overall_score !== null && (!best || r.overall_score > best.overall_score) ? r : best), null)

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Given this historical dataset, which trading strategy performs best?"
      />

      <div className="dashboard-stats">
        <Card tight className="stat-card">
          <div className="stat-value mono">{datasets?.length ?? '—'}</div>
          <div className="stat-label">Datasets</div>
        </Card>
        <Card tight className="stat-card">
          <div className="stat-value mono">{strategies?.length ?? '—'}</div>
          <div className="stat-label">Strategies Available</div>
        </Card>
        <Card tight className="stat-card">
          <div className="stat-value mono">
            {topResult ? topResult.overall_score.toFixed(1) : '—'}
          </div>
          <div className="stat-label">
            {topResult ? `Top Score — ${topResult.strategy_display_name}` : 'No runs yet'}
          </div>
        </Card>
      </div>

      <Card style={{ marginTop: 20 }}>
        <div className="section-label">Research Workflow</div>
        <div className="workflow-row">
          {WORKFLOW_STEPS.map((step, i) => (
            <div key={step.to} className="workflow-step-wrap">
              <button className="workflow-step" onClick={() => navigate(step.to)}>
                <span className="workflow-step-index mono">{String(i + 1).padStart(2, '0')}</span>
                <span>{step.label}</span>
              </button>
              {i < WORKFLOW_STEPS.length - 1 && <span className="workflow-arrow">→</span>}
            </div>
          ))}
        </div>
      </Card>

      <div className="dashboard-actions">
        <Button variant="primary" onClick={() => navigate('/upload')}>
          Upload Data
        </Button>
        {lastRunResults && (
          <Button variant="secondary" onClick={() => navigate('/results')}>
            View Last Results
          </Button>
        )}
      </div>
    </div>
  )
}
