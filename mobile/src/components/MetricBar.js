import { View, Text, StyleSheet } from 'react-native'
import { colors, fonts } from '../styles/tokens'

// Ported from frontend/src/components/MetricBar.jsx -- same visual
// language as ScoreBar, reused for percent-format metrics (win rate,
// max drawdown).
export default function MetricBar({ value }) {
  if (value === null || value === undefined) {
    return <Text style={styles.empty}>—</Text>
  }
  const pct = Math.max(0, Math.min(100, value))
  return (
    <View style={styles.wrap}>
      <Text style={styles.value}>{value.toFixed(1)}%</Text>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${pct}%` }]} />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  wrap: {
    minWidth: 80,
  },
  value: {
    fontFamily: fonts.mono,
    fontSize: 12,
    color: colors.textPrimary,
    marginBottom: 2,
  },
  track: {
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.bgPanelRaised,
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    backgroundColor: colors.accent,
  },
  empty: {
    fontFamily: fonts.mono,
    color: colors.textTertiary,
  },
})
