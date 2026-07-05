import { View, Text, TextInput, ScrollView, Pressable, StyleSheet } from 'react-native'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import { useResearchStore } from '../store/useResearchStore'
import { colors, fonts, radii, spacing } from '../styles/tokens'

const toNullableNumber = (v) => (v === '' ? null : Number(v))

// Ported from frontend/src/pages/Settings.jsx -- same fields, same
// nullable-number semantics ("empty string clears the setting"),
// plain numeric TextInputs (keyboardType="numeric") standing in for
// <input type="number">, a row of Pressable "chips" standing in for
// the <select> direction dropdown (no native picker dependency needed
// for 3 fixed options). Explanatory hint text under each field removed
// per user feedback -- labels + inputs only.
export default function SettingsScreen() {
  const executionSettings = useResearchStore((s) => s.executionSettings)
  const setExecutionSettings = useResearchStore((s) => s.setExecutionSettings)
  const breakdownByMonth = useResearchStore((s) => s.breakdownByMonth)
  const setBreakdownByMonth = useResearchStore((s) => s.setBreakdownByMonth)

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <PageHeader title="Settings" />

      <Card style={styles.spacedCard}>
        <Text style={styles.sectionLabel}>Reporting</Text>
        <Pressable style={styles.checkboxRow} onPress={() => setBreakdownByMonth(!breakdownByMonth)}>
          <View style={[styles.checkbox, breakdownByMonth ? styles.checkboxChecked : null]} />
          <Text style={styles.checkboxLabel}>Monthly breakdown</Text>
        </Pressable>
      </Card>

      <Card style={styles.spacedCard}>
        <Text style={styles.sectionLabel}>Execution</Text>

        <NumberField
          label="Default capital"
          value={executionSettings.capital}
          onChangeValue={(n) => setExecutionSettings({ capital: n })}
        />
        <NumberField
          label="Default quantity per trade"
          value={executionSettings.quantity}
          onChangeValue={(n) => setExecutionSettings({ quantity: n })}
        />
        <NumberField
          label="Default commission per trade"
          value={executionSettings.commission_per_trade}
          onChangeValue={(n) => setExecutionSettings({ commission_per_trade: n })}
        />
        <NumberField
          label="Default slippage (%)"
          value={executionSettings.slippage_pct * 100}
          onChangeValue={(n) => setExecutionSettings({ slippage_pct: (n ?? 0) / 100 })}
        />

        <Text style={styles.fieldLabel}>Trade direction</Text>
        <View style={styles.chipRow}>
          {[
            { value: 'both', label: 'Long & Short' },
            { value: 'long_only', label: 'Long only' },
            { value: 'short_only', label: 'Short only' },
          ].map((opt) => (
            <Pressable
              key={opt.value}
              onPress={() => setExecutionSettings({ direction_filter: opt.value })}
              style={[styles.chip, executionSettings.direction_filter === opt.value ? styles.chipActive : null]}
            >
              <Text
                style={[
                  styles.chipText,
                  executionSettings.direction_filter === opt.value ? styles.chipTextActive : null,
                ]}
              >
                {opt.label}
              </Text>
            </Pressable>
          ))}
        </View>

        <Pressable
          style={styles.checkboxRow}
          onPress={() =>
            setExecutionSettings({ force_close_at_session_end: !executionSettings.force_close_at_session_end })
          }
        >
          <View style={[styles.checkbox, executionSettings.force_close_at_session_end ? styles.checkboxChecked : null]} />
          <Text style={styles.checkboxLabel}>Force close at session end</Text>
        </Pressable>
      </Card>

      <Card>
        <Text style={styles.sectionLabel}>Risk Management</Text>

        <NumberField
          label="ATR Period"
          value={executionSettings.atr_period}
          onChangeValue={(n) => setExecutionSettings({ atr_period: n })}
        />
        <NumberField
          label="Stop Loss (× ATR)"
          value={executionSettings.stop_loss_atr_multiple}
          onChangeValue={(n) => setExecutionSettings({ stop_loss_atr_multiple: n })}
          nullable
        />
        <NumberField
          label="Stop Loss (%)"
          value={executionSettings.stop_loss_pct !== null ? executionSettings.stop_loss_pct * 100 : null}
          onChangeValue={(n) => setExecutionSettings({ stop_loss_pct: n === null ? null : n / 100 })}
          nullable
        />
        <NumberField
          label="Take Profit (× ATR)"
          value={executionSettings.take_profit_atr_multiple}
          onChangeValue={(n) => setExecutionSettings({ take_profit_atr_multiple: n })}
          nullable
        />
        <NumberField
          label="Trailing Stop (× ATR)"
          value={executionSettings.trailing_stop_atr_multiple}
          onChangeValue={(n) => setExecutionSettings({ trailing_stop_atr_multiple: n })}
          nullable
        />
        <NumberField
          label="Risk per trade (%)"
          value={executionSettings.risk_per_trade_pct !== null ? executionSettings.risk_per_trade_pct * 100 : null}
          onChangeValue={(n) => setExecutionSettings({ risk_per_trade_pct: n === null ? null : n / 100 })}
          nullable
        />
      </Card>
    </ScrollView>
  )
}

function NumberField({ label, value, onChangeValue, nullable }) {
  return (
    <View style={styles.fieldGroup}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        placeholder={nullable ? 'Disabled' : undefined}
        placeholderTextColor={colors.textTertiary}
        value={value === null || value === undefined ? '' : String(value)}
        onChangeText={(text) => onChangeValue(toNullableNumber(text))}
      />
    </View>
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
  fieldGroup: {
    marginBottom: spacing[4],
  },
  fieldLabel: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing[1],
  },
  input: {
    fontFamily: fonts.mono,
    fontSize: 14,
    color: colors.textPrimary,
    backgroundColor: colors.bgPanelRaised,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    borderRadius: radii.sm,
    paddingVertical: 9,
    paddingHorizontal: spacing[3],
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
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
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[3],
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
    fontSize: 14,
    color: colors.textPrimary,
  },
})
