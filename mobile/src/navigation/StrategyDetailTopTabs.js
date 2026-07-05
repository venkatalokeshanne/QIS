import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs'
import { StrategyDetailProvider } from '../screens/strategyDetail/StrategyDetailContext'
import ResultsTab from '../screens/strategyDetail/ResultsTab'
import ChartsTab from '../screens/strategyDetail/ChartsTab'
import TickersTab from '../screens/strategyDetail/TickersTab'
import ConfigureTab from '../screens/strategyDetail/ConfigureTab'
import TrendSpiderTab from '../screens/strategyDetail/TrendSpiderTab'
import InfoTab from '../screens/strategyDetail/InfoTab'
import AlertsTab from '../screens/strategyDetail/AlertsTab'
import { topTabScreenOptions } from './navigationTheme'

const TopTab = createMaterialTopTabNavigator()

// Strategy Detail's 6 tabs from the web app (StrategyDetail.jsx),
// nested inside the Backtest stack. Wrapped in StrategyDetailProvider
// so all 6 independently-mounted tab screens share one backtest run
// and one focused-ticker state, matching the web version's single
// component with local useState.
export default function StrategyDetailTopTabs({ route }) {
  const { name } = route.params

  return (
    <StrategyDetailProvider name={name}>
      <TopTab.Navigator screenOptions={topTabScreenOptions}>
        <TopTab.Screen name="Results" component={ResultsTab} />
        <TopTab.Screen name="Charts" component={ChartsTab} />
        <TopTab.Screen name="Tickers" component={TickersTab} />
        <TopTab.Screen name="Configure" component={ConfigureTab} />
        <TopTab.Screen name="TrendSpider" component={TrendSpiderTab} />
        <TopTab.Screen name="Info" component={InfoTab} />
        <TopTab.Screen name="Alerts" component={AlertsTab} />
      </TopTab.Navigator>
    </StrategyDetailProvider>
  )
}
