import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import DailyLevels from './pages/DailyLevels'
import StrategyDetail from './pages/StrategyDetail'
import RunBacktests from './pages/RunBacktests'
import Results from './pages/Results'
import Compare from './pages/Compare'
import Scanner from './pages/Scanner'
import DailySelector from './pages/DailySelector'
import Settings from './pages/Settings'
import StrategySelection from './pages/StrategySelection'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/run" replace />} />
        <Route path="/levels" element={<DailyLevels />} />
        <Route path="/strategy/:name" element={<StrategyDetail />} />
        <Route path="/run" element={<RunBacktests />} />
        <Route path="/results" element={<Results />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/daily-selector" element={<DailySelector />} />
        <Route path="/strategy-selection" element={<StrategySelection />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
