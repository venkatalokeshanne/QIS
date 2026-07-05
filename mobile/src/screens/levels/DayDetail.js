import { View, Text, StyleSheet } from 'react-native'
import Card from '../../components/Card'
import MetricValue from '../../components/MetricValue'
import LevelRow from './LevelRow'
import { OutcomeBadge, DirectionalBadge } from './OutcomeBadge'
import { colors, fonts, spacing } from '../../styles/tokens'

function DetailLevelRow({ label, outcome }) {
  if (!outcome) {
    return (
      <View style={styles.row}>
        <Text style={styles.rowLabel}>{label}</Text>
        <Text style={styles.noData}>no data</Text>
      </View>
    )
  }
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <View style={styles.rowValue}>
        <MetricValue value={outcome.level} format="currency" />
        <OutcomeBadge outcome={outcome.outcome} />
      </View>
    </View>
  )
}

function DetailDirectionalRow({ label, outcome }) {
  if (!outcome) {
    return (
      <View style={styles.row}>
        <Text style={styles.rowLabel}>{label}</Text>
        <Text style={styles.noData}>no data</Text>
      </View>
    )
  }
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <View style={styles.rowValue}>
        <MetricValue value={outcome.level} format="currency" />
        <DirectionalBadge closedAbove={outcome.closed_above} />
      </View>
    </View>
  )
}

// Ported from DayDetail in frontend/src/pages/DailyLevels.jsx -- the
// web version's wide grid of small cards becomes a stacked column here.
export default function DayDetail({ day }) {
  return (
    <View style={styles.container}>
      <Card style={styles.card}>
        <Text style={styles.sectionLabel}>Session</Text>
        <LevelRow label="Open" value={day.session_open} />
        <LevelRow label="High" value={day.session_high} />
        <LevelRow label="Low" value={day.session_low} />
        <LevelRow label="Close" value={day.session_close} highlight />
        {day.gap_pct !== null && (
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Gap</Text>
            <Text style={day.gap_pct >= 0 ? styles.positive : styles.negative}>
              {day.gap_pct >= 0 ? '+' : ''}
              {day.gap_pct.toFixed(2)}%
            </Text>
          </View>
        )}
      </Card>

      <Card style={styles.card}>
        <Text style={styles.sectionLabel}>Prior Day / Pivot / VWAP</Text>
        <DetailLevelRow label="Prior Day High" outcome={day.prior_day_high} />
        <DetailLevelRow label="Prior Day Low" outcome={day.prior_day_low} />
        <DetailDirectionalRow label="Classic Pivot" outcome={day.pivot_point} />
        <DetailDirectionalRow label="VWAP (EOD)" outcome={day.vwap} />
      </Card>

      <Card style={styles.card}>
        <Text style={styles.sectionLabel}>Pivot Points (Classic)</Text>
        <DetailLevelRow label="R3" outcome={day.pivot_r3} />
        <DetailLevelRow label="R2" outcome={day.pivot_r2} />
        <DetailLevelRow label="R1" outcome={day.pivot_r1} />
        <DetailLevelRow label="S1" outcome={day.pivot_s1} />
        <DetailLevelRow label="S2" outcome={day.pivot_s2} />
        <DetailLevelRow label="S3" outcome={day.pivot_s3} />
      </Card>

      <Card style={styles.card}>
        <Text style={styles.sectionLabel}>Camarilla Pivots</Text>
        <DetailLevelRow label="R4" outcome={day.camarilla_r4} />
        <DetailLevelRow label="R3" outcome={day.camarilla_r3} />
        <DetailLevelRow label="R2" outcome={day.camarilla_r2} />
        <DetailLevelRow label="R1" outcome={day.camarilla_r1} />
        <DetailLevelRow label="S1" outcome={day.camarilla_s1} />
        <DetailLevelRow label="S2" outcome={day.camarilla_s2} />
        <DetailLevelRow label="S3" outcome={day.camarilla_s3} />
        <DetailLevelRow label="S4" outcome={day.camarilla_s4} />
      </Card>

      <Card style={styles.card}>
        <Text style={styles.sectionLabel}>DeMark Pivots</Text>
        <DetailDirectionalRow label="Pivot" outcome={day.demark_pivot} />
        <DetailLevelRow label="Resistance" outcome={day.demark_resistance} />
        <DetailLevelRow label="Support" outcome={day.demark_support} />
      </Card>

      <Card style={styles.card}>
        <Text style={styles.sectionLabel}>Average Daily Range</Text>
        {day.adr ? (
          <>
            <LevelRow label="Expected High" value={day.adr.expected_high} />
            <LevelRow label="ADR" value={day.adr.adr} />
            <LevelRow label="Expected Low" value={day.adr.expected_low} />
            <View style={styles.row}>
              <Text style={styles.rowLabel}>Outcome</Text>
              <OutcomeBadge outcome={day.adr.outcome} />
            </View>
          </>
        ) : (
          <Text style={styles.hint}>Not enough prior sessions yet.</Text>
        )}
      </Card>

      <Card>
        <Text style={styles.sectionLabel}>Opening Range (15 min)</Text>
        {day.opening_range ? (
          <>
            <LevelRow label="High" value={day.opening_range.high} />
            <LevelRow label="Low" value={day.opening_range.low} />
            <View style={styles.row}>
              <Text style={styles.rowLabel}>Outcome</Text>
              <OutcomeBadge outcome={day.opening_range.outcome} />
            </View>
          </>
        ) : (
          <Text style={styles.hint}>No data.</Text>
        )}
      </Card>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing[3],
  },
  card: {
    marginBottom: spacing[3],
  },
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[2],
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing[1],
  },
  rowLabel: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
  },
  rowValue: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[2],
  },
  noData: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textTertiary,
  },
  positive: {
    fontFamily: fonts.mono,
    fontSize: 13,
    color: colors.positive,
  },
  negative: {
    fontFamily: fonts.mono,
    fontSize: 13,
    color: colors.negative,
  },
  hint: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
  },
})
