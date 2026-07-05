import { View, Text, ScrollView, ActivityIndicator, StyleSheet } from 'react-native'
import Card from '../../components/Card'
import EmptyState from '../../components/EmptyState'
import MetricBar from '../../components/MetricBar'
import EquityCurve from '../../components/EquityCurve'
import DailyPnl from '../../components/DailyPnl'
import MetricRadar from '../../components/MetricRadar'
import TickerFocusChips from './TickerFocusChips'
import { useStrategyDetail } from './StrategyDetailContext'
import { colors, fonts, spacing } from '../../styles/tokens'

const BAR_METRICS = new Set(['win_rate', 'max_drawdown'])

// Ported from the "charts" tab of frontend/src/pages/StrategyDetail.jsx.
// Web lays P&L/Equity/Radar out as a wide grid (charts-row: two
// side-by-side cards under one full-width P&L bar); at phone width
// everything stacks vertically instead, in the same reading order.
export default function ChartsTab() {
  const { strategy, selectedDatasetIds, runMutation, result, metricDefs } = useStrategyDetail()

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
        <Text style={styles.chartLabel}>P&L by Date</Text>
        <DailyPnl trades={result.trades} main />
      </Card>

      <Card style={styles.spacedCard}>
        <Text style={styles.chartLabel}>Equity Curve</Text>
        <EquityCurve trades={result.trades} />
      </Card>

      <Card style={styles.spacedCard}>
        <Text style={styles.chartLabel}>Strategy Fingerprint</Text>
        <MetricRadar metrics={result.metrics} />
      </Card>

      <Card>
        <View style={styles.metricsGrid}>
          {(metricDefs || [])
            .filter((def) => BAR_METRICS.has(def.name))
            .map((def) => (
              <View key={def.name} style={styles.metricCell}>
                <Text style={styles.metricLabel}>{def.display_name}</Text>
                <MetricBar value={result.metrics[def.name]} />
              </View>
            ))}
        </View>
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
  chartLabel: {
    fontFamily: fonts.ui,
    fontSize: 11,
    color: colors.textSecondary,
    marginBottom: spacing[3],
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[4],
  },
  metricCell: {
    minWidth: 100,
  },
  metricLabel: {
    fontFamily: fonts.ui,
    fontSize: 11,
    color: colors.textSecondary,
    marginBottom: 2,
  },
})
