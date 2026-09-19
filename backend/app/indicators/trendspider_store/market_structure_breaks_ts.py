"""
Market Structure Breaks -- TrendSpider store indicator by Grant Pratt.

Registered as "market_structure_breaks_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68ab31-market-structure-breaks/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_volume = G["volume"]
    G_describe_indicator("Market Structure Breaks", "price", J.obj(("decimals", "by_symbol"), ("shortName", "MSB")))
    showZigZag = J.get(G_input, "boolean")("Show ZigZag Trend", True)
    showStructureLevels = J.get(G_input, "boolean")("Show Structure Levels", True)
    pivotDisplayType = G_input("Pivot Display Type", "Zones", J.JSArray(["Dots", "Lines", "Zones"]))
    showZones = J.get(G_input, "boolean")("Show Support/Resistance Zones", True)
    extendZonesToRight = J.get(G_input, "boolean")("Extend Zones to Right", True)
    swingLength = G_input("Swing Length", 10, J.obj(("min", 5), ("max", 50)))
    lookbackBars = G_input("Lookback Bars", 50, J.obj(("min", 20), ("max", 100)))
    minSwingStrength = G_input("Min Swing Strength", 0.5, J.obj(("min", 0.1), ("max", 2)))
    signalCooldown = G_input("Signal Cooldown", 5, J.obj(("min", 1), ("max", 20)))
    COLORS = J.obj(("zigzagUp", "#4CAF50"), ("zigzagDown", "#F44336"), ("bullishBreak", "#00E676"), ("bearishBreak", "#FF1744"), ("structureLevels", "#9C27B0"), ("pivotLines", "#9C27B0"), ("resistanceZone", "#FF572220"), ("supportZone", "#4CAF5020"), ("swingHighs", "#FF6B6B"), ("swingLows", "#4ECDC4"))
    swingHighs = G_series_of(None)
    swingLows = G_series_of(None)
    i = swingLength
    while J.lt(i, J.sub(J.get(G_close, "length"), swingLength)):
        isSwingHigh = True
        isSwingLow = True
        j = J.sub(i, swingLength)
        while J.le(j, J.add(i, swingLength)):
            if J.seq(j, i):
                j = J.inc(j)
                continue
            if J.ge(J.get(G_high, j), J.get(G_high, i)):
                isSwingHigh = False
            if J.le(J.get(G_low, j), J.get(G_low, i)):
                isSwingLow = False
            j = J.inc(j)
        if J.truthy(isSwingHigh):
            swingRange = J.sub(J.get(G_high, i), J.get(G_low, i))
            avgRange = J.sub(J.div(J.add(J.add(J.get(G_high, i), J.get(G_high, J.sub(i, 1))), J.get(G_high, J.sub(i, 2))), 3), J.div(J.add(J.add(J.get(G_low, i), J.get(G_low, J.sub(i, 1))), J.get(G_low, J.sub(i, 2))), 3))
            if J.ge(swingRange, J.mul(avgRange, minSwingStrength)):
                J.set(swingHighs, i, J.get(G_high, i))
        if J.truthy(isSwingLow):
            swingRange_2 = J.sub(J.get(G_high, i), J.get(G_low, i))
            avgRange_2 = J.sub(J.div(J.add(J.add(J.get(G_high, i), J.get(G_high, J.sub(i, 1))), J.get(G_high, J.sub(i, 2))), 3), J.div(J.add(J.add(J.get(G_low, i), J.get(G_low, J.sub(i, 1))), J.get(G_low, J.sub(i, 2))), 3))
            if J.ge(swingRange_2, J.mul(avgRange_2, minSwingStrength)):
                J.set(swingLows, i, J.get(G_low, i))
        i = J.inc(i)
    zigzagUpLine = G_series_of(None)
    zigzagDownLine = G_series_of(None)
    if J.truthy(showZigZag):
        lastSwingIndex = (-1)
        lastSwingPrice = 0
        lastSwingType = ""
        i_2 = 0
        while J.lt(i_2, J.get(G_close, "length")):
            currentSwingPrice = None
            currentSwingType = ""
            if (J.get(swingHighs, i_2) is not None):
                currentSwingPrice = J.get(swingHighs, i_2)
                currentSwingType = "high"
            elif (J.get(swingLows, i_2) is not None):
                currentSwingPrice = J.get(swingLows, i_2)
                currentSwingType = "low"
            if ((currentSwingPrice is not None) and J.ge(lastSwingIndex, 0)):
                isUptrend = J.gt(currentSwingPrice, lastSwingPrice)
                targetSeries = (zigzagUpLine if J.truthy(isUptrend) else zigzagDownLine)
                j_2 = lastSwingIndex
                while J.le(j_2, i_2):
                    if J.gt(i_2, lastSwingIndex):
                        progress = J.div(J.sub(j_2, lastSwingIndex), J.sub(i_2, lastSwingIndex))
                        J.set(targetSeries, j_2, J.add(lastSwingPrice, J.mul(J.sub(currentSwingPrice, lastSwingPrice), progress)))
                    j_2 = J.inc(j_2)
            if (currentSwingPrice is not None):
                lastSwingIndex = i_2
                lastSwingPrice = currentSwingPrice
                lastSwingType = currentSwingType
            i_2 = J.inc(i_2)
    structureBreakBullish = G_series_of(None)
    structureBreakBearish = G_series_of(None)
    structureLevels = G_series_of(None)
    resistanceZoneTop = G_series_of(None)
    resistanceZoneBottom = G_series_of(None)
    supportZoneTop = G_series_of(None)
    supportZoneBottom = G_series_of(None)
    lastBullishSignal = J.neg(signalCooldown)
    lastBearishSignal = J.neg(signalCooldown)
    pivotZoneTop1 = G_series_of(None)
    pivotZoneBottom1 = G_series_of(None)
    pivotZoneTop2 = G_series_of(None)
    pivotZoneBottom2 = G_series_of(None)
    pivotZoneTop3 = G_series_of(None)
    pivotZoneBottom3 = G_series_of(None)
    pivotZoneTop4 = G_series_of(None)
    pivotZoneBottom4 = G_series_of(None)
    pivotZoneTop5 = G_series_of(None)
    pivotZoneBottom5 = G_series_of(None)
    pivotZoneTop6 = G_series_of(None)
    pivotZoneBottom6 = G_series_of(None)
    pivotZoneTop7 = G_series_of(None)
    pivotZoneBottom7 = G_series_of(None)
    pivotZoneTop8 = G_series_of(None)
    pivotZoneBottom8 = G_series_of(None)
    candleIndex = J.add(lookbackBars, swingLength)
    while J.lt(candleIndex, J.get(G_close, "length")):
        recentSwingHigh = None
        recentSwingHighIndex = (-1)
        lookback = 1
        while J.le(lookback, lookbackBars):
            checkIndex = J.sub(candleIndex, lookback)
            if (J.ge(checkIndex, 0) and (J.get(swingHighs, checkIndex) is not None)):
                recentSwingHigh = J.get(swingHighs, checkIndex)
                recentSwingHighIndex = checkIndex
                break
            lookback = J.inc(lookback)
        if (((recentSwingHigh is not None) and J.gt(J.get(G_close, candleIndex), recentSwingHigh)) and J.ge(J.sub(candleIndex, lastBullishSignal), signalCooldown)):
            volumeConfirmed = True
            if (J.truthy(G_volume) and (J.get(G_volume, candleIndex) is not None)):
                volumeSum = 0
                volumeCount = 0
                if J.gt(candleIndex, 20):
                    v = J.sub(candleIndex, 20)
                    while J.lt(v, candleIndex):
                        volumeSum = J.add(volumeSum, J.get(G_volume, v))
                        volumeCount = J.inc(volumeCount)
                        v = J.inc(v)
                    avgVolume = J.div(volumeSum, volumeCount)
                    volumeConfirmed = J.gt(J.get(G_volume, candleIndex), J.mul(avgVolume, 0.8))
                else:
                    volumeConfirmed = True
            if J.truthy(volumeConfirmed):
                J.set(structureBreakBullish, candleIndex, J.get(G_high, candleIndex))
                lastBullishSignal = candleIndex
                J.set(structureLevels, candleIndex, recentSwingHigh)
                if J.seq(pivotDisplayType, "Zones"):
                    zoneWidth = J.mul(recentSwingHigh, 0.002)
                    extend = candleIndex
                    while J.lt(extend, J.get(G_close, "length")):
                        if (J.get(pivotZoneTop1, extend) is None):
                            J.set(pivotZoneTop1, extend, J.add(recentSwingHigh, zoneWidth))
                            J.set(pivotZoneBottom1, extend, J.sub(recentSwingHigh, zoneWidth))
                        elif (J.get(pivotZoneTop2, extend) is None):
                            J.set(pivotZoneTop2, extend, J.add(recentSwingHigh, zoneWidth))
                            J.set(pivotZoneBottom2, extend, J.sub(recentSwingHigh, zoneWidth))
                        elif (J.get(pivotZoneTop3, extend) is None):
                            J.set(pivotZoneTop3, extend, J.add(recentSwingHigh, zoneWidth))
                            J.set(pivotZoneBottom3, extend, J.sub(recentSwingHigh, zoneWidth))
                        elif (J.get(pivotZoneTop4, extend) is None):
                            J.set(pivotZoneTop4, extend, J.add(recentSwingHigh, zoneWidth))
                            J.set(pivotZoneBottom4, extend, J.sub(recentSwingHigh, zoneWidth))
                        elif (J.get(pivotZoneTop5, extend) is None):
                            J.set(pivotZoneTop5, extend, J.add(recentSwingHigh, zoneWidth))
                            J.set(pivotZoneBottom5, extend, J.sub(recentSwingHigh, zoneWidth))
                        elif (J.get(pivotZoneTop6, extend) is None):
                            J.set(pivotZoneTop6, extend, J.add(recentSwingHigh, zoneWidth))
                            J.set(pivotZoneBottom6, extend, J.sub(recentSwingHigh, zoneWidth))
                        elif (J.get(pivotZoneTop7, extend) is None):
                            J.set(pivotZoneTop7, extend, J.add(recentSwingHigh, zoneWidth))
                            J.set(pivotZoneBottom7, extend, J.sub(recentSwingHigh, zoneWidth))
                        elif (J.get(pivotZoneTop8, extend) is None):
                            J.set(pivotZoneTop8, extend, J.add(recentSwingHigh, zoneWidth))
                            J.set(pivotZoneBottom8, extend, J.sub(recentSwingHigh, zoneWidth))
                        extend = J.inc(extend)
                if J.truthy(showZones):
                    zoneWidth_2 = J.mul(recentSwingHigh, 0.002)
                    extend_2 = candleIndex
                    while J.lt(extend_2, J.get(G_close, "length")):
                        J.set(resistanceZoneTop, extend_2, J.add(recentSwingHigh, zoneWidth_2))
                        J.set(resistanceZoneBottom, extend_2, J.sub(recentSwingHigh, zoneWidth_2))
                        extend_2 = J.inc(extend_2)
        recentSwingLow = None
        recentSwingLowIndex = (-1)
        lookback_2 = 1
        while J.le(lookback_2, lookbackBars):
            checkIndex_2 = J.sub(candleIndex, lookback_2)
            if (J.ge(checkIndex_2, 0) and (J.get(swingLows, checkIndex_2) is not None)):
                recentSwingLow = J.get(swingLows, checkIndex_2)
                recentSwingLowIndex = checkIndex_2
                break
            lookback_2 = J.inc(lookback_2)
        if (((recentSwingLow is not None) and J.lt(J.get(G_close, candleIndex), recentSwingLow)) and J.ge(J.sub(candleIndex, lastBearishSignal), signalCooldown)):
            volumeConfirmed_2 = True
            if (J.truthy(G_volume) and (J.get(G_volume, candleIndex) is not None)):
                volumeSum_2 = 0
                volumeCount_2 = 0
                if J.gt(candleIndex, 20):
                    v_2 = J.sub(candleIndex, 20)
                    while J.lt(v_2, candleIndex):
                        volumeSum_2 = J.add(volumeSum_2, J.get(G_volume, v_2))
                        volumeCount_2 = J.inc(volumeCount_2)
                        v_2 = J.inc(v_2)
                    avgVolume_2 = J.div(volumeSum_2, volumeCount_2)
                    volumeConfirmed_2 = J.gt(J.get(G_volume, candleIndex), J.mul(avgVolume_2, 0.8))
                else:
                    volumeConfirmed_2 = True
            if J.truthy(volumeConfirmed_2):
                J.set(structureBreakBearish, candleIndex, J.get(G_low, candleIndex))
                lastBearishSignal = candleIndex
                J.set(structureLevels, candleIndex, recentSwingLow)
                if J.seq(pivotDisplayType, "Zones"):
                    zoneWidth_3 = J.mul(recentSwingLow, 0.002)
                    extend_3 = candleIndex
                    while J.lt(extend_3, J.get(G_close, "length")):
                        if (J.get(pivotZoneTop1, extend_3) is None):
                            J.set(pivotZoneTop1, extend_3, J.add(recentSwingLow, zoneWidth_3))
                            J.set(pivotZoneBottom1, extend_3, J.sub(recentSwingLow, zoneWidth_3))
                        elif (J.get(pivotZoneTop2, extend_3) is None):
                            J.set(pivotZoneTop2, extend_3, J.add(recentSwingLow, zoneWidth_3))
                            J.set(pivotZoneBottom2, extend_3, J.sub(recentSwingLow, zoneWidth_3))
                        elif (J.get(pivotZoneTop3, extend_3) is None):
                            J.set(pivotZoneTop3, extend_3, J.add(recentSwingLow, zoneWidth_3))
                            J.set(pivotZoneBottom3, extend_3, J.sub(recentSwingLow, zoneWidth_3))
                        elif (J.get(pivotZoneTop4, extend_3) is None):
                            J.set(pivotZoneTop4, extend_3, J.add(recentSwingLow, zoneWidth_3))
                            J.set(pivotZoneBottom4, extend_3, J.sub(recentSwingLow, zoneWidth_3))
                        elif (J.get(pivotZoneTop5, extend_3) is None):
                            J.set(pivotZoneTop5, extend_3, J.add(recentSwingLow, zoneWidth_3))
                            J.set(pivotZoneBottom5, extend_3, J.sub(recentSwingLow, zoneWidth_3))
                        elif (J.get(pivotZoneTop6, extend_3) is None):
                            J.set(pivotZoneTop6, extend_3, J.add(recentSwingLow, zoneWidth_3))
                            J.set(pivotZoneBottom6, extend_3, J.sub(recentSwingLow, zoneWidth_3))
                        elif (J.get(pivotZoneTop7, extend_3) is None):
                            J.set(pivotZoneTop7, extend_3, J.add(recentSwingLow, zoneWidth_3))
                            J.set(pivotZoneBottom7, extend_3, J.sub(recentSwingLow, zoneWidth_3))
                        elif (J.get(pivotZoneTop8, extend_3) is None):
                            J.set(pivotZoneTop8, extend_3, J.add(recentSwingLow, zoneWidth_3))
                            J.set(pivotZoneBottom8, extend_3, J.sub(recentSwingLow, zoneWidth_3))
                        extend_3 = J.inc(extend_3)
                if J.truthy(showZones):
                    zoneWidth_4 = J.mul(recentSwingLow, 0.002)
                    extend_4 = candleIndex
                    while J.lt(extend_4, J.get(G_close, "length")):
                        J.set(supportZoneTop, extend_4, J.add(recentSwingLow, zoneWidth_4))
                        J.set(supportZoneBottom, extend_4, J.sub(recentSwingLow, zoneWidth_4))
                        extend_4 = J.inc(extend_4)
        candleIndex = J.inc(candleIndex)
    if J.seq(pivotDisplayType, "Zones"):
        G_fill(G_paint(pivotZoneTop1, J.obj(("hidden", True))), G_paint(pivotZoneBottom1, J.obj(("hidden", True))), "#9C27B050", J.undefined, "Pivot Zone 1")
        G_fill(G_paint(pivotZoneTop2, J.obj(("hidden", True))), G_paint(pivotZoneBottom2, J.obj(("hidden", True))), "#9C27B050", J.undefined, "Pivot Zone 2")
        G_fill(G_paint(pivotZoneTop3, J.obj(("hidden", True))), G_paint(pivotZoneBottom3, J.obj(("hidden", True))), "#9C27B050", J.undefined, "Pivot Zone 3")
        G_fill(G_paint(pivotZoneTop4, J.obj(("hidden", True))), G_paint(pivotZoneBottom4, J.obj(("hidden", True))), "#9C27B050", J.undefined, "Pivot Zone 4")
        G_fill(G_paint(pivotZoneTop5, J.obj(("hidden", True))), G_paint(pivotZoneBottom5, J.obj(("hidden", True))), "#9C27B050", J.undefined, "Pivot Zone 5")
        G_fill(G_paint(pivotZoneTop6, J.obj(("hidden", True))), G_paint(pivotZoneBottom6, J.obj(("hidden", True))), "#9C27B050", J.undefined, "Pivot Zone 6")
        G_fill(G_paint(pivotZoneTop7, J.obj(("hidden", True))), G_paint(pivotZoneBottom7, J.obj(("hidden", True))), "#9C27B050", J.undefined, "Pivot Zone 7")
        G_fill(G_paint(pivotZoneTop8, J.obj(("hidden", True))), G_paint(pivotZoneBottom8, J.obj(("hidden", True))), "#9C27B050", J.undefined, "Pivot Zone 8")
    if J.truthy(showZigZag):
        G_paint(zigzagUpLine, "ZigZag Up", J.get(COLORS, "zigzagUp"))
        G_paint(zigzagDownLine, "ZigZag Down", J.get(COLORS, "zigzagDown"))
    if J.truthy(showZones):
        G_fill(G_paint(resistanceZoneTop, J.obj(("hidden", True))), G_paint(resistanceZoneBottom, J.obj(("hidden", True))), J.get(COLORS, "resistanceZone"), J.undefined, "Resistance Zones")
        G_fill(G_paint(supportZoneTop, J.obj(("hidden", True))), G_paint(supportZoneBottom, J.obj(("hidden", True))), J.get(COLORS, "supportZone"), J.undefined, "Support Zones")
    G_paint(structureLevels, "Pivot Levels", J.get(COLORS, "structureLevels"))
    G_paint(swingHighs, "Swing Highs", J.get(COLORS, "swingHighs"))
    G_paint(swingLows, "Swing Lows", J.get(COLORS, "swingLows"))
    G_paint(structureBreakBullish, "Bullish Structure Break", J.get(COLORS, "bullishBreak"))
    G_paint(structureBreakBearish, "Bearish Structure Break", J.get(COLORS, "bearishBreak"))


register_store_indicator(
    script,
    name='market_structure_breaks_TS',
    title='Market Structure Breaks',
    developer='Grant Pratt',
    url='https://trendspider.com/trading-tools-store/indicators/68ab31-market-structure-breaks/',
    position='price',
    inputs=[{'id': 'show_zigzag_trend', 'title': 'Show ZigZag Trend', 'type': 'boolean', 'default': True}, {'id': 'show_structure_levels', 'title': 'Show Structure Levels', 'type': 'boolean', 'default': True}, {'id': 'pivot_display_type', 'title': 'Pivot Display Type', 'type': 'select_wide', 'default': 'Zones', 'options': ['Dots', 'Lines', 'Zones']}, {'id': 'show_support_resistance_zones', 'title': 'Show Support/Resistance Zones', 'type': 'boolean', 'default': True}, {'id': 'extend_zones_to_right', 'title': 'Extend Zones to Right', 'type': 'boolean', 'default': True}, {'id': 'swing_length', 'title': 'Swing Length', 'type': 'number', 'default': 10}, {'id': 'lookback_bars', 'title': 'Lookback Bars', 'type': 'number', 'default': 50}, {'id': 'min_swing_strength', 'title': 'Min Swing Strength', 'type': 'number', 'default': 0.5}, {'id': 'signal_cooldown', 'title': 'Signal Cooldown', 'type': 'number', 'default': 5}],
    outputs=['line_1', 'line_2', 'line_4', 'line_5', 'line_7', 'line_8', 'line_10', 'line_11', 'line_13', 'line_14', 'line_16', 'line_17', 'line_19', 'line_20', 'line_22', 'line_23', 'zigzag_up', 'zigzag_down', 'line_27', 'line_28', 'line_30', 'line_31', 'pivot_levels', 'swing_highs', 'swing_lows', 'bullish_structure_break', 'bearish_structure_break'],
    signals=[],
    requires=[],
    parity='exact',
)
