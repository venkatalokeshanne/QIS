// A <th> that toggles sort on click and shows an up/down indicator for
// whichever column is currently active -- shared by every data-table in
// the app so sorting looks and behaves the same everywhere.
export default function SortableTh({ label, sortKey, activeKey, dir, onSort, align, style, className }) {
  const active = sortKey === activeKey
  return (
    <th
      className={`data-table-sortable-th${align === 'right' ? ' align-right' : ''}${active ? ' sorted' : ''}${className ? ` ${className}` : ''}`}
      onClick={() => onSort(sortKey)}
      style={style}
    >
      {label}
      <span className="data-table-sort-indicator">{active ? (dir === 'asc' ? '▲' : '▼') : ''}</span>
    </th>
  )
}
