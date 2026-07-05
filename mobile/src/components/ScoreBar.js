import { View, Text, StyleSheet } from 'react-native'
import { colors, fonts, spacing } from '../styles/tokens'

// Ported from frontend/src/components/ScoreBar.jsx -- the one
// deliberate visual flourish in the app: a thin, single-color bar
// whose width encodes the overall ranking score. No gradient, no
// shadow -- width is the only variable.
export default function ScoreBar({ score }) {
  if (score === null || score === undefined) {
    return <Text style={styles.empty}>—</Text>
  }
  const pct = Math.max(0, Math.min(100, score))
  return (
    <View style={styles.wrap}>
      <Text style={styles.value}>{score.toFixed(1)}</Text>
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
