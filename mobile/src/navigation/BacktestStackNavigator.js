import { createNativeStackNavigator } from '@react-navigation/native-stack'
import RunBacktestsScreen from '../screens/RunBacktestsScreen'
import ResultsScreen from '../screens/ResultsScreen'
import CompareScreen from '../screens/CompareScreen'
import SettingsScreen from '../screens/SettingsScreen'
import StrategyDetailTopTabs from './StrategyDetailTopTabs'
import { stackScreenOptions } from './navigationTheme'

const Stack = createNativeStackNavigator()

// RunBacktests -> StrategyDetail (nested top-tabs) -> Results -> Compare,
// matching the web app's workflow (RunBacktests.jsx pushes into
// StrategyDetail.jsx, then across to Results.jsx / Compare.jsx).
// Results/Compare live here rather than as separate bottom tabs since
// they're workflow-dependent on a run, not independently navigable.
// Settings also lives here now (pushed via a gear icon on
// RunBacktestsScreen) instead of its own bottom tab.
export default function BacktestStackNavigator() {
  return (
    <Stack.Navigator screenOptions={stackScreenOptions}>
      <Stack.Screen name="RunBacktests" component={RunBacktestsScreen} options={{ headerShown: false }} />
      <Stack.Screen name="StrategyDetail" component={StrategyDetailTopTabs} options={{ title: 'Strategy Detail' }} />
      <Stack.Screen name="Results" component={ResultsScreen} options={{ headerShown: false }} />
      <Stack.Screen name="Compare" component={CompareScreen} options={{ headerShown: false }} />
      <Stack.Screen name="Settings" component={SettingsScreen} options={{ title: 'Settings' }} />
    </Stack.Navigator>
  )
}
