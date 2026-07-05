import { useState } from 'react'
import { View, Text, TextInput, FlatList, Modal, Pressable, StyleSheet } from 'react-native'
import DateTimePicker from '@react-native-community/datetimepicker'
import { Ionicons } from '@expo/vector-icons'
import Button from './Button'
import { useDatasets, useFetchFromTwelvedata, useDeleteDataset } from '../api/hooks'
import { useResearchStore } from '../store/useResearchStore'
import { colors, fonts, radii, spacing } from '../styles/tokens'

const INTERVAL_PRESETS = [
  { label: '1m', value: '1min' },
  { label: '5m', value: '5min' },
  { label: '15m', value: '15min' },
  { label: '1h', value: '1h' },
  { label: '1D', value: '1day' },
]

const DURATION_PRESETS = [
  { label: '1D', value: '1D' },
  { label: '5D', value: '5D' },
  { label: '1M', value: '1M' },
  { label: '3M', value: '3M' },
  { label: '6M', value: '6M' },
  { label: '1Y', value: '1Y' },
]

function toIsoDate(d) {
  return d.toISOString().slice(0, 10)
}

// Consolidates the web app's separate Upload/TwelvedataFetchMenu/
// TickerMultiSelect/Datasets pages into one modal, triggered by a
// small icon on the Run Backtests screen -- mobile only supports
// fetching live data from Twelve Data (no CSV upload; picking a file
// on a phone is awkward and this app's real workflow is "pull live
// data, then backtest it"). Closes via the header's X, not a
// competing second primary button.
export default function DataPickerModal({ visible, onClose }) {
  const [symbol, setSymbol] = useState('')
  const [interval, setInterval_] = useState('1min')
  const [duration, setDuration] = useState('1M')
  const [rangeMode, setRangeMode] = useState('duration')
  const [startDate, setStartDate] = useState(null)
  const [endDate, setEndDate] = useState(null)

  const { data: datasets } = useDatasets()
  const selectedDatasetIds = useResearchStore((s) => s.selectedDatasetIds)
  const toggleDatasetId = useResearchStore((s) => s.toggleDatasetId)
  const addSelectedDatasetId = useResearchStore((s) => s.addSelectedDatasetId)
  const fetchMutation = useFetchFromTwelvedata()
  const deleteMutation = useDeleteDataset()

  const onFetch = () => {
    const trimmed = symbol.trim().toUpperCase()
    if (!trimmed) return
    if (rangeMode === 'custom' && !startDate) return

    const payload =
      rangeMode === 'custom'
        ? {
            symbol: trimmed,
            interval,
            duration: null,
            start_date: toIsoDate(startDate),
            end_date: endDate ? toIsoDate(endDate) : null,
            name: null,
          }
        : { symbol: trimmed, interval, duration, name: null }

    fetchMutation.mutate(payload, {
      onSuccess: (data) => {
        addSelectedDatasetId(data.dataset.id)
        setSymbol('')
      },
    })
  }

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable style={styles.panel} onPress={(e) => e.stopPropagation()}>
          <View style={styles.headerRow}>
            <Text style={styles.title}>Choose data</Text>
            <Pressable onPress={onClose} hitSlop={8}>
              <Ionicons name="close" size={22} color={colors.textSecondary} />
            </Pressable>
          </View>

          <Text style={styles.sectionLabel}>Fetch from Twelve Data</Text>
          <TextInput
            style={styles.input}
            placeholder="Symbol, e.g. AAPL"
            placeholderTextColor={colors.textTertiary}
            autoCapitalize="characters"
            value={symbol}
            onChangeText={setSymbol}
          />

          <View style={styles.chipRow}>
            {INTERVAL_PRESETS.map((p) => (
              <Chip key={p.value} label={p.label} active={interval === p.value} onPress={() => setInterval_(p.value)} />
            ))}
          </View>

          <View style={styles.chipRow}>
            <Chip label="Quick range" active={rangeMode === 'duration'} onPress={() => setRangeMode('duration')} />
            <Chip label="Custom dates" active={rangeMode === 'custom'} onPress={() => setRangeMode('custom')} />
          </View>

          {rangeMode === 'duration' ? (
            <View style={styles.chipRow}>
              {DURATION_PRESETS.map((p) => (
                <Chip key={p.value} label={p.label} active={duration === p.value} onPress={() => setDuration(p.value)} />
              ))}
            </View>
          ) : (
            <View style={styles.dateRow}>
              <View style={styles.dateField}>
                <Text style={styles.label}>Start date</Text>
                <DateTimePicker
                  value={startDate || new Date()}
                  mode="date"
                  display="compact"
                  maximumDate={new Date()}
                  onChange={(_, date) => date && setStartDate(date)}
                  themeVariant="dark"
                  accentColor={colors.accent}
                />
              </View>
              <View style={styles.dateField}>
                <Text style={styles.label}>End date (optional)</Text>
                <DateTimePicker
                  value={endDate || new Date()}
                  mode="date"
                  display="compact"
                  maximumDate={new Date()}
                  onChange={(_, date) => date && setEndDate(date)}
                  themeVariant="dark"
                  accentColor={colors.accent}
                />
              </View>
            </View>
          )}

          {fetchMutation.isError ? <Text style={styles.errorText}>{fetchMutation.error.message}</Text> : null}

          <Button
            variant="primary"
            size="sm"
            onPress={onFetch}
            disabled={fetchMutation.isPending || !symbol.trim() || (rangeMode === 'custom' && !startDate)}
            style={styles.fetchButton}
          >
            {fetchMutation.isPending ? 'Fetching…' : 'Fetch & Select'}
          </Button>

          <Text style={[styles.sectionLabel, styles.datasetsSectionLabel]}>Your datasets</Text>
          <FlatList
            style={styles.list}
            data={datasets || []}
            keyExtractor={(d) => d.id}
            ListEmptyComponent={<Text style={styles.emptyText}>Nothing fetched yet.</Text>}
            renderItem={({ item: d }) => {
              const checked = selectedDatasetIds.includes(d.id)
              return (
                <View style={styles.item}>
                  <Pressable style={styles.itemMain} onPress={() => toggleDatasetId(d.id)}>
                    <View style={[styles.checkbox, checked ? styles.checkboxChecked : null]} />
                    <View>
                      <Text style={styles.itemName}>{d.name}</Text>
                      <Text style={styles.itemRows}>{d.row_count.toLocaleString()} rows</Text>
                    </View>
                  </Pressable>
                  <Pressable onPress={() => deleteMutation.mutate(d.id)} hitSlop={8}>
                    <Ionicons name="trash-outline" size={16} color={colors.negative} />
                  </Pressable>
                </View>
              )
            }}
          />
        </Pressable>
      </Pressable>
    </Modal>
  )
}

function Chip({ label, active, onPress }) {
  return (
    <Pressable onPress={onPress} style={[styles.chip, active ? styles.chipActive : null]}>
      <Text style={[styles.chipText, active ? styles.chipTextActive : null]}>{label}</Text>
    </Pressable>
  )
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'flex-end',
  },
  panel: {
    backgroundColor: colors.bgPanel,
    borderTopLeftRadius: radii.lg,
    borderTopRightRadius: radii.lg,
    padding: spacing[6],
    maxHeight: '85%',
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing[4],
  },
  title: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 15,
    color: colors.textPrimary,
  },
  sectionLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textTertiary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    marginBottom: spacing[2],
  },
  datasetsSectionLabel: {
    marginTop: spacing[5],
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
    marginBottom: spacing[3],
  },
  label: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: spacing[1],
  },
  dateRow: {
    flexDirection: 'row',
    gap: spacing[4],
    marginBottom: spacing[3],
  },
  dateField: {
    flex: 1,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[2],
    marginBottom: spacing[3],
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
    marginBottom: spacing[2],
  },
  fetchButton: {
    alignSelf: 'flex-start',
  },
  list: {
    marginTop: spacing[2],
    maxHeight: 220,
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing[3],
    borderBottomWidth: 1,
    borderBottomColor: colors.borderHairline,
  },
  itemMain: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[3],
    flex: 1,
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
  itemName: {
    fontFamily: fonts.ui,
    fontSize: 14,
    color: colors.textPrimary,
  },
  itemRows: {
    fontFamily: fonts.mono,
    fontSize: 11,
    color: colors.textSecondary,
    marginTop: 2,
  },
  emptyText: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textSecondary,
    paddingVertical: spacing[4],
    textAlign: 'center',
  },
})
