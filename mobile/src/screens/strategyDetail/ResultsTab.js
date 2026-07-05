import { View, Text, ScrollView, Pressable, ActivityIndicator, StyleSheet } from 'react-native'
import Card from '../../components/Card'
import EmptyState from '../../components/EmptyState'
import ScoreBar from '../../components/ScoreBar'
import MetricBar from '../../components/MetricBar'
import MetricValue from '../../components/MetricValue'
import TradesTable from '../../components/TradesTable'
import MonthlyBreakdownTable from '../../components/MonthlyBreakdownTable'
import TickerFocusChips from './TickerFocusChips'
import { useStrategyDetail } from './StrategyDetailContext'
import { displayMetricDefs } from '../../utils/metricDisplay'
import { colors, fonts, spacing } from '../../styles/tokens'

// Metrics already 0-100 scale get a visual bar; everything else stays
// plain formatted text -- matches BAR_METRICS in the web version.
const BAR_METRICS = new Set(['win_rate', 'max_drawdown'])

export default function ResultsTab() {
  const {
    strategy,
    selectedDatasetIds,
    runMutation,
    result,
    metricDefs,
    breakdownByMonth,
    setBreakdownByMonth,
    runNow,
  } = useStrategyDetail()

  if (!strategy) return null

  if (selectedDatasetIds.length === 0) {
    return (
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <Card>
          <EmptyState title="Select ticker(s)" />
        </Card>
      </ScrollView>
    )
  }

  if (runMutation.isPending) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={colors.accent} />
        <Text style={styles.loadingText}>Running {strategy.display_name}…</Text>
      </View>
    )
  }

  if (runMutation.isError) {
    return (
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <Text style={styles.errorText}>{runMutation.error.message}</Text>
      </ScrollView>
    )
  }

  if (!result) return null

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <TickerFocusChips />

      <Card style={styles.spacedCard}>
        <View style={styles.headerRow}>
          <View>
            <Text style={styles.metricLabel}>Overall Score</Text>
            <ScoreBar score={result.overall_score} />
          </View>
          <Pressable style={styles.checkboxRow} onPress={() => setBreakdownByMonth(!breakdownByMonth)}>
            <View style={[styles.checkbox, breakdownByMonth ? styles.checkboxChecked : null]} />
            <Text style={styles.checkboxLabel}>Monthly breakdown</Text>
          </Pressable>
        </View>
        <Pressable onPress={runNow} style={styles.rerunButton}>
          <Text style={styles.rerunText}>Re-run</Text>
        </Pressable>

        <View style={styles.metricsGrid}>
          {displayMetricDefs(metricDefs).map((def) => (
            <View key={def.name} style={styles.metricCell}>
              <Text style={styles.metricLabel}>{def.display_name}</Text>
              {BAR_METRICS.has(def.name) ? (
                <MetricBar value={result.metrics[def.name]} />
              ) : (
                <MetricValue value={result.metrics[def.name]} format={def.format} />
              )}
            </View>
          ))}
        </View>
      </Card>

      {result.monthly_metrics && (
        <Card tight style={styles.spacedCard}>
          <Text style={[styles.sectionLabel, styles.tightPadding]}>Monthly Breakdown</Text>
          <MonthlyBreakdownTable monthlyMetrics={result.monthly_metrics} />
        </Card>
      )}

      <Card tight>
        <TradesTable trades={result.trades} />
      </Card>
    </ScrollView>
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
    gap: spacing[3],
  },
  loadingText: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textSecondary,
  },
  errorText: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.negative,
  },
  spacedCard: {
    marginBottom: spacing[4],
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[2],
  },
  checkbox: {
    width: 18,
    height: 18,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
  },
  checkboxChecked: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  checkboxLabel: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textPrimary,
  },
  rerunButton: {
    alignSelf: 'flex-start',
    marginTop: spacing[3],
    paddingVertical: 6,
    paddingHorizontal: spacing[3],
    borderRadius: 6,
    backgroundColor: colors.bgPanelRaised,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
  },
  rerunText: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 12,
    color: colors.textPrimary,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: spacing[5],
  },
  metricCell: {
    width: '33%',
    paddingRight: spacing[3],
    marginBottom: spacing[3],
  },
  metricLabel: {
    fontFamily: fonts.ui,
    fontSize: 11,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
  },
  tightPadding: {
    padding: spacing[4],
    paddingBottom: 0,
  },
})
