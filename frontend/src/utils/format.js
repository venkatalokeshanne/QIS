// Formats a metric value according to the `format` hint the backend
// attaches to each metric's metadata (currency, percent, ratio,
// count, duration_minutes). Centralized here so every table renders
// numbers identically instead of each component reinventing it.
export function formatMetricValue(value, format) {
  if (value === null || value === undefined) return '—'

  switch (format) {
    case 'currency':
      return `${value < 0 ? '-' : ''}$${Math.abs(value).toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`
    case 'percent':
      return `${value.toFixed(2)}%`
    case 'ratio':
      return value.toFixed(2)
    case 'count':
      return Math.round(value).toString()
    case 'duration_minutes':
      return `${value.toFixed(1)} min`
    default:
      return value.toLocaleString(undefined, { maximumFractionDigits: 2 })
  }
}

export function formatDate(isoString) {
  if (!isoString) return '—'
  const d = new Date(isoString)
  if (Number.isNaN(d.getTime())) return isoString
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

export function formatDateTime(isoString) {
  if (!isoString) return '—'
  const d = new Date(isoString)
  if (Number.isNaN(d.getTime())) return isoString
  return d.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
