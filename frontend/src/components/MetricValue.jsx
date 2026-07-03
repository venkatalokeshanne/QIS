import { formatMetricValue } from '../utils/format'
import './MetricValue.css'

const SIGN_COLORED_FORMATS = new Set(['currency'])

export default function MetricValue({ value, format }) {
  const formatted = formatMetricValue(value, format)
  let colorClass = ''
  if (SIGN_COLORED_FORMATS.has(format) && value !== null && value !== undefined) {
    colorClass = value > 0 ? 'metric-positive' : value < 0 ? 'metric-negative' : ''
  }
  return <span className={`mono metric-value ${colorClass}`}>{formatted}</span>
}
