import { View, Text, ScrollView, StyleSheet, ActivityIndicator } from 'react-native'
import Card from '../../components/Card'
import Badge from '../../components/Badge'
import Button from '../../components/Button'
import EmptyState from '../../components/EmptyState'
import { useStrategyDetail } from './StrategyDetailContext'
import { colors, fonts, spacing } from '../../styles/tokens'

export default function InfoTab() {
  const { strategiesLoading, strategy, addToBatch } = useStrategyDetail()

  if (strategiesLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={colors.accent} />
      </View>
    )
  }

  if (!strategy) {
    return (
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <Card>
          <EmptyState title="Unknown strategy" />
        </Card>
      </ScrollView>
    )
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Card>
        <Badge accent>{strategy.category.replace(/_/g, ' ')}</Badge>
        <Text style={styles.description}>{strategy.description}</Text>

        <View style={styles.indicatorsRow}>
          {strategy.indicators_used.map((i) => (
            <View key={i} style={styles.indicatorChip}>
              <Text style={styles.indicatorChipText}>{i}</Text>
            </View>
          ))}
        </View>

        {(strategy.entry_conditions || []).length > 0 && (
          <View style={styles.conditionsBlock}>
            <Text style={styles.conditionLabel}>Entry Conditions</Text>
            {strategy.entry_conditions.map((c) => (
              <Text key={c} style={styles.conditionItem}>
                • {c}
              </Text>
            ))}
          </View>
        )}

        {(strategy.exit_conditions || []).length > 0 && (
          <View style={styles.conditionsBlock}>
            <Text style={styles.conditionLabel}>Exit Conditions</Text>
            {strategy.exit_conditions.map((c) => (
              <Text key={c} style={styles.conditionItem}>
                • {c}
              </Text>
            ))}
          </View>
        )}

        <View style={styles.paramsBlock}>
          {Object.entries(strategy.default_params).map(([k, v]) => (
            <View key={k} style={styles.paramRow}>
              <Text style={styles.paramKey}>{k}</Text>
              <Text style={styles.paramValue}>{String(v)}</Text>
            </View>
          ))}
        </View>

        <Button variant="secondary" onPress={addToBatch} style={styles.actionButton}>
          Add to Batch
        </Button>
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
  },
  description: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textSecondary,
    marginTop: spacing[3],
    lineHeight: 19,
  },
  indicatorsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[2],
    marginTop: spacing[4],
  },
  indicatorChip: {
    backgroundColor: colors.bgPanelRaised,
    borderRadius: 6,
    paddingVertical: 4,
    paddingHorizontal: spacing[2],
  },
  indicatorChipText: {
    fontFamily: fonts.mono,
    fontSize: 11,
    color: colors.textSecondary,
  },
  conditionsBlock: {
    marginTop: spacing[4],
  },
  conditionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[2],
  },
  conditionItem: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textPrimary,
    marginBottom: 4,
  },
  paramsBlock: {
    marginTop: spacing[4],
    backgroundColor: colors.bgPanelRaised,
    borderRadius: 8,
    padding: spacing[3],
  },
  paramRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 3,
  },
  paramKey: {
    fontFamily: fonts.mono,
    fontSize: 12,
    color: colors.textSecondary,
  },
  paramValue: {
    fontFamily: fonts.mono,
    fontSize: 12,
    color: colors.textPrimary,
  },
  actionButton: {
    marginTop: spacing[5],
    alignSelf: 'flex-start',
  },
})
