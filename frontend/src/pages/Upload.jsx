import { useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Button from '../components/Button'
import { useUploadDataset } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import './Upload.css'

export default function Upload() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [datasetName, setDatasetName] = useState('')
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)
  const addSelectedDatasetId = useResearchStore((s) => s.addSelectedDatasetId)

  const uploadMutation = useUploadDataset()

  const handleFile = useCallback((file) => {
    if (!file) return
    setSelectedFile(file)
    setDatasetName(file.name.replace(/\.csv$/i, ''))
    setResult(null)
  }, [])

  const onDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    handleFile(e.dataTransfer.files?.[0])
  }

  const onSubmit = () => {
    if (!selectedFile) return
    setProgress(0)
    uploadMutation.mutate(
      { file: selectedFile, name: datasetName, onProgress: setProgress },
      {
        onSuccess: (data) => {
          setResult(data)
          addSelectedDatasetId(data.dataset.id)
        },
      }
    )
  }

  const reset = () => {
    setSelectedFile(null)
    setResult(null)
    setProgress(0)
    setDatasetName('')
    uploadMutation.reset()
  }

  return (
    <div>
      <PageHeader
        title="Upload Data"
        subtitle="Upload historical OHLCV data as CSV. Columns are detected automatically — timestamp, open, high, low, close, and volume, under common header spellings. Need live market data instead? Use “Fetch from Twelve Data” in the header."
      />

      {!result && (
        <Card>
          <div
            className={`dropzone${dragActive ? ' active' : ''}`}
            onDragOver={(e) => {
              e.preventDefault()
              setDragActive(true)
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              hidden
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
            {selectedFile ? (
              <>
                <div className="dropzone-filename mono">{selectedFile.name}</div>
                <div className="dropzone-hint">
                  {(selectedFile.size / 1024).toFixed(1)} KB — click to choose a different file
                </div>
              </>
            ) : (
              <>
                <div className="dropzone-title">Drop a CSV file here, or click to browse</div>
                <div className="dropzone-hint">
                  Intraday OHLCV data — one row per bar, any reasonable timestamp format
                </div>
              </>
            )}
          </div>

          {selectedFile && (
            <>
              <div className="field-group" style={{ marginTop: 20 }}>
                <label className="field-label" htmlFor="dataset-name">
                  Dataset name
                </label>
                <input
                  id="dataset-name"
                  className="field-input"
                  value={datasetName}
                  onChange={(e) => setDatasetName(e.target.value)}
                />
              </div>

              {uploadMutation.isPending && (
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${progress}%` }} />
                </div>
              )}

              {uploadMutation.isError && (
                <div className="error-banner">
                  {uploadMutation.error.message}
                  {uploadMutation.error.issues?.length > 0 && (
                    <ul style={{ margin: '8px 0 0', paddingLeft: 18 }}>
                      {uploadMutation.error.issues.map((issue, i) => (
                        <li key={i}>{issue}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
                <Button variant="primary" onClick={onSubmit} disabled={uploadMutation.isPending}>
                  {uploadMutation.isPending ? 'Uploading…' : 'Upload & Validate'}
                </Button>
                <Button variant="ghost" onClick={reset} disabled={uploadMutation.isPending}>
                  Cancel
                </Button>
              </div>
            </>
          )}
        </Card>
      )}

      {result && (
        <Card>
          <div className="upload-success-header">
            <div>
              <div className="upload-success-title">{result.dataset.name}</div>
              <div className="page-subtitle">
                {result.dataset.row_count.toLocaleString()} rows · {result.dataset.start_date} → {result.dataset.end_date}
              </div>
            </div>
          </div>

          {result.warnings.length > 0 && (
            <div className="warnings-block">
              <div className="warnings-title">Validation warnings</div>
              <ul className="warnings-list">
                {result.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
            <Button variant="primary" onClick={() => navigate('/run')}>
              Run Backtests →
            </Button>
            <Button variant="secondary" onClick={() => navigate('/datasets')}>
              View Datasets
            </Button>
            <Button variant="ghost" onClick={reset}>
              Upload Another
            </Button>
          </div>
        </Card>
      )}
    </div>
  )
}
