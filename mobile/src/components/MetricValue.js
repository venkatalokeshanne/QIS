import { Text, StyleSheet } from 'react-native'
import { formatMetricValue } from '../utils/format'
import { colors, fonts } from '../styles/tokens'

const SIGN_COLORED_FORMATS = new Set(['currency'])

// Ported from frontend/src/components/MetricValue.jsx.
export default function MetricValue({ value, format, style }) {
  const formatted = formatMetricValue(value, format)
  let colorStyle = null
  if (SIGN_COLORED_FORMATS.has(format) && value !== null && value !== undefined) {
    colorStyle = value > 0 ? styles.positive : value < 0 ? styles.negative : null
  }
  return <Text style={[styles.base, colorStyle, style]}>{formatted}</Text>
}

const styles = StyleSheet.create({
  base: {
    fontFamily: fonts.mono,
    fontSize: 13,
    color: colors.textPrimary,
  },
  positive: {
    color: colors.positive,
  },
  negative: {
    color: colors.negative,
  },
})
