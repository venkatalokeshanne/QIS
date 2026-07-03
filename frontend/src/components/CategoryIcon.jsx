import './CategoryIcon.css'

// One simple line icon per strategy category, matching the app's
// single-accent-color / no-decoration visual language. Unknown
// categories (as new strategy folders get added) fall back to a
// monogram of the first letter rather than needing a new icon drawn.
const ICONS = {
  trend_following: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 17 9 11 13 15 21 5" />
      <polyline points="15 5 21 5 21 11" />
    </svg>
  ),
  breakout: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="4" y1="8" x2="20" y2="8" />
      <line x1="4" y1="16" x2="14" y2="16" />
      <line x1="17" y1="20" x2="17" y2="4" />
      <polyline points="13 8 17 4 21 8" />
    </svg>
  ),
  momentum: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="2 12 7 12 9 5 13 19 15 12 22 12" />
    </svg>
  ),
}

export default function CategoryIcon({ category }) {
  const label = category.replace(/_/g, ' ')
  const icon = ICONS[category]

  return (
    <span className="category-icon" title={label} aria-label={label}>
      {icon || <span className="category-icon-monogram">{label.charAt(0).toUpperCase()}</span>}
    </span>
  )
}
