import { useState } from 'react'
import { View, TextInput, ScrollView, StyleSheet } from 'react-native'
import Card from '../../components/Card'
import DayByDaySection from './DayByDaySection'
import { colors, fonts, radii, spacing } from '../../styles/tokens'

// Simplified per user feedback: pick a ticker, pick date(s), one "Get
// Reports" button -- the aggregate hit-rate stats (Run Backtest) were
// dropped entirely, this screen is now just a symbol input feeding
// straight into the day-by-day report flow.
export default function BacktestLevelsTab() {
  const [symbolInput, setSymbolInput] = useState('')
  const symbol = symbolInput.trim().toUpperCase()

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Card>
        <View style={styles.searchRow}>
          <TextInput
            style={styles.input}
            placeholder="Symbol (e.g. AAPL)"
            placeholderTextColor={colors.textTertiary}
            autoCapitalize="characters"
            value={symbolInput}
            onChangeText={setSymbolInput}
          />
        </View>
      </Card>

      {symbol && <DayByDaySection symbol={symbol} />}
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.bgBase,
  },
  content: {
    padding: spacing[4],
  },
  searchRow: {
    flexDirection: 'row',
    gap: spacing[2],
  },
  input: {
    flex: 1,
    fontFamily: fonts.mono,
    fontSize: 14,
    color: colors.textPrimary,
    backgroundColor: colors.bgPanelRaised,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    borderRadius: radii.sm,
    paddingVertical: 9,
    paddingHorizontal: spacing[3],
  },
})
