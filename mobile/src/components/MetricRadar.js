import { View, Text, StyleSheet } from 'react-native'
import Svg, { Polygon, Line, Circle } from 'react-native-svg'
import { colors, fonts } from '../styles/tokens'

function clamp(v, lo, hi) {
  return Math.min(hi, Math.max(lo, v))
}

// Fixed, hand-picked domains per metric so six wildly different units
// share one 0-100 radar scale -- ported verbatim from
// frontend/src/components/MetricRadar.jsx.
const RADAR_METRICS = [
  { name: 'win_rate', label: 'Win Rate', score: (v) => clamp(v, 0, 100) },
  { name: 'profit_factor', label: 'Profit Factor', score: (v) => (clamp(v, 0, 3) / 3) * 100 },
  { name: 'sharpe_ratio', label: 'Sharpe', score: (v) => ((clamp(v, -1, 3) + 1) / 4) * 100 },
  { name: 'recovery_factor', label: 'Recovery', score: (v) => (clamp(v, 0, 5) / 5) * 100 },
  { name: 'consistency', label: 'Consistency', score: (v) => clamp(v, 0, 1) * 100 },
  { name: 'max_drawdown', label: 'Low Drawdown', score: (v) => 100 - clamp(v, 0, 100) },
]

// Ported onto react-native-svg -- the axisPoint() trig is unchanged.
// Web positions labels via CSS `left/top: ${x}%` on an absolutely
// positioned overlay div, which works here too since RN's View style
// accepts percentage strings for position, and the wrapper is a fixed
// 1:1 aspect-ratio square just like the web version's `aspect-ratio: 1/1`.
export default function MetricRadar({ metrics }) {
  const size = 100
  const center = size / 2
  const maxRadius = 36
  const axisCount = RADAR_METRICS.length
  const angleStep = (Math.PI * 2) / axisCount

  const axisPoint = (i, radius) => {
    const angle = angleStep * i - Math.PI / 2
    return [center + radius * Math.cos(angle), center + radius * Math.sin(angle)]
  }

  const values = RADAR_METRICS.map((axis) => {
    const raw = metrics?.[axis.name]
    if (raw === null || raw === undefined) return null
    return clamp(axis.score(raw), 0, 100)
  })

  const hasData = values.some((v) => v !== null)

  const polygonPoints = values.map((v, i) => axisPoint(i, ((v ?? 0) / 100) * maxRadius).join(',')).join(' ')

  return (
    <View style={styles.wrap}>
      <Svg width="100%" height="100%" viewBox={`0 0 ${size} ${size}`}>
        {[0.25, 0.5, 0.75, 1].map((r) => (
          <Polygon
            key={r}
            points={RADAR_METRICS.map((_, i) => axisPoint(i, maxRadius * r).join(',')).join(' ')}
            fill="none"
            stroke={colors.borderHairline}
            strokeWidth={0.5}
          />
        ))}

        {RADAR_METRICS.map((axis, i) => {
          const [x, y] = axisPoint(i, maxRadius)
          return <Line key={axis.name} x1={center} y1={center} x2={x} y2={y} stroke={colors.borderHairlineStrong} strokeWidth={0.5} />
        })}

        {hasData && (
          <Polygon points={polygonPoints} fill={colors.accentWash} stroke={colors.accent} strokeWidth={1.25} strokeLinejoin="round" />
        )}

        {hasData &&
          values.map((v, i) => {
            if (v === null) return null
            const [x, y] = axisPoint(i, (v / 100) * maxRadius)
            return <Circle key={RADAR_METRICS[i].name} cx={x} cy={y} r={1.8} fill={colors.accent} />
          })}
      </Svg>

      <View style={styles.labelsLayer} pointerEvents="none">
        {RADAR_METRICS.map((axis, i) => {
          const [x, y] = axisPoint(i, maxRadius + 12)
          return (
            <Text key={axis.name} style={[styles.label, { left: `${x}%`, top: `${y}%` }]}>
              {axis.label}
            </Text>
          )
        })}
      </View>

      {!hasData && (
        <View style={styles.emptyOverlay}>
          <Text style={styles.emptyText}>Not enough data for a fingerprint yet.</Text>
        </View>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  wrap: {
    position: 'relative',
    width: '100%',
    maxWidth: 320,
    aspectRatio: 1,
    alignSelf: 'center',
  },
  labelsLayer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  label: {
    position: 'absolute',
    transform: [{ translateX: -30 }, { translateY: -8 }],
    fontFamily: fonts.ui,
    fontSize: 10,
    textTransform: 'uppercase',
    letterSpacing: 0.3,
    color: colors.textTertiary,
    width: 60,
    textAlign: 'center',
  },
  emptyOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyText: {
    fontFamily: fonts.ui,
    fontSize: 13,
    color: colors.textTertiary,
    textAlign: 'center',
  },
})
