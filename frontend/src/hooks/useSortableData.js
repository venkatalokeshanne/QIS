import { useMemo, useState } from 'react'

// Generic click-to-sort helper for any table: pass the raw rows and a
// `getValue(row, key)` accessor, get back the sorted rows plus the
// state/handlers a header cell needs to render its sort indicator.
// Sort is stable (ties keep their original relative order) and treats
// null/undefined as "always last" regardless of direction, since most
// of this app's numeric columns can be null (e.g. sharpe_ratio before
// any trades close) and burying those at the bottom reads better than
// interleaving them.
export function useSortableData(rows, getValue, initialKey = null, initialDir = 'desc') {
  const [sortKey, setSortKey] = useState(initialKey)
  const [sortDir, setSortDir] = useState(initialDir)

  const sorted = useMemo(() => {
    if (!sortKey) return rows
    const indexed = rows.map((row, i) => [row, i])
    indexed.sort(([a, ai], [b, bi]) => {
      const av = getValue(a, sortKey)
      const bv = getValue(b, sortKey)
      const aNil = av === null || av === undefined
      const bNil = bv === null || bv === undefined
      if (aNil || bNil) {
        if (aNil && bNil) return ai - bi
        return aNil ? 1 : -1
      }
      let cmp
      if (typeof av === 'string' && typeof bv === 'string') {
        cmp = av.localeCompare(bv)
      } else {
        cmp = av < bv ? -1 : av > bv ? 1 : 0
      }
      if (cmp === 0) return ai - bi
      return sortDir === 'asc' ? cmp : -cmp
    })
    return indexed.map(([row]) => row)
  }, [rows, sortKey, sortDir, getValue])

  const toggleSort = (key) => {
    if (key === sortKey) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  return { sorted, sortKey, sortDir, toggleSort }
}
