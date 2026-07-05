import { View, Text, StyleSheet } from 'react-native'
import { colors, fonts, radii } from '../../styles/tokens'

const POSITIVE_OUTCOMES = new Set(['held', 'contained'])
const NEGATIVE_OUTCOMES = new Set(['broken', 'exceeded_upside', 'exceeded_downside', 'exceeded_both'])

function formatOutcome(outcome) {
  return outcome.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

// Ported from OutcomeBadge/DirectionalBadge in frontend/src/pages/DailyLevels.jsx.
export function OutcomeBadge({ outcome }) {
  const variant = POSITIVE_OUTCOMES.has(outcome) ? 'positive' : NEGATIVE_OUTCOMES.has(outcome) ? 'negative' : 'neutral'
  return (
    <View style={[styles.badge, styles[variant]]}>
      <Text style={[styles.text, styles[`${variant}Text`]]}>{formatOutcome(outcome)}</Text>
    </View>
  )
}

export function DirectionalBadge({ closedAbove }) {
  const variant = closedAbove ? 'accent' : 'neutral'
  return (
    <View style={[styles.badge, styles[variant]]}>
      <Text style={[styles.text, styles[`${variant}Text`]]}>{closedAbove ? 'Above' : 'Below'}</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  badge: {
    paddingVertical: 2,
    paddingHorizontal: 8,
    borderRadius: radii.sm,
    alignSelf: 'flex-start',
  },
  text: {
    fontFamily: fonts.ui,
    fontSize: 11,
  },
  positive: { backgroundColor: colors.positiveWash },
  positiveText: { color: colors.positive },
  negative: { backgroundColor: colors.negativeWash },
  negativeText: { color: colors.negative },
  neutral: { backgroundColor: colors.bgPanelRaised },
  neutralText: { color: colors.textSecondary },
  accent: { backgroundColor: colors.accentWash },
  accentText: { color: colors.accent },
})
