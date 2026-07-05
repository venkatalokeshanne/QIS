import { ScrollView, StyleSheet } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useNavigation } from '@react-navigation/native'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import StickyColumnTable from '../components/StickyColumnTable'
import { useMetricDefinitions } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { formatMetricValue } from '../utils/format'
import { displayMetricDefs } from '../utils/metricDisplay'
import { colors, spacing } from '../styles/tokens'

// Ported from frontend/src/pages/Compare.jsx onto StickyColumnTable
// (genuinely matrix-shaped: metrics as rows, strategies as columns,
// best value per row highlighted -- the whole point of this screen).
export default function CompareScreen() {
  const navigation = useNavigation()
  const lastRunResults = useResearchStore((s) => s.lastRunResults)
  const compareDatasetId = useResearchStore((s) => s.compareDatasetId)
  const compareSelection = useResearchStore((s) => s.compareSelection)
  const { data: metricDefs } = useMetricDefinitions()

  const datasetResult = lastRunResults?.dataset_results.find((d) => d.dataset_id === compareDatasetId)

  if (!datasetResult || compareSelection.length === 0) {
    return (
      <SafeAreaView style={styles.screen} edges={['top']}>
        <ScrollView contentContainerStyle={styles.content}>
          <Card>
            <EmptyState
              title="Nothing selected to compare"
              action={
                <Button variant="primary" onPress={() => navigation.navigate('Results')}>
                  Go to Results
                </Button>
              }
            />
          </Card>
        </ScrollView>
      </SafeAreaView>
    )
  }

  const selected = datasetResult.results.filter((r) => compareSelection.includes(r.strategy_name))

  const bestForMetric = (metricName, higherIsBetter) => {
    const values = selected.map((r) => r.metrics[metricName]).filter((v) => v !== null && v !== undefined)
    if (values.length === 0) return null
    return higherIsBetter ? Math.max(...values) : Math.min(...values)
  }

  const bestScore = Math.max(...selected.map((s) => s.overall_score ?? -Infinity))

  const columns = selected.map((r) => ({ key: r.strategy_name, label: r.strategy_display_name }))

  const rows = [
    {
      label: 'Overall Score',
      cells: Object.fromEntries(
        selected.map((r) => [
          r.strategy_name,
          { text: r.overall_score?.toFixed(1) ?? '—', best: r.overall_score === bestScore && r.overall_score !== null },
        ])
      ),
    },
    ...displayMetricDefs(metricDefs).map((def) => {
      const best = bestForMetric(def.name, def.higher_is_better)
      return {
        label: def.display_name,
        cells: Object.fromEntries(
          selected.map((r) => {
            const value = r.metrics[def.name]
            return [r.strategy_name, { text: formatMetricValue(value, def.format), best: best !== null && value === best }]
          })
        ),
      }
    }),
  ]

  return (
    <SafeAreaView style={styles.screen} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        <Card tight>
          <StickyColumnTable columns={columns} rows={rows} />
        </Card>
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
})
