// Shared between Header (desktop inline nav) and StrategySidebar (the
// same links reappear inside the mobile drawer) -- one list, not two
// that can drift apart.
export const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', exact: true },
  { to: '/upload', label: 'Upload Data' },
  { to: '/datasets', label: 'Datasets' },
  { to: '/levels', label: 'Daily Levels' },
  { to: '/run', label: 'Run Backtests' },
  { to: '/compare', label: 'Compare' },
  { to: '/settings', label: 'Settings' },
]
