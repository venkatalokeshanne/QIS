import { useState } from 'react'
import { View, Text, Pressable, StyleSheet } from 'react-native'
import DateTimePicker from '@react-native-community/datetimepicker'
import { Ionicons } from '@expo/vector-icons'
import Card from '../../components/Card'
import Button from '../../components/Button'
import MetricValue from '../../components/MetricValue'
import { useLevelsDayReports } from '../../api/hooks'
import { formatDate } from '../../utils/format'
import { OutcomeBadge } from './OutcomeBadge'
import DayDetail from './DayDetail'
import { colors, fonts, radii, spacing } from '../../styles/tokens'

function toIsoDate(d) {
  return d.toISOString().slice(0, 10)
}

// Ported from DayByDaySection in frontend/src/pages/DailyLevels.jsx.
// Web's <input type="date"> becomes a real native DateTimePicker
// (compact display); the results table becomes card-stacked with
// tap-to-expand DayDetail, since each row's data is genuinely a report,
// not a matrix column set.
export default function DayByDaySection({ symbol }) {
  const [dateInput, setDateInput] = useState(new Date())
  const [selectedDates, setSelectedDates] = useState([])
  const [expandedDate, setExpandedDate] = useState(null)
  const dayReportsMutation = useLevelsDayReports()

  const addDate = () => {
    const iso = toIsoDate(dateInput)
    setSelectedDates((prev) => (prev.includes(iso) ? prev : [...prev, iso].sort()))
  }

  const removeDate = (date) => {
    setSelectedDates((prev) => prev.filter((d) => d !== date))
  }

  const handleRun = () => {
    if (selectedDates.length === 0) return
    dayReportsMutation.mutate({ symbol, dates: selectedDates })
    setExpandedDate(null)
  }

  const reports = dayReportsMutation.data?.reports || []
  const datesNotFound = dayReportsMutation.data?.dates_not_found || []

  return (
    <Card style={styles.card}>
      <Text style={styles.sectionLabel}>Day-by-Day</Text>

      <View style={styles.dateAddRow}>
        <DateTimePicker
          value={dateInput}
          mode="date"
          display="compact"
          maximumDate={new Date()}
          onChange={(_, date) => date && setDateInput(date)}
          themeVariant="dark"
          accentColor={colors.accent}
        />
        <Pressable onPress={addDate} style={styles.addDateButton} hitSlop={8}>
          <Ionicons name="add" size={18} color={colors.accent} />
        </Pressable>
      </View>

      {selectedDates.length > 0 && (
        <View style={styles.chipRow}>
          {selectedDates.map((date) => (
            <View key={date} style={styles.dateChip}>
              <Text style={styles.dateChipText}>{formatDate(date)}</Text>
              <Pressable onPress={() => removeDate(date)} hitSlop={6}>
                <Ionicons name="close" size={12} color={colors.accent} />
              </Pressable>
            </View>
          ))}
        </View>
      )}

      <Button
        variant="primary"
        onPress={handleRun}
        disabled={selectedDates.length === 0 || dayReportsMutation.isPending}
        style={styles.actionsRow}
      >
        {dayReportsMutation.isPending ? 'Fetching…' : `Get Reports (${selectedDates.length})`}
      </Button>

      {dayReportsMutation.isError && <Text style={styles.errorText}>{dayReportsMutation.error.message}</Text>}

      {datesNotFound.length > 0 && (
        <Text style={styles.hint}>
          No data for: {datesNotFound.map((d) => formatDate(d)).join(', ')} -- outside the freshest fetched window or
          not a trading day.
        </Text>
      )}

      {reports.map((day) => {
        const expanded = expandedDate === day.date
        return (
          <View key={day.date} style={styles.dayCard}>
            <Pressable onPress={() => setExpandedDate(expanded ? null : day.date)} style={styles.dayRow}>
              <View>
                <Text style={styles.dayDate}>{formatDate(day.date)}</Text>
                <View style={styles.dayMetaRow}>
                  <MetricValue value={day.session_open} format="currency" style={styles.dayMeta} />
                  <Text style={styles.dayMetaArrow}>→</Text>
                  <MetricValue value={day.session_close} format="currency" style={styles.dayMeta} />
                  {day.gap_pct !== null && (
                    <Text style={styles.dayMeta}>
                      {' '}
                      ({day.gap_pct >= 0 ? '+' : ''}
                      {day.gap_pct.toFixed(2)}%)
                    </Text>
                  )}
                </View>
                <Text style={styles.dayCounts}>
                  {day.levels_touched_count} touched · {day.levels_held_count} held · {day.levels_broken_count} broken
                </Text>
              </View>
              <View style={styles.dayBadges}>
                {day.adr ? <OutcomeBadge outcome={day.adr.outcome} /> : null}
                {day.opening_range ? <OutcomeBadge outcome={day.opening_range.outcome} /> : null}
              </View>
            </Pressable>
            {expanded && <DayDetail day={day} />}
          </View>
        )
      })}
    </Card>
  )
}

const styles = StyleSheet.create({
  card: {
    marginTop: spacing[4],
  },
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[2],
  },
  hint: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing[3],
  },
  dateAddRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[3],
  },
  addDateButton: {
    width: 32,
    height: 32,
    borderRadius: radii.sm,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    backgroundColor: colors.bgPanelRaised,
    alignItems: 'center',
    justifyContent: 'center',
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[2],
    marginTop: spacing[3],
  },
  dateChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 6,
    paddingHorizontal: spacing[3],
    borderRadius: radii.sm,
    backgroundColor: colors.accentWash,
    borderWidth: 1,
    borderColor: colors.accent,
  },
  dateChipText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.accent,
  },
  actionsRow: {
    marginTop: spacing[4],
    alignSelf: 'flex-start',
  },
  errorText: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.negative,
    marginTop: spacing[3],
  },
  dayCard: {
    marginTop: spacing[4],
    paddingTop: spacing[3],
    borderTopWidth: 1,
    borderTopColor: colors.borderHairline,
  },
  dayRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  dayDate: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 14,
    color: colors.textPrimary,
  },
  dayMetaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 2,
  },
  dayMeta: {
    fontSize: 12,
  },
  dayMetaArrow: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textTertiary,
  },
  dayCounts: {
    fontFamily: fonts.ui,
    fontSize: 11,
    color: colors.textTertiary,
    marginTop: 2,
  },
  dayBadges: {
    flexDirection: 'row',
    gap: spacing[2],
  },
})
