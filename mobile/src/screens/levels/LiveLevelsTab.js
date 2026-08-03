import { useState } from 'react'
import { View, Text, TextInput, ScrollView, Pressable, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import Card from '../../components/Card'
import Button from '../../components/Button'
import MetricValue from '../../components/MetricValue'
import { useDailyLevels } from '../../api/hooks'
import { formatDateTime } from '../../utils/format'
import LevelRow from './LevelRow'
import { colors, fonts, radii, spacing } from '../../styles/tokens'

const SIGNAL_META = {
  buy: { label: 'BUY', color: colors.positive, wash: colors.positiveWash },
  sell: { label: 'SELL', color: colors.negative, wash: colors.negativeWash },
  neutral: { label: 'NEUTRAL', color: colors.textSecondary, wash: colors.bgPanelRaised },
}

// Ported from LiveLevelsTab in frontend/src/pages/DailyLevels.jsx --
// each level-type group stays its own Card (already card-stacked on
// web too), just laid out in a single column instead of a wide grid.
export default function LiveLevelsTab() {
  const [symbolInput, setSymbolInput] = useState('')
  const [reasonsOpen, setReasonsOpen] = useState(false)
  const levelsMutation = useDailyLevels()
  const levels = levelsMutation.data

  const handleSubmit = () => {
    const symbol = symbolInput.trim().toUpperCase()
    if (!symbol) return
    levelsMutation.mutate(symbol)
  }

  const srBelow = levels ? levels.auto_support_resistance.filter((v) => v < levels.current_price).reverse() : []
  const srAbove = levels ? levels.auto_support_resistance.filter((v) => v >= levels.current_price) : []

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Card>
        <View style={styles.searchRow}>
          <TextInput
            style={styles.input}
            placeholder="Symbol (e.g. AAPL)"
            placeholderTextColor={colors.textTertiary}
            autoCapitalize="characters"
            value={symbolInput}
            onChangeText={setSymbolInput}
            onSubmitEditing={handleSubmit}
          />
          <Button variant="primary" onPress={handleSubmit} disabled={levelsMutation.isPending || !symbolInput.trim()}>
            {levelsMutation.isPending ? 'Loading…' : 'Get Levels'}
          </Button>
        </View>
        {levelsMutation.isError && <Text style={styles.errorText}>{levelsMutation.error.message}</Text>}
      </Card>

      {levels && (
        <>
          <Card style={styles.spacedCard}>
            <View style={styles.headerRow}>
              <View>
                <Text style={styles.symbol}>{levels.symbol}</Text>
                <Text style={styles.hint}>Data as of {formatDateTime(levels.as_of)}</Text>
              </View>
              <View style={styles.priceBlock}>
                <MetricValue value={levels.current_price} format="currency" style={styles.currentPrice} />
                <Text style={levels.gap_pct >= 0 ? styles.gapPositive : styles.gapNegative}>
                  Gap {levels.gap_pct >= 0 ? '+' : ''}
                  {levels.gap_pct.toFixed(2)}% vs prior close
                </Text>
              </View>
            </View>
          </Card>

          <Card style={styles.spacedCard}>
            <Pressable style={styles.signalRow} onPress={() => setReasonsOpen((open) => !open)}>
              <View style={[styles.signalBadge, { backgroundColor: SIGNAL_META[levels.signal].wash }]}>
                <Text style={[styles.signalBadgeText, { color: SIGNAL_META[levels.signal].color }]}>
                  {SIGNAL_META[levels.signal].label}
                </Text>
              </View>
              <Text style={styles.signalHint}>Why?</Text>
              <Ionicons
                name={reasonsOpen ? 'chevron-up' : 'information-circle-outline'}
                size={18}
                color={colors.textSecondary}
              />
            </Pressable>
            {reasonsOpen && (
              <View style={styles.reasonsList}>
                {levels.signal_reasons.length === 0 ? (
                  <Text style={styles.reasonItem}>Nothing lines up strongly enough for a directional read right now.</Text>
                ) : (
                  levels.signal_reasons.map((reason, i) => (
                    <Text key={i} style={styles.reasonItem}>
                      • {reason}
                    </Text>
                  ))
                )}
                <Text style={styles.signalCaveat}>
                  A confluence heuristic across today's levels -- not a guaranteed prediction. Always confirm with
                  price action before acting.
                </Text>
              </View>
            )}
          </Card>

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>Prior Session</Text>
            <LevelRow label="High" value={levels.prior_high} />
            <LevelRow label="Close" value={levels.prior_close} />
            <LevelRow label="Low" value={levels.prior_low} />
          </Card>

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>Today</Text>
            <LevelRow label="Open" value={levels.session_open} />
            <LevelRow label="VWAP" value={levels.vwap} highlight />
            <LevelRow label="Opening Range High" value={levels.opening_range_high} />
            <LevelRow label="Opening Range Low" value={levels.opening_range_low} />
          </Card>

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>Average Daily Range (14)</Text>
            <LevelRow label="Expected High" value={levels.adr_expected_high} />
            <LevelRow label="ADR" value={levels.adr} />
            <LevelRow label="Expected Low" value={levels.adr_expected_low} />
          </Card>

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>Pivot Points (Classic)</Text>
            <LevelRow label="R3" value={levels.pivot_points.r3} />
            <LevelRow label="R2" value={levels.pivot_points.r2} />
            <LevelRow label="R1" value={levels.pivot_points.r1} />
            <LevelRow label="Pivot" value={levels.pivot_points.pivot} highlight />
            <LevelRow label="S1" value={levels.pivot_points.s1} />
            <LevelRow label="S2" value={levels.pivot_points.s2} />
            <LevelRow label="S3" value={levels.pivot_points.s3} />
          </Card>

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>Camarilla Pivots</Text>
            <LevelRow label="R4" value={levels.camarilla_pivots.r4} />
            <LevelRow label="R3" value={levels.camarilla_pivots.r3} />
            <LevelRow label="R2" value={levels.camarilla_pivots.r2} />
            <LevelRow label="R1" value={levels.camarilla_pivots.r1} />
            <LevelRow label="S1" value={levels.camarilla_pivots.s1} />
            <LevelRow label="S2" value={levels.camarilla_pivots.s2} />
            <LevelRow label="S3" value={levels.camarilla_pivots.s3} />
            <LevelRow label="S4" value={levels.camarilla_pivots.s4} />
          </Card>

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>DeMark Pivots</Text>
            <LevelRow label="Resistance" value={levels.demark_pivots.resistance} />
            <LevelRow label="Pivot" value={levels.demark_pivots.pivot} highlight />
            <LevelRow label="Support" value={levels.demark_pivots.support} />
          </Card>

          <Card style={styles.spacedCard}>
            <Text style={styles.sectionLabel}>Auto Support / Resistance</Text>
            {srAbove.length === 0 && srBelow.length === 0 ? (
              <Text style={styles.hint}>Not enough swing history yet.</Text>
            ) : (
              <>
                {srAbove.map((v, i) => (
                  <LevelRow key={`above-${i}`} label="Resistance" value={v} />
                ))}
                {srBelow.map((v, i) => (
                  <LevelRow key={`below-${i}`} label="Support" value={v} />
                ))}
              </>
            )}
          </Card>

          <Card>
            <Text style={styles.sectionLabel}>Fibonacci Retracement (50-bar swing)</Text>
            <LevelRow label="23.6%" value={levels.fibonacci_retracement['236']} />
            <LevelRow label="38.2%" value={levels.fibonacci_retracement['382']} />
            <LevelRow label="50%" value={levels.fibonacci_retracement['50']} />
            <LevelRow label="61.8%" value={levels.fibonacci_retracement['618']} />
            <LevelRow label="78.6%" value={levels.fibonacci_retracement['786']} />
          </Card>
        </>
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
  searchRow: {
    flexDirection: 'row',
    gap: spacing[2],
  },
  input: {
    flex: 1,
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
  errorText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.negative,
    marginTop: spacing[3],
  },
  spacedCard: {
    marginTop: spacing[4],
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  symbol: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 18,
    color: colors.textPrimary,
  },
  hint: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2,
  },
  priceBlock: {
    alignItems: 'flex-end',
  },
  currentPrice: {
    fontSize: 18,
  },
  gapPositive: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.positive,
    marginTop: 2,
  },
  gapNegative: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.negative,
    marginTop: 2,
  },
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[2],
  },
  signalRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[3],
  },
  signalBadge: {
    paddingVertical: 6,
    paddingHorizontal: spacing[3],
    borderRadius: radii.sm,
  },
  signalBadgeText: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 13,
    letterSpacing: 0.5,
  },
  signalHint: {
    flex: 1,
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
  },
  reasonsList: {
    marginTop: spacing[3],
    paddingTop: spacing[3],
    borderTopWidth: 1,
    borderTopColor: colors.borderHairline,
  },
  reasonItem: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textPrimary,
    marginBottom: spacing[2],
    lineHeight: 19,
  },
  signalCaveat: {
    fontFamily: fonts.ui,
    fontSize: 11,
    color: colors.textTertiary,
    marginTop: spacing[1],
    fontStyle: 'italic',
  },
})
