import { View, Text, FlatList, Modal, Pressable, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { colors, fonts, radii, spacing } from '../styles/tokens'

// Single-select strategy picker (unlike StrategySelectModal's
// multi-select "run a batch" picker) -- tapping a row both selects it
// and closes the modal, since choosing which one strategy an alert
// watches is a single decision, not a running selection.
export default function StrategyPickerModal({ visible, onClose, strategies, onSelect }) {
  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable style={styles.panel} onPress={(e) => e.stopPropagation()}>
          <View style={styles.headerRow}>
            <Text style={styles.title}>Choose strategy</Text>
            <Pressable onPress={onClose} hitSlop={8}>
              <Ionicons name="close" size={22} color={colors.textSecondary} />
            </Pressable>
          </View>

          <FlatList
            data={strategies}
            keyExtractor={(s) => s.name}
            renderItem={({ item: s, index }) => (
              <Pressable
                style={[styles.row, index > 0 ? styles.rowBordered : null]}
                onPress={() => {
                  onSelect(s.name)
                  onClose()
                }}
              >
                <Text style={styles.rowName}>{s.display_name}</Text>
                <Text style={styles.rowDesc} numberOfLines={2}>
                  {s.description}
                </Text>
              </Pressable>
            )}
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
    paddingVertical: spacing[3],
  },
  rowBordered: {
    borderTopWidth: 1,
    borderTopColor: colors.borderHairline,
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
})
