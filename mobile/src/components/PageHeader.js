import { View, Text, StyleSheet } from 'react-native'
import { colors, fonts, spacing } from '../styles/tokens'

// Ported from frontend/src/components/PageHeader.jsx. `actions` on web
// sits inline to the right of the title (desktop-width row); on a
// phone-width screen there's rarely room for that, so actions render
// as their own row below the subtitle instead of fighting for
// horizontal space.
export default function PageHeader({ title, subtitle, actions }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      {actions ? <View style={styles.actions}>{actions}</View> : null}
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing[6],
  },
  title: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 22,
    color: colors.textPrimary,
  },
  subtitle: {
    marginTop: spacing[1],
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textSecondary,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing[2],
    marginTop: spacing[4],
  },
})
