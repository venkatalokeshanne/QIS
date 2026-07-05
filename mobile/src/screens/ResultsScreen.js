import { useMemo, useState } from 'react'
import { View, Text, ScrollView, Pressable, StyleSheet } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useNavigation } from '@react-navigation/native'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import ScoreBar from '../components/ScoreBar'
import MetricValue from '../components/MetricValue'
import TradesTable from '../components/TradesTable'
import StickyColumnTable from '../components/StickyColumnTable'
import { useMetricDefinitions } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { displayMetricDefs } from '../utils/metricDisplay'
import { colors, fonts, radii, spacing } from '../styles/tokens'

const SUMMARY_METRIC_ORDER = ['net_profit', 'win_rate', 'profit_factor', 'max_drawdown', 'total_trades']

// Ported from frontend/src/pages/Results.jsx. Grouped-by-ticker view is
// card-stacked (per the plan) with tap-to-expand detail; Matrix view
// (strategies x tickers) is genuinely matrix-shaped so it uses
// StickyColumnTable instead, same as Compare.
export default function ResultsScreen() {
  const navigation = useNavigation()
  const lastRunResults = useResearchStore((s) => s.lastRunResults)
  const compareDatasetId = useResearchStore((s) => s.compareDatasetId)
  const compareSelection = useResearchStore((s) => s.compareSelection)
  const setCompareSelection = useResearchStore((s) => s.setCompareSelection)
  const { data: metricDefs } = useMetricDefinitions()
  const [expandedKey, setExpandedKey] = useState(null)
  const [view, setView] = useState('grouped')

  const metricFormatByName = useMemo(() => {
    const map = {}
    for (const m of metricDefs || []) map[m.name] = m
    return map
  }, [metricDefs])

  if (!lastRunResults) {
    return (
      <SafeAreaView style={styles.screen} edges={['top']}>
        <ScrollView contentContainerStyle={styles.content}>
          <Card>
            <EmptyState
              title="No results yet"
              action={
                <Button variant="primary" onPress={() => navigation.navigate('RunBacktests')}>
                  Run Backtests
                </Button>
              }
            />
          </Card>
        </ScrollView>
      </SafeAreaView>
    )
  }

  const { dataset_results: datasetResults } = lastRunResults
  const isMultiTicker = datasetResults.length > 1

  const toggleCompare = (datasetId, strategyName) => {
    const current = datasetId === compareDatasetId ? compareSelection : []
    setCompareSelection(
      datasetId,
      current.includes(strategyName) ? current.filter((n) => n !== strategyName) : [...current, strategyName]
    )
  }

  return (
    <SafeAreaView style={styles.screen} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.actionsRow}>
        {isMultiTicker && (
          <View style={styles.viewToggle}>
            <Pressable onPress={() => setView('grouped')} style={[styles.chip, view === 'grouped' ? styles.chipActive : null]}>
              <Text style={[styles.chipText, view === 'grouped' ? styles.chipTextActive : null]}>Grouped</Text>
            </Pressable>
            <Pressable onPress={() => setView('matrix')} style={[styles.chip, view === 'matrix' ? styles.chipActive : null]}>
              <Text style={[styles.chipText, view === 'matrix' ? styles.chipTextActive : null]}>Matrix</Text>
            </Pressable>
          </View>
        )}
        {compareSelection.length > 0 && (
          <Button variant="primary" onPress={() => navigation.navigate('Compare')}>
            Compare {compareSelection.length} →
          </Button>
        )}
      </View>

      {(!isMultiTicker || view === 'grouped') &&
        datasetResults.map((d) => (
          <View key={d.dataset_id} style={styles.tickerSection}>
            {isMultiTicker && <Text style={styles.sectionLabel}>{d.dataset_name}</Text>}
            {d.results.map((r) => {
              const key = `${d.dataset_id}:${r.strategy_name}`
              const expanded = expandedKey === key
              const checked = d.dataset_id === compareDatasetId && compareSelection.includes(r.strategy_name)
              return (
                <Card key={key} style={styles.strategyCard}>
                  <Pressable onPress={() => setExpandedKey(expanded ? null : key)}>
                    <View style={styles.strategyRow}>
                      <Pressable
                        onPress={() => toggleCompare(d.dataset_id, r.strategy_name)}
                        style={[styles.checkbox, checked ? styles.checkboxChecked : null]}
                      />
                      <View style={styles.strategyInfo}>
                        <View style={styles.strategyTitleRow}>
                          {r.rank ? (
                            <View style={[styles.rankBadge, r.rank === 1 ? styles.rankBadgeFirst : null]}>
                              <Text style={styles.rankBadgeText}>{String(r.rank).padStart(2, '0')}</Text>
                            </View>
                          ) : null}
                          <Text style={styles.strategyName}>{r.strategy_display_name}</Text>
                        </View>
                        <View style={styles.metricsRow}>
                          {SUMMARY_METRIC_ORDER.slice(0, 3).map((name) => (
                            <MetricValue
                              key={name}
                              value={r.metrics[name]}
                              format={metricFormatByName[name]?.format}
                              style={styles.metricChip}
                            />
                          ))}
                        </View>
                      </View>
                      <ScoreBar score={r.overall_score} />
                    </View>
                  </Pressable>

                  {expanded && (
                    <View style={styles.detailPanel}>
                      <View style={styles.detailMetricsGrid}>
                        {displayMetricDefs(metricDefs).map((def) => (
                          <View key={def.name} style={styles.detailMetric}>
                            <Text style={styles.detailMetricLabel}>{def.display_name}</Text>
                            <MetricValue value={r.metrics[def.name]} format={def.format} />
                          </View>
                        ))}
                      </View>
                      <TradesTable trades={r.trades} />
                    </View>
                  )}
                </Card>
              )
            })}
          </View>
        ))}

      {isMultiTicker && view === 'matrix' && <MatrixView datasetResults={datasetResults} />}
      </ScrollView>
    </SafeAreaView>
  )
}

function MatrixView({ datasetResults }) {
  const strategyOrder = datasetResults[0]?.results.map((r) => ({
    name: r.strategy_name,
    display_name: r.strategy_display_name,
  })) || []

  const scoreFor = (datasetId, strategyName) => {
    const dataset = datasetResults.find((d) => d.dataset_id === datasetId)
    return dataset?.results.find((r) => r.strategy_name === strategyName)?.overall_score ?? null
  }

  const bestScoreByStrategy = {}
  for (const s of strategyOrder) {
    const scores = datasetResults.map((d) => scoreFor(d.dataset_id, s.name)).filter((v) => v !== null)
    bestScoreByStrategy[s.name] = scores.length ? Math.max(...scores) : null
  }

  const columns = datasetResults.map((d) => ({ key: d.dataset_id, label: d.dataset_name }))
  const rows = strategyOrder.map((s) => ({
    label: s.display_name,
    cells: Object.fromEntries(
      datasetResults.map((d) => {
        const score = scoreFor(d.dataset_id, s.name)
        return [d.dataset_id, { text: score?.toFixed(1) ?? '—', best: score !== null && score === bestScoreByStrategy[s.name] }]
      })
    ),
  }))

  return (
    <Card tight>
      <StickyColumnTable columns={columns} rows={rows} />
    </Card>
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
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing[4],
    flexWrap: 'wrap',
    gap: spacing[2],
  },
  viewToggle: {
    flexDirection: 'row',
    gap: spacing[2],
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
  tickerSection: {
    marginBottom: spacing[5],
  },
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[2],
  },
  strategyCard: {
    marginBottom: spacing[3],
  },
  strategyRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing[3],
  },
  checkbox: {
    width: 18,
    height: 18,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    marginTop: 2,
  },
  checkboxChecked: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  strategyInfo: {
    flex: 1,
  },
  strategyTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[2],
  },
  rankBadge: {
    paddingVertical: 2,
    paddingHorizontal: 6,
    borderRadius: radii.sm,
    backgroundColor: colors.bgPanelRaised,
  },
  rankBadgeFirst: {
    backgroundColor: colors.accentWash,
  },
  rankBadgeText: {
    fontFamily: fonts.mono,
    fontSize: 11,
    color: colors.accent,
  },
  strategyName: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 14,
    color: colors.textPrimary,
  },
  metricsRow: {
    flexDirection: 'row',
    gap: spacing[3],
    marginTop: spacing[2],
  },
  metricChip: {
    fontSize: 11,
  },
  detailPanel: {
    marginTop: spacing[4],
    paddingTop: spacing[4],
    borderTopWidth: 1,
    borderTopColor: colors.borderHairline,
  },
  detailMetricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: spacing[4],
  },
  detailMetric: {
    width: '33%',
    paddingRight: spacing[3],
    marginBottom: spacing[3],
  },
  detailMetricLabel: {
    fontFamily: fonts.ui,
    fontSize: 11,
    color: colors.textSecondary,
    marginBottom: 2,
  },
})
