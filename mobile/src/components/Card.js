import { View, StyleSheet } from 'react-native'
import { colors, radii, spacing } from '../styles/tokens'

// Ported from frontend/src/components/Card.jsx.
export default function Card({ tight, style, children }) {
  return <View style={[styles.card, tight ? styles.tight : null, style]}>{children}</View>
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.bgPanel,
    borderWidth: 1,
    borderColor: colors.borderHairline,
    borderRadius: radii.lg,
    padding: spacing[6],
  },
  tight: {
    padding: spacing[4],
  },
})
