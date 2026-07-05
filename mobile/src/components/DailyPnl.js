import { useMemo, useState } from 'react'
import { View, Text, StyleSheet } from 'react-native'
import Svg, { Line, Rect } from 'react-native-svg'
import { formatMetricValue } from '../utils/format'
import { colors, fonts, radii, spacing } from '../styles/tokens'

function dateKey(iso) {
  if (!iso) return null
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return null
  return d.toISOString().slice(0, 10)
}

function formatDayLabel(key) {
  const d = new Date(`${key}T00:00:00`)
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

// Ported from frontend/src/components/DailyPnl.jsx onto
// react-native-svg -- same day-aggregation logic, touch-and-drag
// scrubbing standing in for mouse hover (see EquityCurve for the same
// pattern).
export default function DailyPnl({ trades, main = false }) {
  const [layoutWidth, setLayoutWidth] = useState(0)
  const [hoverIndex, setHoverIndex] = useState(null)

  const days = useMemo(() => {
    if (!trades || trades.length === 0) return []
    const totals = new Map()
    for (const t of trades) {
      const key = dateKey(t.exit_time ?? t.entry_time)
      if (!key) continue
      totals.set(key, (totals.get(key) ?? 0) + (t.pnl ?? 0))
    }
    return Array.from(totals.entries())
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
      .map(([date, pnl]) => ({ date, pnl }))
  }, [trades])

  if (days.length === 0) {
    return <Text style={styles.emptyText}>No trades to chart.</Text>
  }

  const width = 100
  const height = 100
  const midY = height / 2
  const maxAbs = Math.max(1, ...days.map((d) => Math.abs(d.pnl)))
  const slot = width / days.length
  const gap = Math.min(slot * 0.3, 1.2)
  const barWidth = Math.max(slot - gap, 0.3)

  const handleTouch = (e) => {
    if (!layoutWidth) return
    const x = e.nativeEvent.locationX
    const fraction = Math.min(1, Math.max(0, x / layoutWidth))
    setHoverIndex(Math.min(days.length - 1, Math.floor(fraction * days.length)))
  }

  const hovered = hoverIndex !== null ? days[hoverIndex] : null

  return (
    <View
      onLayout={(e) => setLayoutWidth(e.nativeEvent.layout.width)}
      onTouchStart={handleTouch}
      onTouchMove={handleTouch}
      onTouchEnd={() => setHoverIndex(null)}
      style={styles.wrap}
    >
      <Svg width="100%" height={main ? 220 : 160} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
        <Line x1="0" y1={midY} x2={width} y2={midY} stroke={colors.borderHairlineStrong} strokeWidth={1} vectorEffect="non-scaling-stroke" />
        {days.map((d, i) => {
          const barHeight = Math.max((Math.abs(d.pnl) / maxAbs) * midY, 0.6)
          const x = i * slot + gap / 2
          const isPositive = d.pnl >= 0
          const y = isPositive ? midY - barHeight : midY
          const active = hoverIndex === i
          return (
            <Rect
              key={d.date}
              x={x}
              y={y}
              width={barWidth}
              height={barHeight}
              fill={isPositive ? colors.positive : colors.negative}
              opacity={active ? 1 : 0.85}
            />
          )
        })}
      </Svg>

      {hovered && (
        <View style={[styles.tooltip, { left: `${((hoverIndex + 0.5) / days.length) * 100}%` }]}>
          <Text style={styles.tooltipLabel}>{formatDayLabel(hovered.date)}</Text>
          <Text style={[styles.tooltipValue, { color: hovered.pnl >= 0 ? colors.positive : colors.negative }]}>
            {formatMetricValue(hovered.pnl, 'currency')}
          </Text>
        </View>
      )}

      <View style={styles.footline}>
        <Text style={styles.footlineText}>{formatDayLabel(days[0].date)}</Text>
        {days.length > 1 && <Text style={styles.footlineText}>{formatDayLabel(days[days.length - 1].date)}</Text>}
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  wrap: {
    position: 'relative',
    width: '100%',
  },
  emptyText: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textTertiary,
    paddingVertical: spacing[4],
  },
  tooltip: {
    position: 'absolute',
    top: 0,
    transform: [{ translateX: -40 }, { translateY: -50 }],
    backgroundColor: colors.bgPanelRaised,
    borderWidth: 1,
    borderColor: colors.borderHairlineStrong,
    borderRadius: radii.sm,
    paddingVertical: 6,
    paddingHorizontal: spacing[3],
  },
  tooltipLabel: {
    fontFamily: fonts.ui,
    fontSize: 10,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
    color: colors.textTertiary,
  },
  tooltipValue: {
    fontFamily: fonts.monoMedium,
    fontSize: 13,
  },
  footline: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing[2],
  },
  footlineText: {
    fontFamily: fonts.ui,
    fontSize: 11,
    color: colors.textTertiary,
  },
})
