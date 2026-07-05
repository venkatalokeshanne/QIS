import { useState } from 'react'
import { View, Text, Pressable, StyleSheet } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import LiveLevelsTab from './LiveLevelsTab'
import BacktestLevelsTab from './BacktestLevelsTab'
import { colors, fonts, spacing } from '../../styles/tokens'

// Ported from frontend/src/pages/DailyLevels.jsx -- same simple local
// tab-state toggle (no need for a nested navigator here, unlike
// Strategy Detail, since neither tab needs deep-linkable sub-routes).
// SafeAreaView (top edge only) keeps the Live/Backtest toggle clear of
// the status bar/notch -- this screen has no stack header (headerShown
// is false on the tab) so nothing else pushes it down.
export default function LevelsScreen() {
  const [tab, setTab] = useState('live')

  return (
    <SafeAreaView style={styles.screen} edges={['top']}>
      <View style={styles.tabBar}>
        <Pressable style={[styles.tabItem, tab === 'live' ? styles.tabItemActive : null]} onPress={() => setTab('live')}>
          <Text style={[styles.tabText, tab === 'live' ? styles.tabTextActive : null]}>Live</Text>
        </Pressable>
        <Pressable style={[styles.tabItem, tab === 'backtest' ? styles.tabItemActive : null]} onPress={() => setTab('backtest')}>
          <Text style={[styles.tabText, tab === 'backtest' ? styles.tabTextActive : null]}>Backtest</Text>
        </Pressable>
      </View>

      {tab === 'live' ? <LiveLevelsTab /> : <BacktestLevelsTab />}
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.bgBase,
  },
  tabBar: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: colors.borderHairline,
    backgroundColor: colors.bgPanel,
  },
  tabItem: {
    flex: 1,
    paddingVertical: spacing[3],
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabItemActive: {
    borderBottomColor: colors.accent,
  },
  tabText: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 13,
    color: colors.textSecondary,
  },
  tabTextActive: {
    color: colors.accent,
  },
})
