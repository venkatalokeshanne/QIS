import { View, Text, Pressable, ScrollView, StyleSheet } from 'react-native'
import { colors, fonts, spacing } from '../styles/tokens'

// Generic horizontal-scroll table, standing in for the web app's
// `.data-table` (a plain <table> with CSS-driven horizontal overflow --
// RN has no table element, so this reimplements it as a ScrollView of
// fixed-width columns). Reused for the dataset preview grid here, and
// later for TradesTable / Compare / MonthlyBreakdownTable, per the
// plan's split of dense-data screens into card-stacked vs
// horizontal-scroll based on whether the data is genuinely matrix-shaped.
//
// columns: [{ key, label, width?, mono?: bool }] -- every column is
// center-aligned (per user feedback), so there's no per-column align
// override anymore.
// rows: array of plain objects keyed by column.key
// onRowPress?: (row) => void -- wraps each data row in a Pressable when given
// rowStyle?: (row) => ViewStyle -- extra per-row style (e.g. a win/loss tint)
export default function DataTable({ columns, rows, onRowPress, rowStyle }) {
  const RowWrap = onRowPress ? Pressable : View

  return (
    <ScrollView horizontal showsHorizontalScrollIndicator>
      <View>
        <View style={styles.headerRow}>
          {columns.map((col) => (
            <Text
              key={col.key}
              numberOfLines={1}
              style={[styles.headerCell, { width: col.width ?? 100 }]}
            >
              {col.label}
            </Text>
          ))}
        </View>
        {rows.map((row, i) => (
          <RowWrap
            key={row.id ?? i}
            style={[styles.row, rowStyle ? rowStyle(row) : null]}
            onPress={onRowPress ? () => onRowPress(row) : undefined}
          >
            {columns.map((col) => (
              <Text
                key={col.key}
                numberOfLines={1}
                style={[styles.cell, col.mono ? styles.mono : null, { width: col.width ?? 100 }]}
              >
                {col.render ? col.render(row) : String(row[col.key] ?? '')}
              </Text>
            ))}
          </RowWrap>
        ))}
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  headerRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: colors.borderHairlineStrong,
    paddingBottom: spacing[2],
    marginBottom: spacing[1],
  },
  headerCell: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 11,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    paddingHorizontal: spacing[2],
    textAlign: 'center',
  },
  row: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: colors.borderHairline,
    paddingVertical: spacing[2],
  },
  cell: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textPrimary,
    paddingHorizontal: spacing[2],
    textAlign: 'center',
  },
  mono: {
    fontFamily: fonts.mono,
  },
})
