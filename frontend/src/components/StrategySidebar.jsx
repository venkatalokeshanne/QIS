import { useMemo, useState } from 'react'
import { NavLink, useNavigate, useParams } from 'react-router-dom'
import CategoryIcon from './CategoryIcon'
import TickerSelect from './TickerSelect'
import { useStrategies } from '../api/hooks'
import { NAV_ITEMS } from '../nav-items'
import './StrategySidebar.css'

export default function StrategySidebar({ mobileOpen }) {
  const navigate = useNavigate()
  const { name: activeName } = useParams()
  const { data: strategies } = useStrategies()
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    if (!strategies) return []
    const q = search.trim().toLowerCase()
    if (!q) return strategies
    return strategies.filter(
      (s) =>
        s.display_name.toLowerCase().includes(q) ||
        s.name.toLowerCase().includes(q) ||
        s.category.toLowerCase().includes(q)
    )
  }, [strategies, search])

  return (
    <aside className={`strategy-sidebar${mobileOpen ? ' open' : ''}`}>
      {/* Only visible in the mobile drawer (≤640px) -- on wider
          screens these same links already live in the header. */}
      <nav className="strategy-sidebar-mobile-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.exact}
            className={({ isActive }) => `strategy-sidebar-mobile-link${isActive ? ' active' : ''}`}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Only visible in the mobile drawer (≤640px) -- on wider screens the
          ticker picker lives in the header instead (see Header.jsx). */}
      <div className="strategy-sidebar-mobile-dataset">
        <span className="field-label">Tickers</span>
        <TickerSelect />
      </div>

      <div className="strategy-sidebar-search">
        <input
          type="text"
          className="field-input"
          placeholder="Search strategies…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="strategy-sidebar-list">
        {(strategies || []).length === 0 ? (
          <div className="strategy-sidebar-empty">Loading…</div>
        ) : filtered.length === 0 ? (
          <div className="strategy-sidebar-empty">No matches.</div>
        ) : (
          filtered.map((s) => (
            <button
              key={s.name}
              className={`strategy-sidebar-item${activeName === s.name ? ' active' : ''}`}
              onClick={() => navigate(`/strategy/${s.name}`)}
              title={`Open ${s.display_name}`}
            >
              <span className="strategy-sidebar-name">{s.display_name}</span>
              <CategoryIcon category={s.category} />
            </button>
          ))
        )}
      </div>
    </aside>
  )
}
