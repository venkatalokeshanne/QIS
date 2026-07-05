import { useState } from 'react'
import { View, Text, TextInput, ScrollView, Pressable, StyleSheet } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import Card from '../components/Card'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import StrategyPickerModal from '../components/StrategyPickerModal'
import { useStrategies, useWatches, useCreateWatch, useDeleteWatch, useSendTestNotification } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { colors, fonts, radii, spacing } from '../styles/tokens'

const INTERVALS = [
  { value: '1min', label: '1 min' },
  { value: '5min', label: '5 min' },
  { value: '15min', label: '15 min' },
]

// Global, top-level home for signal alerts -- lets a day/interday
// trader get a push notification the moment a strategy's own
// entry/exit logic (the SAME logic Results/Charts show for a
// backtest) fires against a live symbol, without diving into that
// strategy's own detail screen first. Any per-strategy param overrides
// already set on the Configure tab are reused here too (falls back to
// the strategy's own defaults), so an alert matches whatever that
// strategy is currently tuned to.
export default function AlertsScreen() {
  const pushToken = useResearchStore((s) => s.pushToken)
  const strategyParamOverrides = useResearchStore((s) => s.strategyParamOverrides)
  const { data: strategies } = useStrategies()
  const { data: watches, isLoading } = useWatches(pushToken)
  const createMutation = useCreateWatch()
  const deleteMutation = useDeleteWatch()
  const testNotificationMutation = useSendTestNotification()

  const [pickerOpen, setPickerOpen] = useState(false)
  const [strategyName, setStrategyName] = useState(null)
  const [symbol, setSymbol] = useState('')
  const [interval, setInterval_] = useState('5min')

  const selectedStrategy = (strategies || []).find((s) => s.name === strategyName)

  if (!pushToken) {
    return (
      <SafeAreaView style={styles.screen} edges={['top']}>
        <ScrollView contentContainerStyle={styles.content}>
          <Card>
            <EmptyState
              title="Notifications unavailable"
              body="Push notification permission wasn't granted, or this is running on a simulator (a physical device is required)."
            />
          </Card>
        </ScrollView>
      </SafeAreaView>
    )
  }

  const createAlert = () => {
    if (!symbol.trim() || !selectedStrategy) return
    const effectiveParams = { ...selectedStrategy.default_params, ...(strategyParamOverrides[selectedStrategy.name] || {}) }
    createMutation.mutate(
      {
        expo_push_token: pushToken,
        symbol: symbol.trim().toUpperCase(),
        strategy_name: selectedStrategy.name,
        strategy_params: effectiveParams,
        interval,
      },
      { onSuccess: () => setSymbol('') }
    )
  }

  return (
    <SafeAreaView style={styles.screen} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        <Card>
          <Text style={styles.sectionLabel}>New Alert</Text>

          <Pressable style={styles.strategyButton} onPress={() => setPickerOpen(true)}>
            <Text style={selectedStrategy ? styles.strategyButtonText : styles.strategyButtonPlaceholder}>
              {selectedStrategy ? selectedStrategy.display_name : 'Choose strategy'}
            </Text>
            <Ionicons name="chevron-down" size={16} color={colors.textSecondary} />
          </Pressable>

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

          <Button
            variant="primary"
            onPress={createAlert}
            disabled={!symbol.trim() || !selectedStrategy || createMutation.isPending}
          >
            Create Alert
          </Button>
          {createMutation.isError && <Text style={styles.errorText}>{createMutation.error.message}</Text>}
        </Card>

        <Card style={styles.spacedCard}>
          <Text style={styles.sectionLabel}>Test Delivery</Text>
          <Text style={styles.hintText}>
            Sends a push right now, bypassing strategy signals and market hours -- confirms notifications actually
            reach this device.
          </Text>
          <Button
            variant="secondary"
            onPress={() => testNotificationMutation.mutate(pushToken)}
            disabled={testNotificationMutation.isPending}
          >
            Send Test Notification
          </Button>
          {testNotificationMutation.isSuccess && <Text style={styles.successText}>Sent -- check your device.</Text>}
          {testNotificationMutation.isError && (
            <Text style={styles.errorText}>{testNotificationMutation.error.message}</Text>
          )}
        </Card>

        <Card tight style={styles.listCard}>
          <Text style={[styles.sectionLabel, styles.listLabel]}>Active Alerts</Text>
          {!isLoading && (watches || []).length === 0 && <EmptyState title="No alerts yet" />}
          {(watches || []).map((watch) => (
            <View key={watch.id} style={styles.watchRow}>
              <View style={styles.watchInfo}>
                <Text style={styles.watchSymbol}>{watch.symbol}</Text>
                <Text style={styles.watchMeta}>
                  {(strategies || []).find((s) => s.name === watch.strategy_name)?.display_name || watch.strategy_name}
                  {' · '}
                  {INTERVALS.find((o) => o.value === watch.interval)?.label}
                </Text>
              </View>
              <Pressable onPress={() => deleteMutation.mutate(watch.id)} hitSlop={8}>
                <Ionicons name="trash-outline" size={18} color={colors.textTertiary} />
              </Pressable>
            </View>
          ))}
        </Card>
      </ScrollView>

      <StrategyPickerModal
        visible={pickerOpen}
        onClose={() => setPickerOpen(false)}
        strategies={strategies || []}
        onSelect={setStrategyName}
      />
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
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[3],
  },
  strategyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: colors.bgPanelRaised,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    borderRadius: radii.sm,
    paddingVertical: 9,
    paddingHorizontal: spacing[3],
    marginBottom: spacing[3],
  },
  strategyButtonText: {
    fontFamily: fonts.ui,
    fontSize: 14,
    color: colors.textPrimary,
  },
  strategyButtonPlaceholder: {
    fontFamily: fonts.ui,
    fontSize: 14,
    color: colors.textTertiary,
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
  successText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.positive,
    marginTop: spacing[2],
  },
  spacedCard: {
    marginTop: spacing[4],
  },
  hintText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing[3],
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
