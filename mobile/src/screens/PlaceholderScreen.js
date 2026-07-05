import { StyleSheet, Text, View } from 'react-native'
import { colors, fonts } from '../styles/tokens'

// Temporary stand-in for screens not yet built past Phase 1 -- confirms
// navigation/theming works before any real screen content exists.
export default function PlaceholderScreen({ route }) {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>{route.name}</Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgBase,
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    color: colors.textPrimary,
    fontFamily: fonts.uiSemiBold,
    fontSize: 18,
  },
})
