import { View, Text, ScrollView, ActivityIndicator, StyleSheet } from 'react-native'
import { useNavigation } from '@react-navigation/native'
import Card from '../../components/Card'
import EmptyState from '../../components/EmptyState'
import DataTable from '../../components/DataTable'
import { useStrategyDetail } from './StrategyDetailContext'
import { formatMetricValue } from '../../utils/format'
import { colors, fonts, spacing } from '../../styles/tokens'

const TICKER_COMPARE_METRICS = ['net_profit', 'win_rate', 'sharpe_ratio', 'total_trades']

// Ported from the "tickers" tab of frontend/src/pages/StrategyDetail.jsx
// -- ranks this one strategy across every selected ticker. Genuinely
// matrix-shaped (many metric columns per ticker row), so it uses the
// horizontal-scroll DataTable rather than card-stacking. Tapping a row
// focuses that ticker and jumps to the Results tab, matching the web
// version's click-a-row behavior.
export default function TickersTab() {
  const navigation = useNavigation()
  const { strategy, selectedDatasetIds, runMutation, tickerRanking, metricFormatByName, setFocusedDatasetId } =
    useStrategyDetail()

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

  if (tickerRanking.length === 0) return null

  const columns = [
    { key: 'rank', label: 'Rank', width: 50, render: (r) => String(r.rank).padStart(2, '0') },
    { key: 'ticker', label: 'Ticker', width: 110, render: (r) => r.dataset_name },
    ...TICKER_COMPARE_METRICS.map((metricName) => ({
      key: metricName,
      label: metricFormatByName[metricName]?.display_name || metricName,
      width: 100,
      mono: true,
      render: (r) => formatMetricValue(r.result.metrics[metricName], metricFormatByName[metricName]?.format),
    })),
    {
      key: 'overall_score',
      label: 'Overall Score',
      width: 110,
      render: (r) => r.result.overall_score?.toFixed(1) ?? '—',
    },
  ]

  const rows = tickerRanking.map((t, i) => ({ ...t, id: t.dataset_id, rank: i + 1 }))

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Card tight>
        <DataTable
          columns={columns}
          rows={rows}
          onRowPress={(row) => {
            setFocusedDatasetId(row.dataset_id)
            navigation.navigate('Results')
          }}
        />
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
})
