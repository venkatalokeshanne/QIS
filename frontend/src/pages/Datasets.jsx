import { useState, Fragment } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import { useDatasets, useDatasetPreview, useDeleteDataset } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { formatDate } from '../utils/format'

export default function Datasets() {
  const navigate = useNavigate()
  const { data: datasets, isLoading, isError, error } = useDatasets()
  const [previewId, setPreviewId] = useState(null)
  const deleteMutation = useDeleteDataset()
  const setSelectedDatasetIds = useResearchStore((s) => s.setSelectedDatasetIds)

  if (isLoading) return <div className="loading-text">Loading datasets…</div>
  if (isError) return <div className="error-banner">{error.message}</div>

  if (!datasets?.length) {
    return (
      <div>
        <PageHeader title="Datasets" subtitle="Every dataset you've uploaded, ready to backtest against." />
        <Card>
          <EmptyState
            title="No datasets yet"
            body="Upload historical OHLCV data to start researching strategies."
            action={
              <Button variant="primary" onClick={() => navigate('/upload')}>
                Upload Data
              </Button>
            }
          />
        </Card>
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title="Datasets"
        subtitle="Every dataset you've uploaded, ready to backtest against."
        actions={
          <Button variant="primary" onClick={() => navigate('/upload')}>
            Upload Data
          </Button>
        }
      />

      <Card tight>
        <div className="data-table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Rows</th>
                <th>Range</th>
                <th>Uploaded</th>
                <th className="align-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((d) => (
                <Fragment key={d.id}>
                  <tr>
                    <td style={{ fontWeight: 600 }}>{d.name}</td>
                    <td className="mono">{d.row_count.toLocaleString()}</td>
                    <td className="mono" style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
                      {formatDate(d.start_date)} → {formatDate(d.end_date)}
                    </td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{formatDate(d.created_at)}</td>
                    <td className="align-right">
                      <div style={{ display: 'flex', gap: 6, justifyContent: 'flex-end' }}>
                        <Button size="sm" variant="ghost" onClick={() => setPreviewId(previewId === d.id ? null : d.id)}>
                          {previewId === d.id ? 'Hide' : 'Preview'}
                        </Button>
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => {
                            setSelectedDatasetIds([d.id])
                            navigate('/run')
                          }}
                        >
                          Run Backtests
                        </Button>
                        <Button size="sm" variant="danger" onClick={() => deleteMutation.mutate(d.id)}>
                          Delete
                        </Button>
                      </div>
                    </td>
                  </tr>
                  {previewId === d.id && (
                    <tr>
                      <td colSpan={5} style={{ padding: 0, background: 'var(--bg-base)' }}>
                        <DatasetPreview datasetId={d.id} />
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

function DatasetPreview({ datasetId }) {
  const { data, isLoading } = useDatasetPreview(datasetId, 10)
  if (isLoading) return <div className="loading-text" style={{ padding: 16 }}>Loading preview…</div>
  if (!data?.rows?.length) return null

  const columns = Object.keys(data.rows[0])

  return (
    <div style={{ padding: '16px 24px' }}>
      <div className="data-table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c} className={c !== 'timestamp' ? 'align-right' : ''}>
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, i) => (
              <tr key={i}>
                {columns.map((c) => (
                  <td key={c} className={`mono${c !== 'timestamp' ? ' align-right' : ''}`}>
                    {typeof row[c] === 'number' ? row[c].toFixed(2) : row[c]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
