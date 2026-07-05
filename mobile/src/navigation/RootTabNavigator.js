import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { Ionicons } from '@expo/vector-icons'
import AlertsScreen from '../screens/AlertsScreen'
import LevelsScreen from '../screens/levels/LevelsScreen'
import BacktestStackNavigator from './BacktestStackNavigator'
import { bottomTabScreenOptions } from './navigationTheme'

const Tab = createBottomTabNavigator()

// 3-tab bottom nav: Backtest (the whole point of the app -- data
// picking now lives behind a small icon inside it instead of its own
// tab, per user feedback), Levels, Alerts. Settings moved behind a
// gear icon inside Backtest (pushed onto its stack) since it's tuned
// rarely, unlike Alerts which is a standalone, frequently-checked
// destination on its own.
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
        name="Alerts"
        component={AlertsScreen}
        options={{
          headerShown: false,
          tabBarIcon: ({ color, size }) => <Ionicons name="notifications-outline" size={size} color={color} />,
        }}
      />
    </Tab.Navigator>
  )
}
