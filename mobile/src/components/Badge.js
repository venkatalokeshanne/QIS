import { View, Text, StyleSheet } from 'react-native'
import { colors, fonts, radii, spacing } from '../styles/tokens'

// Ported from frontend/src/components/Badge.jsx.
export default function Badge({ accent, children }) {
  return (
    <View style={[styles.badge, accent ? styles.accent : null]}>
      <Text style={[styles.text, accent ? styles.accentText : null]}>{children}</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  badge: {
    alignSelf: 'flex-start',
    paddingVertical: 3,
    paddingHorizontal: spacing[2],
    borderRadius: radii.sm,
    backgroundColor: colors.bgPanelRaised,
  },
  accent: {
    backgroundColor: colors.accentWash,
  },
  text: {
    fontFamily: fonts.ui,
    fontSize: 11,
    color: colors.textSecondary,
    textTransform: 'capitalize',
  },
  accentText: {
    color: colors.accent,
  },
})
