import { View, Text, StyleSheet } from 'react-native'
import { colors, fonts, spacing } from '../styles/tokens'

// Ported from frontend/src/components/EmptyState.jsx.
export default function EmptyState({ title, body, action }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      {body ? <Text style={styles.body}>{body}</Text> : null}
      {action}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    paddingVertical: spacing[12],
    paddingHorizontal: spacing[6],
  },
  title: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 15,
    color: colors.textPrimary,
    marginBottom: spacing[2],
  },
  body: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textSecondary,
    textAlign: 'center',
    maxWidth: 320,
    marginBottom: spacing[5],
  },
})
