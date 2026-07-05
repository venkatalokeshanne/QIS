import { useState } from 'react'
import { View, Text, TextInput, ScrollView, Pressable, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import Card from '../../components/Card'
import Button from '../../components/Button'
import EmptyState from '../../components/EmptyState'
import { useStrategyDetail } from './StrategyDetailContext'
import { useResearchStore } from '../../store/useResearchStore'
import { useWatches, useCreateWatch, useDeleteWatch } from '../../api/hooks'
import { colors, fonts, radii, spacing } from '../../styles/tokens'

const INTERVALS = [
  { value: '1min', label: '1 min' },
  { value: '5min', label: '5 min' },
  { value: '15min', label: '15 min' },
]

// New tab, not in the web app -- lets a day/interday trader get a push
// notification the moment this strategy's own entry/exit logic (the
// SAME logic Results/Charts show for a backtest) fires against a live
// symbol, without having to keep the app open. Creating a watch just
// registers (symbol, interval, strategy, this strategy's current
// Configure-tab params) with the backend poller (app.services.poller);
// delivery is handled entirely server-side.
export default function AlertsTab() {
  const { strategy, effectiveParams } = useStrategyDetail()
  const pushToken = useResearchStore((s) => s.pushToken)
  const { data: watches, isLoading } = useWatches(pushToken)
  const createMutation = useCreateWatch()
  const deleteMutation = useDeleteWatch()

  const [symbol, setSymbol] = useState('')
  const [interval, setInterval_] = useState('5min')

  if (!strategy) return null

  if (!pushToken) {
    return (
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <Card>
          <EmptyState
            title="Notifications unavailable"
            body="Push notification permission wasn't granted, or this is running on a simulator (a physical device is required)."
          />
        </Card>
      </ScrollView>
    )
  }

  const strategyWatches = (watches || []).filter((w) => w.strategy_name === strategy.name)

  const createAlert = () => {
    if (!symbol.trim()) return
    createMutation.mutate(
      {
        expo_push_token: pushToken,
        symbol: symbol.trim().toUpperCase(),
        strategy_name: strategy.name,
        strategy_params: effectiveParams,
        interval,
      },
      { onSuccess: () => setSymbol('') }
    )
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Card>
        <Text style={styles.sectionLabel}>New Alert</Text>
        <TextInput
          style={styles.input}
          placeholder="Symbol (e.g. AAPL)"
          placeholderTextColor={colors.textTertiary}
          autoCapitalize="characters"
          autoCorrect={false}
          value={symbol}
          onChangeText={setSymbol}
        />
        <View style={styles.chipRow}>
          {INTERVALS.map((opt) => (
            <Pressable
              key={opt.value}
              onPress={() => setInterval_(opt.value)}
              style={[styles.chip, interval === opt.value ? styles.chipActive : null]}
            >
              <Text style={[styles.chipText, interval === opt.value ? styles.chipTextActive : null]}>
                {opt.label}
              </Text>
            </Pressable>
          ))}
        </View>
        <Button variant="primary" onPress={createAlert} disabled={!symbol.trim() || createMutation.isPending}>
          Create Alert
        </Button>
        {createMutation.isError && <Text style={styles.errorText}>{createMutation.error.message}</Text>}
      </Card>

      <Card tight style={styles.listCard}>
        <Text style={[styles.sectionLabel, styles.listLabel]}>Active Alerts</Text>
        {!isLoading && strategyWatches.length === 0 && (
          <EmptyState title="No alerts for this strategy yet" />
        )}
        {strategyWatches.map((watch) => (
          <View key={watch.id} style={styles.watchRow}>
            <View style={styles.watchInfo}>
              <Text style={styles.watchSymbol}>{watch.symbol}</Text>
              <Text style={styles.watchMeta}>{INTERVALS.find((o) => o.value === watch.interval)?.label}</Text>
            </View>
            <Pressable onPress={() => deleteMutation.mutate(watch.id)} hitSlop={8}>
              <Ionicons name="trash-outline" size={18} color={colors.textTertiary} />
            </Pressable>
          </View>
        ))}
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
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[3],
  },
  input: {
    fontFamily: fonts.ui,
    fontSize: 14,
    color: colors.textPrimary,
    backgroundColor: colors.bgPanelRaised,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    borderRadius: radii.sm,
    paddingVertical: 9,
    paddingHorizontal: spacing[3],
    marginBottom: spacing[3],
  },
  chipRow: {
    flexDirection: 'row',
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
  errorText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.negative,
    marginTop: spacing[2],
  },
  listCard: {
    marginTop: spacing[4],
  },
  listLabel: {
    paddingHorizontal: spacing[4],
    paddingTop: spacing[4],
  },
  watchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[3],
    borderTopWidth: 1,
    borderTopColor: colors.borderHairline,
  },
  watchInfo: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: spacing[2],
  },
  watchSymbol: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 14,
    color: colors.textPrimary,
  },
  watchMeta: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
  },
})
