"""
Market Absorption & Efficiency Classifier -- TrendSpider store indicator by Gustivus.

Registered as "market_absorption_efficiency_classifier_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6960ab-market-absorption-efficiency-classifier/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_volume = G["volume"]
    def calculateVWAP(startIdx=J.undefined, endIdx=J.undefined, *_args):
        sumPV = 0
        sumV = 0
        i = startIdx
        while (J.le(i, endIdx) and J.lt(i, J.get(G_close, "length"))):
            typicalPrice = J.div(J.add(J.add(J.get(G_high, i), J.get(G_low, i)), J.get(G_close, i)), 3)
            vol = (_t1 if J.truthy(_t1 := J.get(G_volume, i)) else 0)
            sumPV = J.add(sumPV, J.mul(typicalPrice, vol))
            sumV = J.add(sumV, vol)
            i = J.inc(i)
        return (J.div(sumPV, sumV) if J.gt(sumV, 0) else J.get(G_close, endIdx))
    def calculateEfficiency(idx=J.undefined, period=J.undefined, *_args):
        if J.lt(idx, period):
            return 0
        netMove = J.get(G_Math, "abs")(J.sub(J.get(G_close, idx), J.get(G_close, J.sub(idx, period))))
        totalMove = 0
        i = 1
        while J.le(i, period):
            totalMove = J.add(totalMove, J.get(G_Math, "abs")(J.sub(J.get(G_close, J.add(J.sub(idx, i), 1)), J.get(G_close, J.sub(idx, i)))))
            i = J.inc(i)
        return (J.div(netMove, totalMove) if J.gt(totalMove, 0) else 0)
    def calculateAverageVolume(idx=J.undefined, window=J.undefined, *_args):
        if J.lt(idx, window):
            return (_t1 if J.truthy(_t1 := J.get(G_volume, idx)) else 0)
        avgVolume = 0
        i = 1
        while J.le(i, window):
            avgVolume = J.add(avgVolume, (_t2 if J.truthy(_t2 := J.get(G_volume, J.sub(idx, i))) else 0))
            i = J.inc(i)
        return J.div(avgVolume, window)
    def calculateAverageRange(idx=J.undefined, period=J.undefined, *_args):
        if J.lt(idx, period):
            return J.sub(J.get(G_high, idx), J.get(G_low, idx))
        avgRange = 0
        i = 1
        while J.le(i, period):
            avgRange = J.add(avgRange, J.sub(J.get(G_high, J.sub(idx, i)), J.get(G_low, J.sub(idx, i))))
            i = J.inc(i)
        return J.div(avgRange, period)
    def detectAbsorption(idx=J.undefined, window=J.undefined, *_args):
        if J.lt(idx, window):
            return J.obj(("type", "none"), ("strength", 0))
        avgVolume = calculateAverageVolume(idx, window)
        currentVol = (_t1 if J.truthy(_t1 := J.get(G_volume, idx)) else 0)
        isHighVolume = J.gt(currentVol, J.mul(avgVolume, volumeMultiple))
        range = J.sub(J.get(G_high, idx), J.get(G_low, idx))
        body = J.get(G_Math, "abs")(J.sub(J.get(G_close, idx), J.get(G_open, idx)))
        upperWick = J.sub(J.get(G_high, idx), J.get(G_Math, "max")(J.get(G_close, idx), J.get(G_open, idx)))
        lowerWick = J.sub(J.get(G_Math, "min")(J.get(G_close, idx), J.get(G_open, idx)), J.get(G_low, idx))
        avgRange = calculateAverageRange(idx, J.get(G_Math, "min")(14, idx))
        if J.truthy(isHighVolume):
            if J.lt(range, J.mul(avgRange, 0.7)):
                closePosition = (J.div(J.sub(J.get(G_close, idx), J.get(G_low, idx)), range) if J.gt(range, 0) else 0.5)
                if J.gt(closePosition, 0.7):
                    return J.obj(("type", "bullish_absorption"), ("strength", J.div(currentVol, avgVolume)))
                elif J.lt(closePosition, 0.3):
                    return J.obj(("type", "bearish_absorption"), ("strength", J.div(currentVol, avgVolume)))
                else:
                    return J.obj(("type", "churning"), ("strength", J.div(currentVol, avgVolume)))
            if (J.gt(lowerWick, J.mul(body, 2)) and J.gt(lowerWick, J.mul(upperWick, 2))):
                return J.obj(("type", "bullish_absorption"), ("strength", J.div(currentVol, avgVolume)))
            elif (J.gt(upperWick, J.mul(body, 2)) and J.gt(upperWick, J.mul(lowerWick, 2))):
                return J.obj(("type", "bearish_absorption"), ("strength", J.div(currentVol, avgVolume)))
        return J.obj(("type", "none"), ("strength", 0))
    def volumePriceAnalysis(idx=J.undefined, period=J.undefined, *_args):
        if J.lt(idx, period):
            return J.obj(("divergence", False), ("type", "none"))
        recentPriceMove = J.sub(J.get(G_close, idx), J.get(G_close, J.sub(idx, J.get(G_Math, "floor")(J.div(period, 2)))))
        recentVolTrend = J.sub(J.get(G_volume, idx), J.get(G_volume, J.sub(idx, J.get(G_Math, "floor")(J.div(period, 2)))))
        if (J.lt(recentPriceMove, 0) and J.gt(recentVolTrend, 0)):
            return J.obj(("divergence", True), ("type", "bullish"))
        if (J.gt(recentPriceMove, 0) and J.lt(recentVolTrend, 0)):
            return J.obj(("divergence", True), ("type", "bearish"))
        return J.obj(("divergence", False), ("type", "none"))
    def determineMarketState(idx=J.undefined, absorption=J.undefined, efficiency=J.undefined, vpAnalysis=J.undefined, avgVolume=J.undefined, avgRange=J.undefined, *_args):
        currentVol = (_t1 if J.truthy(_t1 := J.get(G_volume, idx)) else 0)
        currentRange = J.sub(J.get(G_high, idx), J.get(G_low, idx))
        bodySize = J.get(G_Math, "abs")(J.sub(J.get(G_close, idx), J.get(G_open, idx)))
        priceDirection = (1 if J.gt(J.get(G_close, idx), J.get(G_open, idx)) else (-1))
        if J.seq(J.get(absorption, "type"), "bullish_absorption"):
            return "DEMAND_ABSORPTION"
        elif J.seq(J.get(absorption, "type"), "bearish_absorption"):
            return "SUPPLY_ABSORPTION"
        elif J.seq(J.get(absorption, "type"), "churning"):
            return "CONSOLIDATION"
        if J.gt(efficiency, 0.7):
            return ("EFFICIENT_UP" if J.gt(priceDirection, 0) else "EFFICIENT_DOWN")
        if ((((J.lt(efficiency, 0.2) and J.gt(currentVol, J.mul(avgVolume, exhaustionVolumeMultiple))) and J.lt(bodySize, J.mul(avgRange, 0.3))) and J.gt(currentRange, J.mul(avgRange, 1.5))) and J.truthy(J.get(vpAnalysis, "divergence"))):
            return "EXHAUSTION"
        return "NEUTRAL"
    G_describe_indicator("Market Absorption & Efficiency Classifier", "overlay", J.obj(("shortName", "MAEC")))
    absorptionWindow = J.get(G_input, "number")("Absorption Window", 20, J.obj(("min", 10), ("max", 50)))
    efficiencyPeriod = J.get(G_input, "number")("Efficiency Period", 14, J.obj(("min", 5), ("max", 30)))
    volumeMultiple = J.get(G_input, "number")("High Volume Multiple", 1.5, J.obj(("min", 1.2), ("max", 3), ("step", 0.1)))
    exhaustionVolumeMultiple = J.get(G_input, "number")("Exhaustion Volume Multiple", 2.5, J.obj(("min", 2), ("max", 4), ("step", 0.1)))
    showAbsorptionLevels = J.get(G_input, "boolean")("Show Absorption Levels", True)
    paintCandles = J.get(G_input, "boolean")("Paint Candles", True)
    showDivergences = J.get(G_input, "boolean")("Show Volume Divergences", True)
    purpleSequenceMin = J.get(G_input, "number")("Purple Sequence Minimum", 2, J.obj(("min", 2), ("max", 5)))
    COLORS = J.obj(("DEMAND_ABSORPTION", "#00FF88"), ("SUPPLY_ABSORPTION", "#0B3D91"), ("EFFICIENT_UP", "#00A8E1"), ("EFFICIENT_DOWN", "#BF00FF"), ("CONSOLIDATION", "#FF6B35"), ("EXHAUSTION", "#FF003F"), ("NEUTRAL", "#A0A0A0"))
    marketState = J.JSArray([])
    absorptionLevels = G_series_of(None)
    efficiencyRatio = G_series_of(0)
    volumeDivergence = G_series_of(False)
    purpleSequence = G_series_of(0)
    absorptionZones = J.JSArray([])
    purpleCount = 0
    maxPurpleStreak = 0
    i = 0
    while J.lt(i, J.get(G_time, "length")):
        efficiency = calculateEfficiency(i, efficiencyPeriod)
        J.set(efficiencyRatio, i, efficiency)
        absorption = detectAbsorption(i, absorptionWindow)
        vpAnalysis = volumePriceAnalysis(i, efficiencyPeriod)
        avgVolume = calculateAverageVolume(i, absorptionWindow)
        avgRange = calculateAverageRange(i, 14)
        state = determineMarketState(i, absorption, efficiency, vpAnalysis, avgVolume, avgRange)
        J.set(marketState, i, state)
        if J.seq(state, "EFFICIENT_DOWN"):
            purpleCount = J.inc(purpleCount)
            J.set(purpleSequence, i, purpleCount)
            maxPurpleStreak = J.get(G_Math, "max")(maxPurpleStreak, purpleCount)
        else:
            if J.ge(purpleCount, purpleSequenceMin):
                J.set(purpleSequence, i, J.neg(purpleCount))
            purpleCount = 0
        if (J.truthy(J.get(vpAnalysis, "divergence")) and J.truthy(showDivergences)):
            J.set(volumeDivergence, i, True)
        if ((J.sne(J.get(absorption, "type"), "none") and J.gt(J.get(absorption, "strength"), 2)) and J.truthy(showAbsorptionLevels)):
            if J.seq(J.get(absorption, "type"), "bullish_absorption"):
                J.get(absorptionZones, "push")(J.obj(("index", i), ("price", J.get(G_low, i)), ("type", "support"), ("strength", J.get(absorption, "strength"))))
            elif J.seq(J.get(absorption, "type"), "bearish_absorption"):
                J.get(absorptionZones, "push")(J.obj(("index", i), ("price", J.get(G_high, i)), ("type", "resistance"), ("strength", J.get(absorption, "strength"))))
        i = J.inc(i)
    def _f1(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(b, "index"), J.get(a, "index"))
    J.get(absorptionZones, "sort")(_f1)
    recentZones = J.get(absorptionZones, "slice")(0, 5)
    supportLevel1 = G_series_of(None)
    supportLevel2 = G_series_of(None)
    resistanceLevel1 = G_series_of(None)
    resistanceLevel2 = G_series_of(None)
    def _f2(z=J.undefined, *_args):
        return J.seq(J.get(z, "type"), "support")
    supports = J.get(recentZones, "filter")(_f2)
    def _f3(z=J.undefined, *_args):
        return J.seq(J.get(z, "type"), "resistance")
    resistances = J.get(recentZones, "filter")(_f3)
    if J.gt(J.get(supports, "length"), 0):
        i_2 = J.get(J.get(supports, 0), "index")
        while J.lt(i_2, J.get(G_time, "length")):
            J.set(supportLevel1, i_2, J.get(J.get(supports, 0), "price"))
            i_2 = J.inc(i_2)
    if J.gt(J.get(supports, "length"), 1):
        i_3 = J.get(J.get(supports, 1), "index")
        while J.lt(i_3, J.get(G_time, "length")):
            J.set(supportLevel2, i_3, J.get(J.get(supports, 1), "price"))
            i_3 = J.inc(i_3)
    if J.gt(J.get(resistances, "length"), 0):
        i_4 = J.get(J.get(resistances, 0), "index")
        while J.lt(i_4, J.get(G_time, "length")):
            J.set(resistanceLevel1, i_4, J.get(J.get(resistances, 0), "price"))
            i_4 = J.inc(i_4)
    if J.gt(J.get(resistances, "length"), 1):
        i_5 = J.get(J.get(resistances, 1), "index")
        while J.lt(i_5, J.get(G_time, "length")):
            J.set(resistanceLevel2, i_5, J.get(J.get(resistances, 1), "price"))
            i_5 = J.inc(i_5)
    if J.truthy(paintCandles):
        candleColors = J.JSArray([])
        i_6 = 0
        while J.lt(i_6, J.get(G_time, "length")):
            _t4 = J.get(marketState, i_6)
            if J.seq(_t4, "DEMAND_ABSORPTION"):
                _t5 = 0
            elif J.seq(_t4, "SUPPLY_ABSORPTION"):
                _t5 = 1
            elif J.seq(_t4, "EFFICIENT_UP"):
                _t5 = 2
            elif J.seq(_t4, "EFFICIENT_DOWN"):
                _t5 = 3
            elif J.seq(_t4, "CONSOLIDATION"):
                _t5 = 4
            elif J.seq(_t4, "EXHAUSTION"):
                _t5 = 5
            else:
                _t5 = 6
            _c6 = False
            for _once in (0,):
                if _t5 <= 0:
                    J.set(candleColors, i_6, J.get(COLORS, "DEMAND_ABSORPTION"))
                    break
                if _t5 <= 1:
                    J.set(candleColors, i_6, J.get(COLORS, "SUPPLY_ABSORPTION"))
                    break
                if _t5 <= 2:
                    J.set(candleColors, i_6, J.get(COLORS, "EFFICIENT_UP"))
                    break
                if _t5 <= 3:
                    J.set(candleColors, i_6, J.get(COLORS, "EFFICIENT_DOWN"))
                    break
                if _t5 <= 4:
                    J.set(candleColors, i_6, J.get(COLORS, "CONSOLIDATION"))
                    break
                if _t5 <= 5:
                    J.set(candleColors, i_6, J.get(COLORS, "EXHAUSTION"))
                    break
                if _t5 <= 6:
                    J.set(candleColors, i_6, None)
                pass
            i_6 = J.inc(i_6)
        G_color_candles(candleColors)
    if J.truthy(showAbsorptionLevels):
        G_paint(supportLevel1, J.obj(("name", "Primary Support"), ("color", J.get(COLORS, "DEMAND_ABSORPTION")), ("style", "line"), ("width", 2), ("opacity", 0.6)))
        G_paint(supportLevel2, J.obj(("name", "Secondary Support"), ("color", J.get(COLORS, "DEMAND_ABSORPTION")), ("style", "dotted"), ("width", 1), ("opacity", 0.4)))
        G_paint(resistanceLevel1, J.obj(("name", "Primary Resistance"), ("color", J.get(COLORS, "SUPPLY_ABSORPTION")), ("style", "line"), ("width", 2), ("opacity", 0.6)))
        G_paint(resistanceLevel2, J.obj(("name", "Secondary Resistance"), ("color", J.get(COLORS, "SUPPLY_ABSORPTION")), ("style", "dotted"), ("width", 1), ("opacity", 0.4)))
    demandAbsorption = G_series_of(False)
    supplyAbsorption = G_series_of(False)
    efficientUp = G_series_of(False)
    efficientDown = G_series_of(False)
    consolidation = G_series_of(False)
    exhaustion = G_series_of(False)
    purpleWarning = G_series_of(False)
    purpleReversal = G_series_of(False)
    purpleExtreme = G_series_of(False)
    efficiencyBreakout = G_series_of(False)
    absorptionBreakdown = G_series_of(False)
    i_7 = 1
    while J.lt(i_7, J.get(G_time, "length")):
        currentState = J.get(marketState, i_7)
        prevState = J.get(marketState, J.sub(i_7, 1))
        J.set(demandAbsorption, i_7, J.seq(currentState, "DEMAND_ABSORPTION"))
        J.set(supplyAbsorption, i_7, J.seq(currentState, "SUPPLY_ABSORPTION"))
        J.set(efficientUp, i_7, J.seq(currentState, "EFFICIENT_UP"))
        J.set(efficientDown, i_7, J.seq(currentState, "EFFICIENT_DOWN"))
        J.set(consolidation, i_7, J.seq(currentState, "CONSOLIDATION"))
        J.set(exhaustion, i_7, J.seq(currentState, "EXHAUSTION"))
        if J.seq(J.get(purpleSequence, i_7), purpleSequenceMin):
            J.set(purpleWarning, i_7, True)
        if J.ge(J.get(purpleSequence, i_7), J.add(purpleSequenceMin, 1)):
            J.set(purpleReversal, i_7, True)
        if J.ge(J.get(purpleSequence, i_7), 4):
            J.set(purpleExtreme, i_7, True)
        if (J.lt(J.get(purpleSequence, i_7), 0) and J.ge(J.get(G_Math, "abs")(J.get(purpleSequence, i_7)), purpleSequenceMin)):
            J.set(purpleReversal, i_7, True)
        if (((J.seq(currentState, "EFFICIENT_UP") or J.seq(currentState, "EFFICIENT_DOWN")) and J.gt(J.get(efficiencyRatio, i_7), 0.8)) and J.lt(J.get(efficiencyRatio, J.sub(i_7, 1)), 0.5)):
            J.set(efficiencyBreakout, i_7, True)
        if (J.seq(currentState, "EXHAUSTION") and (J.seq(prevState, "DEMAND_ABSORPTION") or J.seq(prevState, "SUPPLY_ABSORPTION"))):
            J.set(absorptionBreakdown, i_7, True)
        i_7 = J.inc(i_7)
    G_register_signal(demandAbsorption, "\ud83d\udfe2 GREEN CANDLE - Demand Absorption")
    G_register_signal(supplyAbsorption, "\ud83d\udd35 NAVY CANDLE - Supply Absorption")
    G_register_signal(efficientUp, "\ud83d\udd37 LIGHT BLUE CANDLE - Efficient Uptrend")
    G_register_signal(efficientDown, "\ud83d\udfe3 PURPLE CANDLE - Efficient Decline")
    G_register_signal(consolidation, "\ud83d\udfe0 ORANGE CANDLE - High Volume Consolidation")
    G_register_signal(exhaustion, "\ud83d\udd34 RED CANDLE - Extreme Exhaustion")
    G_register_signal(efficiencyBreakout, "⚡ Efficiency Surge - Directional Acceleration")
    G_register_signal(absorptionBreakdown, "\ud83d\udca5 Absorption Failure - Support/Resistance Break")
    G_register_signal(volumeDivergence, "\ud83d\udcca Volume/Price Divergence - Trend Inconsistency")


register_store_indicator(
    script,
    name='market_absorption_efficiency_classifier_TS',
    title='Market Absorption & Efficiency Classifier',
    developer='Gustivus',
    url='https://trendspider.com/trading-tools-store/indicators/6960ab-market-absorption-efficiency-classifier/',
    position='price',
    inputs=[{'id': 'absorption_window', 'title': 'Absorption Window', 'type': 'number', 'default': 20}, {'id': 'efficiency_period', 'title': 'Efficiency Period', 'type': 'number', 'default': 14}, {'id': 'high_volume_multiple', 'title': 'High Volume Multiple', 'type': 'number', 'default': 1.5}, {'id': 'exhaustion_volume_multiple', 'title': 'Exhaustion Volume Multiple', 'type': 'number', 'default': 2.5}, {'id': 'show_absorption_levels', 'title': 'Show Absorption Levels', 'type': 'boolean', 'default': True}, {'id': 'paint_candles', 'title': 'Paint Candles', 'type': 'boolean', 'default': True}, {'id': 'show_volume_divergences', 'title': 'Show Volume Divergences', 'type': 'boolean', 'default': True}, {'id': 'purple_sequence_minimum', 'title': 'Purple Sequence Minimum', 'type': 'number', 'default': 2}],
    outputs=['cdl', 'primary_support', 'secondary_support', 'primary_resistance', 'secondary_resistance', '___green_candle___demand_absorption', '___navy_candle___supply_absorption', '___light_blue_candle___efficient_uptrend', '___purple_candle___efficient_decline', '___orange_candle___high_volume_consolidation', '___red_candle___extreme_exhaustion', '__efficiency_surge___directional_acceleration', '___absorption_failure___support_resistance_break', '___volume_price_divergence___trend_inconsistency'],
    signals=['___green_candle___demand_absorption', '___navy_candle___supply_absorption', '___light_blue_candle___efficient_uptrend', '___purple_candle___efficient_decline', '___orange_candle___high_volume_consolidation', '___red_candle___extreme_exhaustion', '__efficiency_surge___directional_acceleration', '___absorption_failure___support_resistance_break', '___volume_price_divergence___trend_inconsistency'],
    requires=[],
    parity='exact',
)
