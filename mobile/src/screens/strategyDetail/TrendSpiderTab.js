import { View, Text, ScrollView, StyleSheet } from 'react-native'
import Card from '../../components/Card'
import EmptyState from '../../components/EmptyState'
import { useStrategyDetail } from './StrategyDetailContext'
import { trendspiderGuides, trendspiderCommonSteps, trendspiderRiskManagementSteps } from '../../data/trendspiderGuides'
import { colors, fonts, spacing } from '../../styles/tokens'

// Ported from the "trendspider" tab of frontend/src/pages/StrategyDetail.jsx.
export default function TrendSpiderTab() {
  const { name, riskManagementLines } = useStrategyDetail()
  const tsGuide = trendspiderGuides[name]

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Card style={styles.spacedCard}>
        <Text style={styles.sectionLabel}>Setup Steps</Text>
        {trendspiderCommonSteps.map((step, i) => (
          <Text key={i} style={styles.stepItem}>
            {i + 1}. {step}
          </Text>
        ))}
      </Card>

      {tsGuide ? (
        <>
          {tsGuide.directionNote ? <Text style={styles.directionNote}>{tsGuide.directionNote}</Text> : null}

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>Indicators to Add</Text>
            {tsGuide.indicators.map((ind, i) => (
              <View key={i} style={styles.indicatorRow}>
                <Text style={styles.indicatorName}>{ind.name}</Text>
                <Text style={styles.indicatorDetail}>{ind.settings}</Text>
              </View>
            ))}
          </Card>

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>Entry Rules -- Long</Text>
            {tsGuide.entryLong.length > 0 ? (
              tsGuide.entryLong.map((rule, i) => (
                <Text key={i} style={styles.conditionItem}>
                  • {rule}
                </Text>
              ))
            ) : (
              <Text style={styles.hint}>Not supported by this strategy.</Text>
            )}
          </Card>

          {tsGuide.entryShort.length > 0 && (
            <Card style={styles.spacedCard}>
              <Text style={styles.sectionLabel}>Entry Rules -- Short</Text>
              {tsGuide.entryShort.map((rule, i) => (
                <Text key={i} style={styles.conditionItem}>
                  • {rule}
                </Text>
              ))}
            </Card>
          )}

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>Exit Rules</Text>
            {tsGuide.exit.map((rule, i) => (
              <Text key={i} style={styles.conditionItem}>
                • {rule}
              </Text>
            ))}
          </Card>

          {riskManagementLines && (
            <Card style={styles.spacedCard}>
              <Text style={styles.sectionLabel}>Risk Management -- Stop Loss / Take Profit</Text>
              <Text style={styles.hint}>
                Stops and targets aren't part of this strategy's own rules -- they come from your global Execution
                Settings and apply the same way to every strategy. Here's what's currently active and how to match it
                in TrendSpider:
              </Text>
              {riskManagementLines.map((line, i) => (
                <Text key={i} style={styles.monoItem}>
                  • {line}
                </Text>
              ))}
              {trendspiderRiskManagementSteps.map((step, i) => (
                <Text key={`step-${i}`} style={styles.conditionItem}>
                  • {step}
                </Text>
              ))}
            </Card>
          )}

          {tsGuide.notes.length > 0 && (
            <Card>
              <Text style={styles.sectionLabel}>Notes</Text>
              {tsGuide.notes.map((note, i) => (
                <Text key={i} style={note.warning ? styles.warningText : styles.hint}>
                  {note.warning ? '⚠ ' : ''}
                  {note.text}
                </Text>
              ))}
            </Card>
          )}
        </>
      ) : (
        <Card>
          <EmptyState title="No guide yet" />
        </Card>
      )}
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
  spacedCard: {
    marginBottom: spacing[4],
  },
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[3],
  },
  stepItem: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textPrimary,
    marginBottom: spacing[2],
    lineHeight: 19,
  },
  directionNote: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing[4],
  },
  indicatorRow: {
    marginBottom: spacing[2],
  },
  indicatorName: {
    fontFamily: fonts.mono,
    fontSize: 13,
    color: colors.textPrimary,
  },
  indicatorDetail: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2,
  },
  conditionItem: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textPrimary,
    marginBottom: 4,
  },
  monoItem: {
    fontFamily: fonts.mono,
    fontSize: 13,
    color: colors.textPrimary,
    marginBottom: 4,
  },
  hint: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing[3],
  },
  warningText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.negative,
    marginBottom: spacing[2],
  },
})
