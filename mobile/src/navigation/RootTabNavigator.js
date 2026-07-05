import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { Ionicons } from '@expo/vector-icons'
import SettingsScreen from '../screens/SettingsScreen'
import LevelsScreen from '../screens/levels/LevelsScreen'
import BacktestStackNavigator from './BacktestStackNavigator'
import { bottomTabScreenOptions } from './navigationTheme'

const Tab = createBottomTabNavigator()

// 3-tab bottom nav: Backtest (the whole point of the app -- data
// picking now lives behind a small icon inside it instead of its own
// tab, per user feedback), Levels, Settings.
export default function RootTabNavigator() {
  return (
    <Tab.Navigator screenOptions={bottomTabScreenOptions}>
      <Tab.Screen
        name="Backtest"
        component={BacktestStackNavigator}
        options={{
          headerShown: false,
          tabBarIcon: ({ color, size }) => <Ionicons name="stats-chart-outline" size={size} color={color} />,
        }}
      />
      <Tab.Screen
        name="Levels"
        component={LevelsScreen}
        options={{
          title: 'Daily Levels',
          headerShown: false,
          tabBarIcon: ({ color, size }) => <Ionicons name="pulse-outline" size={size} color={color} />,
        }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Ionicons name="settings-outline" size={size} color={color} />,
        }}
      />
    </Tab.Navigator>
  )
}
