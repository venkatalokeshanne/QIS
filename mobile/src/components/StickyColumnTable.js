import { View, Text, ScrollView, StyleSheet } from 'react-native'
import { colors, fonts, spacing } from '../styles/tokens'

const ROW_HEIGHT = 40
const STICKY_WIDTH = 140
const COL_WIDTH = 100

// RN has no CSS `position: sticky`, so a pinned first column is built
// as two side-by-side, independently-non-scrolling Views inside one
// row: a fixed-width label column on the left, and a horizontal
// ScrollView with the data columns on the right. Both share the same
// fixed ROW_HEIGHT per row so they stay visually aligned; the parent
// screen's own vertical ScrollView carries both together.
//
// columns: [{ key, label }]
// rows: [{ label, cells: { [columnKey]: { text, best? } } }]
export default function StickyColumnTable({ columns, rows }) {
  return (
    <View style={styles.wrap}>
      <View style={styles.stickyCol}>
        <View style={styles.headerCell}>
          <Text style={styles.headerText}>Metric</Text>
        </View>
        {rows.map((row, i) => (
          <View key={i} style={styles.stickyCell}>
            <Text style={styles.stickyLabel} numberOfLines={2}>
              {row.label}
            </Text>
          </View>
        ))}
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator>
        <View>
          <View style={styles.headerRow}>
            {columns.map((col) => (
              <View key={col.key} style={[styles.headerCell, { width: COL_WIDTH }]}>
                <Text style={styles.headerText} numberOfLines={2}>
                  {col.label}
                </Text>
              </View>
            ))}
          </View>
          {rows.map((row, i) => (
            <View key={i} style={styles.dataRow}>
              {columns.map((col) => {
                const cell = row.cells[col.key] || {}
                return (
                  <View key={col.key} style={[styles.dataCell, { width: COL_WIDTH }]}>
                    <Text style={[styles.dataText, cell.best ? styles.bestText : null]}>{cell.text ?? '—'}</Text>
                  </View>
                )
              })}
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: 'row',
  },
  stickyCol: {
    width: STICKY_WIDTH,
    borderRightWidth: 1,
    borderRightColor: colors.borderHairlineStrong,
  },
  headerRow: {
    flexDirection: 'row',
  },
  headerCell: {
    height: ROW_HEIGHT,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing[2],
    borderBottomWidth: 1,
    borderBottomColor: colors.borderHairlineStrong,
  },
  headerText: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  stickyCell: {
    height: ROW_HEIGHT,
    justifyContent: 'center',
    paddingHorizontal: spacing[2],
    borderBottomWidth: 1,
    borderBottomColor: colors.borderHairline,
  },
  stickyLabel: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 12,
    color: colors.textPrimary,
  },
  dataRow: {
    flexDirection: 'row',
  },
  dataCell: {
    height: ROW_HEIGHT,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing[2],
    borderBottomWidth: 1,
    borderBottomColor: colors.borderHairline,
  },
  dataText: {
    fontFamily: fonts.mono,
    fontSize: 13,
    color: colors.textPrimary,
    textAlign: 'center',
  },
  bestText: {
    color: colors.accent,
    fontFamily: fonts.monoMedium,
  },
})
