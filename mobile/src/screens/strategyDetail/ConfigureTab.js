import { View, Text, TextInput, ScrollView, Pressable, StyleSheet } from 'react-native'
import Card from '../../components/Card'
import Button from '../../components/Button'
import { useStrategyDetail } from './StrategyDetailContext'
import { colors, fonts, radii, spacing } from '../../styles/tokens'

// Ported from the "configure" tab of frontend/src/pages/StrategyDetail.jsx
// (its renderParamInput switch). Direction becomes a chip row (no
// native <select> in RN), boolean becomes a toggle Pressable, array
// becomes a comma-separated text input matching the web version's own
// comma-parsing behavior, number/string are plain TextInputs.
export default function ConfigureTab() {
  const { strategy, effectiveParams, paramsOverride, hasOverride, setStrategyParamOverride, resetStrategyParams, name } =
    useStrategyDetail()

  if (!strategy) return null

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Card>
        <View style={styles.headerRow}>
          <Text style={styles.sectionLabel}>Parameters</Text>
          <Button size="sm" variant="ghost" onPress={() => resetStrategyParams(name)} disabled={!hasOverride}>
            Reset to Defaults
          </Button>
        </View>

        {Object.entries(strategy.default_params).map(([key, defaultValue]) => (
          <View key={key} style={styles.fieldGroup}>
            <Text style={styles.fieldLabel}>{key}</Text>
            <ParamInput
              paramKey={key}
              value={effectiveParams[key]}
              onChange={(value) => setStrategyParamOverride(name, key, value)}
            />
            {paramsOverride[key] !== undefined && <Text style={styles.defaultHint}>Default: {String(defaultValue)}</Text>}
          </View>
        ))}
      </Card>
    </ScrollView>
  )
}

function ParamInput({ paramKey, value, onChange }) {
  if (paramKey === 'direction') {
    const options = [
      { value: 'both', label: 'Long & Short' },
      { value: 'long_only', label: 'Long only' },
      { value: 'short_only', label: 'Short only' },
    ]
    return (
      <View style={styles.chipRow}>
        {options.map((opt) => (
          <Pressable
            key={opt.value}
            onPress={() => onChange(opt.value)}
            style={[styles.chip, value === opt.value ? styles.chipActive : null]}
          >
            <Text style={[styles.chipText, value === opt.value ? styles.chipTextActive : null]}>{opt.label}</Text>
          </Pressable>
        ))}
      </View>
    )
  }

  if (typeof value === 'boolean') {
    return (
      <Pressable style={styles.checkboxRow} onPress={() => onChange(!value)}>
        <View style={[styles.checkbox, value ? styles.checkboxChecked : null]} />
        <Text style={styles.checkboxLabel}>{value ? 'Enabled' : 'Disabled'}</Text>
      </Pressable>
    )
  }

  if (Array.isArray(value)) {
    return (
      <TextInput
        style={[styles.input, styles.mono]}
        value={value.join(', ')}
        onChangeText={(text) =>
          onChange(
            text
              .split(',')
              .map((s) => Number(s.trim()))
              .filter((n) => !Number.isNaN(n))
          )
        }
      />
    )
  }

  if (typeof value === 'number') {
    return (
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        value={String(value)}
        onChangeText={(text) => onChange(text === '' ? 0 : Number(text))}
      />
    )
  }

  return <TextInput style={styles.input} value={value} onChangeText={onChange} />
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.bgBase,
  },
  content: {
    padding: spacing[4],
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
  },
  fieldGroup: {
    marginBottom: spacing[4],
  },
  fieldLabel: {
    fontFamily: fonts.mono,
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing[1],
  },
  defaultHint: {
    fontFamily: fonts.ui,
    fontSize: 11,
    color: colors.textTertiary,
    marginTop: spacing[1],
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
  },
  mono: {
    fontFamily: fonts.mono,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
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
