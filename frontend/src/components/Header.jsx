import { NavLink, useNavigate, useParams } from 'react-router-dom'
import { useStrategies } from '../api/hooks'
import { NAV_ITEMS } from '../nav-items'
import TickerMultiSelect from './TickerMultiSelect'
import TwelvedataFetchMenu from './TwelvedataFetchMenu'
import './Header.css'

export default function Header({ mobileNavOpen, onMenuToggle }) {
  const navigate = useNavigate()
  const { name: activeStrategyName } = useParams()
  const { data: strategies } = useStrategies()

  return (
    <header className="topbar">
      <button
        className={`topbar-menu-toggle${mobileNavOpen ? ' open' : ''}`}
        onClick={onMenuToggle}
        aria-label={mobileNavOpen ? 'Close navigation menu' : 'Toggle navigation menu'}
        aria-expanded={mobileNavOpen}
      >
        <span />
        <span />
        <span />
      </button>

      <div className="topbar-brand">
        <span className="topbar-brand-mark">Q</span>
        <span className="topbar-brand-name">Quant Research</span>
      </div>

      <nav className="topbar-nav">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.exact}
            className={({ isActive }) => `topbar-link${isActive ? ' active' : ''}`}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="topbar-dataset">
        {/* Desktop/tablet only -- hidden ≤640px via CSS, where the ticker
            picker moves into the drawer (StrategySidebar) instead. */}
        <div className="topbar-ticker-select">
          <TickerMultiSelect />
        </div>

        {/* Mobile-only: the ticker picker moves into the drawer where
            there's room; this compact quick-switcher takes its place in
            the header, since jumping between strategies while already on a
            strategy detail page is the more common mobile action. */}
        <select
          className="topbar-strategy-select"
          value={activeStrategyName || ''}
          onChange={(e) => e.target.value && navigate(`/strategy/${e.target.value}`)}
        >
          <option value="" disabled>
            Choose a strategy…
          </option>
          {(strategies || []).map((s) => (
            <option key={s.name} value={s.name}>
              {s.display_name}
            </option>
          ))}
        </select>

        <TwelvedataFetchMenu />
      </div>
    </header>
  )
}
