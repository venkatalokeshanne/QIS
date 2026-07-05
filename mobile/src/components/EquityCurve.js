import { useMemo, useState } from 'react'
import { View, Text, StyleSheet } from 'react-native'
import Svg, { Defs, LinearGradient, Stop, Line, Path, Circle } from 'react-native-svg'
import { formatMetricValue } from '../utils/format'
import { colors, fonts, radii, spacing } from '../styles/tokens'

// Ported from frontend/src/components/EquityCurve.jsx onto
// react-native-svg -- the coordinate math (toX/toY, area/line path
// construction) is unchanged, only the element tags change
// (<svg>/<path>/<line>/<circle> -> <Svg>/<Path>/<Line>/<Circle>).
// Web's mouse-hover crosshair becomes touch-and-drag scrubbing
// (onTouchStart/onTouchMove show the tooltip, onTouchEnd hides it) --
// the direct mobile equivalent of "hover to inspect a point."
export default function EquityCurve({ trades }) {
  const [layoutWidth, setLayoutWidth] = useState(0)
  const [hoverIndex, setHoverIndex] = useState(null)

  const points = useMemo(() => {
    if (!trades || trades.length === 0) return []
    let cumulative = 0
    return trades.map((t) => (cumulative += t.pnl ?? 0))
  }, [trades])

  if (points.length === 0) {
    return <Text style={styles.emptyText}>No trades to chart.</Text>
  }

  const width = 100
  const height = 100
  const min = Math.min(0, ...points)
  const max = Math.max(0, ...points)
  const range = max - min || 1

  const toX = (i) => (points.length === 1 ? width / 2 : (i / (points.length - 1)) * width)
  const toY = (v) => height - ((v - min) / range) * height
  const zeroY = toY(0)

  const linePath = points.map((v, i) => `${i === 0 ? 'M' : 'L'} ${toX(i)} ${toY(v)}`).join(' ')
  const areaPath = `${linePath} L ${toX(points.length - 1)} ${zeroY} L ${toX(0)} ${zeroY} Z`

  const final = points[points.length - 1]
  const isPositive = final >= 0

  const handleTouch = (e) => {
    if (!layoutWidth) return
    const x = e.nativeEvent.locationX
    const fraction = Math.min(1, Math.max(0, x / layoutWidth))
    setHoverIndex(Math.round(fraction * (points.length - 1)))
  }

  const hoverValue = hoverIndex !== null ? points[hoverIndex] : null
  const hoverX = hoverIndex !== null ? toX(hoverIndex) : null

  return (
    <View
      onLayout={(e) => setLayoutWidth(e.nativeEvent.layout.width)}
      onTouchStart={handleTouch}
      onTouchMove={handleTouch}
      onTouchEnd={() => setHoverIndex(null)}
      style={styles.wrap}
    >
      <Svg width="100%" height={160} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
        <Defs>
          <LinearGradient id="equityFillPositive" x1="0" y1="0" x2="0" y2="1">
            <Stop offset="0%" stopColor={colors.positive} stopOpacity={0.35} />
            <Stop offset="100%" stopColor={colors.positive} stopOpacity={0} />
          </LinearGradient>
          <LinearGradient id="equityFillNegative" x1="0" y1="0" x2="0" y2="1">
            <Stop offset="0%" stopColor={colors.negative} stopOpacity={0} />
            <Stop offset="100%" stopColor={colors.negative} stopOpacity={0.35} />
          </LinearGradient>
        </Defs>

        <Line x1="0" y1={zeroY} x2={width} y2={zeroY} stroke={colors.borderHairlineStrong} strokeWidth={1} vectorEffect="non-scaling-stroke" />

        <Path d={areaPath} fill={isPositive ? 'url(#equityFillPositive)' : 'url(#equityFillNegative)'} />

        <Path
          d={linePath}
          fill="none"
          stroke={isPositive ? colors.positive : colors.negative}
          strokeWidth={1.5}
          vectorEffect="non-scaling-stroke"
        />

        {hoverIndex !== null && (
          <>
            <Line
              x1={hoverX}
              y1="0"
              x2={hoverX}
              y2={height}
              stroke={colors.textTertiary}
              strokeWidth={1}
              strokeDasharray="2 2"
              vectorEffect="non-scaling-stroke"
            />
            <Circle
              cx={hoverX}
              cy={toY(hoverValue)}
              r={2.2}
              fill={hoverValue >= 0 ? colors.positive : colors.negative}
              stroke={colors.bgPanel}
              strokeWidth={1}
              vectorEffect="non-scaling-stroke"
            />
          </>
        )}
      </Svg>

      {hoverIndex !== null && (
        <View style={[styles.tooltip, { left: `${(hoverX / width) * 100}%` }]}>
          <Text style={styles.tooltipLabel}>Trade {hoverIndex + 1}</Text>
          <Text style={[styles.tooltipValue, { color: hoverValue >= 0 ? colors.positive : colors.negative }]}>
            {formatMetricValue(hoverValue, 'currency')}
          </Text>
        </View>
      )}

      <View style={styles.footline}>
        <Text style={styles.footlineText}>Trade 1</Text>
        <Text style={styles.footlineText}>Trade {points.length}</Text>
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
