import { useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Header from './Header'
import StrategySidebar from './StrategySidebar'
import './Layout.css'

export default function Layout() {
  const location = useLocation()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  // Any navigation -- a NavLink inside the drawer, or a strategy click
  // from StrategySidebar's own navigate() -- closes the mobile drawer.
  useEffect(() => {
    setMobileNavOpen(false)
  }, [location.pathname])

  useEffect(() => {
    document.body.style.overflow = mobileNavOpen ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [mobileNavOpen])

  return (
    <div className="shell">
      <Header mobileNavOpen={mobileNavOpen} onMenuToggle={() => setMobileNavOpen((open) => !open)} />
      <div className="shell-body">
        {mobileNavOpen && (
          <div className="mobile-nav-backdrop" onClick={() => setMobileNavOpen(false)} />
        )}
        <StrategySidebar mobileOpen={mobileNavOpen} />
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
