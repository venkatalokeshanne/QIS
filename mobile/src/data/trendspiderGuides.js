// Step-by-step TrendSpider Strategy Builder setup for each strategy,
// mirroring this strategy's exact entry/exit rules (cross-checked
// against backend/app/strategies/<name>/strategy.py & the /catalog
// endpoint). Indicator/comparison names follow TrendSpider's no-code
// rule builder as of early 2026 -- verify exact labels in your own
// account since TrendSpider's UI changes between releases.
//
// `warning: true` entries flag rules that don't map cleanly onto a
// plain drag-and-drop block (session-relative timing, candlestick
// pattern lookback, relative volume, prior-session references) and
// may need TrendSpider's Raw Script / custom formula editor instead.

const VOLUME_FILTER_INDICATOR = { name: 'Volume Moving Average', settings: 'SMA of Volume, length = volume_avg_period (default 20)' }
const VOLUME_FILTER_RULE = 'Volume > Volume SMA'

export const trendspiderGuides = {
  adaptive_daily_regime: {
    indicators: [
      { name: 'ADX/DI', settings: 'period 14 -- used only for its ADX line' },
      { name: 'Relative Volume', settings: 'period 20' },
      { name: 'EMA (fast)', settings: 'period 9' },
      { name: 'EMA (slow)', settings: 'period 21' },
      VOLUME_FILTER_INDICATOR,
      { name: 'RSI', settings: 'period 14' },
      { name: 'Bollinger Bands', settings: 'period 20, std dev 2.0' },
    ],
    entryLong: [
      "Regime gate (evaluated once per session from YESTERDAY's closing ADX/RVOL, not today's data): if RVOL < 0.5 -- no entries at all today",
      'Otherwise, if ADX >= 25 (yesterday) -- TREND day: EMA(9) Crosses Above EMA(21) AND ' + VOLUME_FILTER_RULE,
      'Otherwise -- RANGE day: Close Crosses Above Lower Band (was below, closes back above) AND RSI < 30',
    ],
    entryShort: [
      'Same regime gate as Long',
      'TREND day: EMA(9) Crosses Below EMA(21) AND ' + VOLUME_FILTER_RULE,
      'RANGE day: Close Crosses Below Upper Band (was above, closes back below) AND RSI > 70',
    ],
    exit: [
      'Opposite EMA cross, OR',
      'Close Crosses Middle Band, OR',
      'RSI >= 70 or RSI <= 30',
      '(any one of these closes the position -- it does not matter which regime opened the trade)',
    ],
    notes: [
      {
        warning: true,
        text:
          "This strategy is NOT a fixed rule set -- it picks a different indicator family each morning based on yesterday's close, using a day-level lookup (group-by-session, shifted one day) that plain cross/threshold blocks can't express. TrendSpider's no-code builder can't conditionally swap which rule group is \"live\" day-to-day. Replicating this faithfully needs TrendSpider's Raw Script (custom formula) editor -- if you don't have access to it, the closest approximation is deploying the TREND-day rules and the RANGE-day rules as two SEPARATE strategies/bots, and manually (or via a scheduled script) enabling only one of them each morning based on ADX/RVOL from yesterday's close.",
      },
      {
        warning: false,
        text: 'This is also the only strategy in this platform where "no trade today" (the sit-out day) is itself part of the strategy logic, not just an empty signal -- there is no single-condition way to represent that in a crosses-only builder either.',
      },
    ],
  },
  adx_di_cross: {
    indicators: [{ name: 'ADX/DI', settings: 'period 14 -- gives ADX, +DI, -DI lines' }],
    entryLong: ['+DI Crosses Above -DI', 'ADX > 25'],
    entryShort: ['-DI Crosses Above +DI', 'ADX > 25'],
    exit: ['Opposite DI cross (-DI Crosses Above +DI closes longs, +DI Crosses Above -DI closes shorts)'],
    notes: [],
  },
  base_strategy: {
    directionNote: 'Long only -- this strategy has no direction toggle.',
    indicators: [
      { name: 'VWAP', settings: 'session VWAP' },
      { name: 'RSI', settings: 'period 14' },
      { name: 'MACD', settings: '12 / 26 / 9' },
    ],
    entryLong: [
      'Close < VWAP',
      'RSI < 40',
      'MACD Histogram > MACD Histogram[1 bar ago]',
      'Close > Open',
      'Volume > Volume[1 bar ago]',
    ],
    entryShort: [],
    exit: ['Close ≥ VWAP', 'RSI > 55 (either condition triggers exit)'],
    notes: [],
  },
  bollinger_breakout: {
    indicators: [
      { name: 'Bollinger Bands', settings: 'period 20, std dev 2.0' },
      VOLUME_FILTER_INDICATOR,
    ],
    entryLong: ['Close Crosses Above Upper Band', VOLUME_FILTER_RULE],
    entryShort: ['Close Crosses Below Lower Band', VOLUME_FILTER_RULE],
    exit: ['Close Crosses Middle Band (SMA basis), either direction'],
    notes: [],
  },
  bollinger_reversion: {
    indicators: [
      { name: 'Bollinger Bands', settings: 'period 20, std dev 2.0' },
      { name: 'RSI', settings: 'period 14' },
    ],
    entryLong: ['Close Crosses Above Lower Band (was below, closes back above)', 'RSI < 30'],
    entryShort: ['Close Crosses Below Upper Band (was above, closes back below)', 'RSI > 70'],
    exit: ['Close Crosses Middle Band', 'or RSI reaches the opposite extreme (>70 for longs, <30 for shorts)'],
    notes: [],
  },
  cci_reversal: {
    indicators: [{ name: 'CCI', settings: 'period 20' }],
    entryLong: ['CCI Crosses Above -100'],
    entryShort: ['CCI Crosses Below 100'],
    exit: ['CCI Crosses 0'],
    notes: [],
  },
  donchian_breakout: {
    indicators: [{ name: 'Donchian Channels', settings: 'period 20' }],
    entryLong: ['Close Crosses Above Upper Donchian Band'],
    entryShort: ['Close Crosses Below Lower Donchian Band'],
    exit: ['Close Crosses Midline (basis)'],
    notes: [
      {
        warning: true,
        text: "This strategy excludes the current bar from the high/low window (breakout is measured against the prior N bars). TrendSpider's stock Donchian indicator typically includes the current bar -- check for an \"offset by 1\" option, or signals may fire slightly differently than this backtest.",
      },
    ],
  },
  ema_cross: {
    indicators: [
      { name: 'EMA (fast)', settings: 'period 9' },
      { name: 'EMA (slow)', settings: 'period 21' },
      { name: 'EMA (trend filter, optional -- on by default)', settings: 'period 50' },
      { ...VOLUME_FILTER_INDICATOR, name: 'Volume Moving Average (optional filter, on by default)' },
    ],
    entryLong: ['EMA(9) Crosses Above EMA(21)', 'Close > EMA(50)', VOLUME_FILTER_RULE],
    entryShort: ['EMA(9) Crosses Below EMA(21)', 'Close < EMA(50)', VOLUME_FILTER_RULE],
    exit: ['Opposite EMA cross'],
    notes: [{ warning: false, text: 'Drop the trend/volume rules from the group if you set use_trend_filter or use_volume_filter to false in Configure.' }],
  },
  gap_and_go: {
    indicators: [
      { name: 'Opening Range', settings: '5 minutes' },
      VOLUME_FILTER_INDICATOR,
    ],
    entryLong: [
      'Gap up ≥ 2%: Open (today) ≥ Previous Session Close × 1.02',
      'Close Crosses Above Opening Range High',
      'Time Since Session Open < 90 minutes',
      VOLUME_FILTER_RULE,
    ],
    entryShort: [
      'Gap down ≥ 2%: Open (today) ≤ Previous Session Close × 0.98',
      'Close Crosses Below Opening Range Low',
      'Time Since Session Open < 90 minutes',
      VOLUME_FILTER_RULE,
    ],
    exit: ['Close re-enters the Opening Range (failed breakout)', 'Forced close at session end (e.g. Time ≥ 15:59)'],
    notes: [
      {
        warning: true,
        text: 'Needs a prior-session-close reference for the gap check, plus a session-clock time filter -- confirm your TrendSpider plan supports both (usually via a Gap indicator / session-anchored tools).',
      },
    ],
  },
  ichimoku_breakout: {
    indicators: [{ name: 'Ichimoku Cloud', settings: 'conversion 9, base 26, leading span B 52, displacement 26' }],
    entryLong: ['Close Crosses Above Max(Senkou Span A, Senkou Span B) -- cloud top'],
    entryShort: ['Close Crosses Below Min(Senkou Span A, Senkou Span B) -- cloud bottom'],
    exit: ['Close re-enters the cloud (crosses back inside the min/max band)'],
    notes: [],
  },
  inside_bar_breakout: {
    indicators: [{ name: 'Candlestick Pattern: Inside Bar', settings: 'built-in pattern detector' }],
    entryLong: ["Prior bar's Pattern = Inside Bar", "Close Crosses Above that inside bar's High"],
    entryShort: ["Prior bar's Pattern = Inside Bar", "Close Crosses Below that inside bar's Low"],
    exit: ['A fresh Inside Bar pattern forms again'],
    notes: [{ warning: true, text: 'Needs candlestick-pattern recognition, not just indicator crosses -- confirm Inside Bar is in your Candlestick Pattern library.' }],
  },
  keltner_breakout: {
    indicators: [
      { name: 'Keltner Channels', settings: 'EMA 20, ATR 10, multiplier 2.0' },
      VOLUME_FILTER_INDICATOR,
    ],
    entryLong: ['Close Crosses Above Upper Keltner Band', VOLUME_FILTER_RULE],
    entryShort: ['Close Crosses Below Lower Keltner Band', VOLUME_FILTER_RULE],
    exit: ['Close Crosses Middle Band (EMA basis)'],
    notes: [],
  },
  macd_momentum: {
    indicators: [
      { name: 'MACD', settings: '12 / 26 / 9' },
      { name: 'EMA (trend)', settings: 'period 50' },
    ],
    entryLong: ['MACD Histogram Crosses Above 0', 'Close > EMA(50)'],
    entryShort: ['MACD Histogram Crosses Below 0', 'Close < EMA(50)'],
    exit: ['Opposite histogram zero-cross'],
    notes: [],
  },
  momentum_breakout: {
    indicators: [
      { name: 'ROC', settings: 'period 10' },
      { name: 'Relative Volume', settings: 'period 20, threshold 1.5' },
    ],
    entryLong: ['High = new session high so far', 'RVOL > 1.5', 'ROC > 0'],
    entryShort: ['Low = new session low so far', 'RVOL > 1.5', 'ROC < 0'],
    exit: ['ROC Crosses 0'],
    notes: [
      {
        warning: true,
        text: 'Needs a session-anchored running max/min for "new high/low so far", and Relative Volume may need a custom formula (Volume / SMA(Volume, 20)) if not a stock indicator on your plan.',
      },
    ],
  },
  orb: {
    indicators: [
      { name: 'Opening Range', settings: '15 minutes' },
      VOLUME_FILTER_INDICATOR,
    ],
    entryLong: ['Opening range has finished forming', 'Close Crosses Above Opening Range High', VOLUME_FILTER_RULE],
    entryShort: ['Opening range has finished forming', 'Close Crosses Below Opening Range Low', VOLUME_FILTER_RULE],
    exit: ['Close re-enters the Opening Range (failed breakout)', 'Forced close at session end'],
    notes: [{ warning: true, text: 'Session-end forced close needs a time-based exit rule (e.g. Time ≥ 15:59) -- our execution engine applies this automatically, TrendSpider needs it added explicitly.' }],
  },
  parabolic_sar_following: {
    indicators: [{ name: 'Parabolic SAR', settings: 'start 0.02, increment 0.02, max 0.2' }],
    entryLong: ['Close Crosses Above SAR'],
    entryShort: ['Close Crosses Below SAR'],
    exit: ['Opposite cross'],
    notes: [],
  },
  stochastic_reversal: {
    indicators: [{ name: 'Stochastic Oscillator', settings: '%K period 14, slowing 3, %D period 3' }],
    entryLong: ['%K Crosses Above 20'],
    entryShort: ['%K Crosses Below 80'],
    exit: ['%K Crosses 50'],
    notes: [],
  },
  supertrend_following: {
    indicators: [{ name: 'SuperTrend', settings: 'period 10, multiplier 3.0' }],
    entryLong: ['SuperTrend flips bullish (line moves from above price to below)'],
    entryShort: ['SuperTrend flips bearish (line moves from below price to above)'],
    exit: ['Opposite flip'],
    notes: [],
  },
  trend_momentum: {
    indicators: [
      { name: 'EMA (trend)', settings: 'period 50' },
      { name: 'RSI', settings: 'period 14' },
      VOLUME_FILTER_INDICATOR,
    ],
    entryLong: ['Close > EMA(50)', 'RSI Crosses Above 40', VOLUME_FILTER_RULE],
    entryShort: ['Close < EMA(50)', 'RSI Crosses Below 60', VOLUME_FILTER_RULE],
    exit: ['RSI ≥ 70', 'or RSI ≤ 30', 'or trend regime flips (Close Crosses EMA(50) the opposite way)'],
    notes: [],
  },
  volume_climax_reversal: {
    indicators: [{ name: 'Relative Volume', settings: 'period 20, threshold 3.0' }],
    entryLong: ['RVOL > 3.0', 'Low = new session low', 'Close > Open'],
    entryShort: ['RVOL > 3.0', 'High = new session high', 'Close < Open'],
    exit: ['RVOL Crosses Below 1.0'],
    notes: [{ warning: true, text: 'Relative Volume and session running high/low may need a custom formula if not stock indicators on your plan.' }],
  },
  vwap_bounce: {
    indicators: [
      { name: 'VWAP', settings: 'session VWAP' },
      { name: 'EMA (trend)', settings: 'period 50' },
      VOLUME_FILTER_INDICATOR,
    ],
    entryLong: ['Close > EMA(50)', 'Low ≤ VWAP this bar', 'Close > VWAP', 'Close > Open', VOLUME_FILTER_RULE],
    entryShort: ['Close < EMA(50)', 'High ≥ VWAP this bar', 'Close < VWAP', 'Close < Open', VOLUME_FILTER_RULE],
    exit: ['Close Crosses VWAP (opposite direction of entry)'],
    notes: [],
  },
  williams_r_reversal: {
    indicators: [{ name: 'Williams %R', settings: 'period 14' }],
    entryLong: ['%R Crosses Above -80'],
    entryShort: ['%R Crosses Below -20'],
    exit: ['%R Crosses -50'],
    notes: [],
  },
}

export const trendspiderCommonSteps = [
  'Open a chart for the ticker/timeframe, then click the lightning-bolt Strategies icon → + New Strategy.',
  'Add every indicator listed below to the chart first (with the exact settings shown) so they appear in the rule builder dropdowns.',
  "In Entry Conditions, add one rule group for Long and (if applicable) a separate one for Short. Rules in a group are AND'd by default.",
  'In Exit Conditions, add the exit rules -- most strategies exit symmetrically regardless of side.',
  'Set the Direction toggle (Enable Long / Enable Short) to match this strategy.',
  'Save, run Backtest, then manually check 2-3 historical bars where you expect a signal and confirm the trade log marks an entry there.',
]

// Stop-loss/take-profit/trailing-stop and per-trade risk sizing are NOT
// per-strategy parameters in this platform -- they're one global
// Execution Settings config (Settings page) applied uniformly to
// whichever strategy is running (see backend/app/strategies/execution.py).
// So "does this strategy use a stop loss" really means "is one currently
// turned on in Settings" -- this reads that config live so the guide
// only shows real values, matching the platform's own precedence:
// trailing stop > flat % stop > ATR-multiple stop (mutually exclusive),
// take-profit is independent of which stop is active.
export function buildRiskManagementSteps(executionSettings) {
  const {
    atr_period,
    stop_loss_atr_multiple,
    stop_loss_pct,
    take_profit_atr_multiple,
    trailing_stop_atr_multiple,
    risk_per_trade_pct,
  } = executionSettings || {}

  const hasTrailing = trailing_stop_atr_multiple != null
  const hasPctStop = stop_loss_pct != null
  const hasAtrStop = stop_loss_atr_multiple != null
  const hasTakeProfit = take_profit_atr_multiple != null
  const stopActive = hasTrailing || hasPctStop || hasAtrStop

  if (!stopActive && !hasTakeProfit) return null

  const lines = []
  if (hasTrailing) {
    lines.push(`Trailing Stop: ${trailing_stop_atr_multiple}x ATR(${atr_period}) -- trails price as the trade moves in your favor.`)
  } else if (hasPctStop) {
    lines.push(`Stop Loss: fixed ${(stop_loss_pct * 100).toFixed(2)}% from entry.`)
  } else if (hasAtrStop) {
    lines.push(`Stop Loss: ${stop_loss_atr_multiple}x ATR(${atr_period}) from entry.`)
  } else {
    lines.push('Stop Loss: not currently configured.')
  }

  lines.push(
    hasTakeProfit
      ? `Take Profit: ${take_profit_atr_multiple}x ATR(${atr_period}) from entry.`
      : 'Take Profit: not currently configured.'
  )

  if (risk_per_trade_pct != null && stopActive) {
    lines.push(
      `Position sizing: risk ${(risk_per_trade_pct * 100).toFixed(2)}% of account equity per trade, sized off the stop distance above.`
    )
  }

  return lines
}

export const trendspiderRiskManagementSteps = [
  "Open the strategy's Settings panel (top toolbar, next to Explain / Deploy a Bot) -- Stop Loss / Take Profit / Trailing Stop live there, separate from the Entry/Exit condition scripts.",
  'Enable Stop Loss and Take Profit and set them to ATR-based mode (or fixed %, matching whichever is active below).',
  'A trailing stop replaces a fixed stop loss when both would otherwise apply -- only turn on one, matching the platform.',
  'For risk-based sizing, set Position Sizing to "Risk % of Equity" and enter the percentage below -- TrendSpider sizes the position off the stop distance automatically, the same way this platform does.',
]
