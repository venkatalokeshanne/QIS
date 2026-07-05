import { useState } from 'react'
import { View, Text, ScrollView, Pressable, ActivityIndicator, StyleSheet } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useNavigation } from '@react-navigation/native'
import { Ionicons } from '@expo/vector-icons'
import Card from '../components/Card'
import Button from '../components/Button'
import DataPickerModal from '../components/DataPickerModal'
import StrategySelectModal from '../components/StrategySelectModal'
import { useDatasets, useStrategies, useRunBacktest } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { colors, fonts, radii, spacing } from '../styles/tokens'

// The main/first screen of the app: pick data (via the small icon,
// which opens DataPickerModal), pick strategies (multi-select, shown
// as removable chips right below Tickers -- same pattern as the
// ticker chips), tap Analyze. No page title/subtitle at the top (the
// bottom tab is already labeled "Backtest"). Monthly breakdown lives
// in Settings now, not here.
export default function RunBacktestsScreen() {
  const navigation = useNavigation()
  const [pickerOpen, setPickerOpen] = useState(false)
  const [strategyPickerOpen, setStrategyPickerOpen] = useState(false)
  const { data: datasets } = useDatasets()
  const { data: strategies, isLoading: strategiesLoading } = useStrategies()

  const selectedDatasetIds = useResearchStore((s) => s.selectedDatasetIds)
  const toggleDatasetId = useResearchStore((s) => s.toggleDatasetId)
  const selectedStrategyNames = useResearchStore((s) => s.selectedStrategyNames)
  const toggleStrategyName = useResearchStore((s) => s.toggleStrategyName)
  const setSelectedStrategyNames = useResearchStore((s) => s.setSelectedStrategyNames)
  const executionSettings = useResearchStore((s) => s.executionSettings)
  const setLastRunResults = useResearchStore((s) => s.setLastRunResults)
  const strategyParamOverrides = useResearchStore((s) => s.strategyParamOverrides)
  const breakdownByMonth = useResearchStore((s) => s.breakdownByMonth)

  const runMutation = useRunBacktest()

  const runAll = selectedStrategyNames.length === 0
  const selectedStrategies = (strategies || []).filter((s) => selectedStrategyNames.includes(s.name))
  const selectedDatasets = (datasets || []).filter((d) => selectedDatasetIds.includes(d.id))

  const handleAnalyze = () => {
    if (selectedDatasetIds.length === 0) return
    const namesToRun = runAll ? (strategies || []).map((s) => s.name) : selectedStrategyNames
    const strategyParams = Object.fromEntries(
      namesToRun.filter((n) => strategyParamOverrides[n]).map((n) => [n, strategyParamOverrides[n]])
    )
    runMutation.mutate(
      {
        dataset_ids: selectedDatasetIds,
        strategy_names: runAll ? null : selectedStrategyNames,
        strategy_params: strategyParams,
        execution: executionSettings,
        breakdown_by_month: breakdownByMonth,
      },
      {
        onSuccess: (data) => {
          setLastRunResults(data)
          navigation.navigate('Results')
        },
      }
    )
  }

  if (strategiesLoading) {
    return (
      <SafeAreaView style={styles.center} edges={['top']}>
        <ActivityIndicator color={colors.accent} />
      </SafeAreaView>
    )
  }

  return (
    <SafeAreaView style={styles.screen} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.topRow}>
        <Pressable onPress={() => setPickerOpen(true)} style={styles.dataIconButton}>
          <Ionicons name="cloud-download-outline" size={18} color={colors.accent} />
          <Text style={styles.dataIconLabel}>Data</Text>
        </Pressable>
      </View>

      <Card style={styles.spacedCard}>
        <Text style={styles.sectionLabel}>Tickers</Text>
        {selectedDatasets.length > 0 && (
          <View style={styles.chipRow}>
            {selectedDatasets.map((d) => (
              <Pressable key={d.id} onPress={() => toggleDatasetId(d.id)} style={styles.tickerChip}>
                <Text style={styles.tickerChipText}>{d.name}</Text>
                <Ionicons name="close" size={12} color={colors.accent} />
              </Pressable>
            ))}
          </View>
        )}
      </Card>

      <Card style={styles.spacedCard}>
        <Text style={styles.sectionLabel}>Strategies</Text>
        <View style={styles.chipRow}>
          {runAll ? (
            <View style={styles.allChip}>
              <Text style={styles.allChipText}>All Strategies</Text>
            </View>
          ) : (
            selectedStrategies.map((s) => (
              <Pressable key={s.name} onPress={() => toggleStrategyName(s.name)} style={styles.tickerChip}>
                <Text style={styles.tickerChipText}>{s.display_name}</Text>
                <Ionicons name="close" size={12} color={colors.accent} />
              </Pressable>
            ))
          )}
          <Pressable onPress={() => setStrategyPickerOpen(true)} style={styles.addChip}>
            <Ionicons name="add" size={14} color={colors.textSecondary} />
            <Text style={styles.addChipText}>Choose</Text>
          </Pressable>
        </View>
      </Card>

      {selectedDatasetIds.length === 0 && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>Select at least one ticker before running.</Text>
        </View>
      )}

      {runMutation.isError && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{runMutation.error.message}</Text>
        </View>
      )}

      <Button
        variant="primary"
        disabled={selectedDatasetIds.length === 0 || runMutation.isPending}
        onPress={handleAnalyze}
        style={styles.analyzeButton}
      >
        {runMutation.isPending ? 'Analyzing…' : 'Analyze →'}
      </Button>

      <DataPickerModal visible={pickerOpen} onClose={() => setPickerOpen(false)} />
      <StrategySelectModal
        visible={strategyPickerOpen}
        onClose={() => setStrategyPickerOpen(false)}
        strategies={strategies || []}
        selectedNames={selectedStrategyNames}
        onToggle={toggleStrategyName}
        onSelectAll={() => {
          setSelectedStrategyNames([])
          setStrategyPickerOpen(false)
        }}
        onViewDetail={(name) => navigation.navigate('StrategyDetail', { name })}
      />
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.bgBase,
  },
  content: {
    padding: spacing[4],
  },
  center: {
    flex: 1,
    backgroundColor: colors.bgBase,
    alignItems: 'center',
    justifyContent: 'center',
  },
  topRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginBottom: spacing[4],
  },
  dataIconButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingVertical: 6,
    paddingHorizontal: spacing[3],
    borderRadius: radii.sm,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    backgroundColor: colors.bgPanelRaised,
  },
  dataIconLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 12,
    color: colors.accent,
  },
  spacedCard: {
    marginBottom: spacing[4],
  },
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[2],
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[2],
    alignItems: 'center',
  },
  tickerChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 6,
    paddingHorizontal: spacing[3],
    borderRadius: radii.sm,
    backgroundColor: colors.accentWash,
    borderWidth: 1,
    borderColor: colors.accent,
  },
  tickerChipText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.accent,
  },
  allChip: {
    paddingVertical: 6,
    paddingHorizontal: spacing[3],
    borderRadius: radii.sm,
    backgroundColor: colors.bgPanelRaised,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
  },
  allChipText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
  },
  addChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingVertical: 6,
    paddingHorizontal: spacing[3],
    borderRadius: radii.sm,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    backgroundColor: colors.bgPanelRaised,
  },
  addChipText: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 12,
    color: colors.textSecondary,
  },
  errorBanner: {
    backgroundColor: colors.negativeWash,
    borderRadius: radii.sm,
    padding: spacing[3],
    marginBottom: spacing[3],
  },
  errorText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.negative,
  },
  analyzeButton: {
    marginTop: spacing[2],
  },
})
