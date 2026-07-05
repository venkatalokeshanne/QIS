import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs'
import { StrategyDetailProvider } from '../screens/strategyDetail/StrategyDetailContext'
import ChartsTab from '../screens/strategyDetail/ChartsTab'
import ConfigureTab from '../screens/strategyDetail/ConfigureTab'
import InfoTab from '../screens/strategyDetail/InfoTab'
import { topTabScreenOptions } from './navigationTheme'

const TopTab = createMaterialTopTabNavigator()

// Strategy Detail's tabs, nested inside the Backtest stack. Wrapped in
// StrategyDetailProvider so all independently-mounted tab screens
// share one backtest run and one focused-ticker state, matching the
// web version's single component with local useState. Results/Tickers/
// TrendSpider (ported from the web app) were dropped on mobile as
// redundant with the batch Results screen reached from Run Backtests;
// Alerts moved to its own global bottom tab (see AlertsScreen) instead
// of living per-strategy here.
export default function StrategyDetailTopTabs({ route }) {
  const { name } = route.params

  return (
    <StrategyDetailProvider name={name}>
      <TopTab.Navigator screenOptions={topTabScreenOptions}>
        <TopTab.Screen name="Charts" component={ChartsTab} />
        <TopTab.Screen name="Configure" component={ConfigureTab} />
        <TopTab.Screen name="Info" component={InfoTab} />
      </TopTab.Navigator>
    </StrategyDetailProvider>
  )
}
