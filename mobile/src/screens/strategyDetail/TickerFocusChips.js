import { View, Text, Pressable, StyleSheet } from 'react-native'
import { useStrategyDetail } from './StrategyDetailContext'
import { colors, fonts, radii, spacing } from '../../styles/tokens'

// Shared by ResultsTab and ChartsTab -- when more than one ticker is
// selected, lets the user pick which one's results/charts are shown
// (mirrors the web version's identical chip row in both tabs).
export default function TickerFocusChips() {
  const { datasetResults, focusedDatasetId, setFocusedDatasetId } = useStrategyDetail()
  if (datasetResults.length <= 1) return null

  return (
    <View style={styles.row}>
      {datasetResults.map((d) => (
        <Pressable
          key={d.dataset_id}
          onPress={() => setFocusedDatasetId(d.dataset_id)}
          style={[styles.chip, focusedDatasetId === d.dataset_id ? styles.chipActive : null]}
        >
          <Text style={[styles.chipText, focusedDatasetId === d.dataset_id ? styles.chipTextActive : null]}>
            {d.dataset_name}
          </Text>
        </Pressable>
      ))}
    </View>
  )
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[2],
    marginBottom: spacing[4],
  },
  chip: {
    paddingVertical: 6,
    paddingHorizontal: spacing[3],
    borderRadius: radii.sm,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    backgroundColor: colors.bgPanelRaised,
  },
  chipActive: {
    backgroundColor: colors.accentWash,
    borderColor: colors.accent,
  },
  chipText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
  },
  chipTextActive: {
    color: colors.accent,
  },
})
