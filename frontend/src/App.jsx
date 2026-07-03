import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Datasets from './pages/Datasets'
import DailyLevels from './pages/DailyLevels'
import StrategyDetail from './pages/StrategyDetail'
import RunBacktests from './pages/RunBacktests'
import Results from './pages/Results'
import Compare from './pages/Compare'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/datasets" element={<Datasets />} />
        <Route path="/levels" element={<DailyLevels />} />
        <Route path="/strategy/:name" element={<StrategyDetail />} />
        <Route path="/run" element={<RunBacktests />} />
        <Route path="/results" element={<Results />} />
        <Route path="/compare" element={<Compare />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}
