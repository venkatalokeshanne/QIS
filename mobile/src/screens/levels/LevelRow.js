import { View, Text, StyleSheet } from 'react-native'
import MetricValue from '../../components/MetricValue'
import { colors, fonts, spacing } from '../../styles/tokens'

// Ported from the LevelRow helper in frontend/src/pages/DailyLevels.jsx.
export default function LevelRow({ label, value, highlight, format = 'currency' }) {
  return (
    <View style={[styles.row, highlight ? styles.rowHighlight : null]}>
      <Text style={styles.label}>{label}</Text>
      <MetricValue value={value} format={format} />
    </View>
  )
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing[1],
  },
  rowHighlight: {
    backgroundColor: colors.accentWash,
    marginHorizontal: -spacing[2],
    paddingHorizontal: spacing[2],
    borderRadius: 4,
  },
  label: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
  },
})
