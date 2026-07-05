import { View, Text, FlatList, Modal, Pressable, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { colors, fonts, radii, spacing } from '../styles/tokens'

// Multi-select strategy picker: "All Strategies" (tapping it clears
// the selection back to the store's "run all" convention -- an empty
// array -- and closes the modal, since it's a reset action) plus a
// checkbox per individual strategy (toggling stays open so several can
// be picked in one visit). The small info icon per row jumps to that
// strategy's full detail without changing the current selection.
export default function StrategySelectModal({ visible, onClose, strategies, selectedNames, onToggle, onSelectAll, onViewDetail }) {
  const runAll = selectedNames.length === 0

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable style={styles.panel} onPress={(e) => e.stopPropagation()}>
          <View style={styles.headerRow}>
            <Text style={styles.title}>Choose strategies</Text>
            <Pressable onPress={onClose} hitSlop={8}>
              <Ionicons name="close" size={22} color={colors.textSecondary} />
            </Pressable>
          </View>

          <Pressable style={styles.row} onPress={onSelectAll}>
            <View style={[styles.checkbox, runAll ? styles.checkboxChecked : null]} />
            <View style={styles.rowText}>
              <Text style={styles.rowName}>All Strategies</Text>
            </View>
          </Pressable>

          <FlatList
            data={strategies}
            keyExtractor={(s) => s.name}
            renderItem={({ item: s }) => {
              const checked = selectedNames.includes(s.name)
              return (
                <View style={[styles.row, styles.rowBordered]}>
                  <Pressable style={styles.rowMain} onPress={() => onToggle(s.name)}>
                    <View style={[styles.checkbox, checked ? styles.checkboxChecked : null]} />
                    <View style={styles.rowText}>
                      <Text style={styles.rowName}>{s.display_name}</Text>
                      <Text style={styles.rowDesc} numberOfLines={2}>
                        {s.description}
                      </Text>
                    </View>
                  </Pressable>
                  <Pressable
                    onPress={() => {
                      onClose()
                      onViewDetail(s.name)
                    }}
                    hitSlop={8}
                    style={styles.infoButton}
                  >
                    <Ionicons name="information-circle-outline" size={20} color={colors.textSecondary} />
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
    maxHeight: '80%',
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
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing[3],
  },
  rowBordered: {
    borderTopWidth: 1,
    borderTopColor: colors.borderHairline,
  },
  rowMain: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing[3],
    flex: 1,
  },
  checkbox: {
    width: 18,
    height: 18,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    marginTop: 2,
  },
  checkboxChecked: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  rowText: {
    flex: 1,
  },
  rowName: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 14,
    color: colors.textPrimary,
  },
  rowDesc: {
    fontFamily: fonts.ui,
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2,
  },
  infoButton: {
    paddingLeft: spacing[2],
  },
})
