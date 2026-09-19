"""
Darvas Box Indicator -- TrendSpider store indicator by TrendSpider.

Registered as "darvas_box_indicator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69a876-darvas-box-indicator/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("Darvas Box Indicator")
    confirmBars = J.get(G_input, "number")("Confirmation Bars", 3, J.obj(("min", 1)))
    showLabels = J.seq(J.get(G_input, "select")("Show Labels", "Yes", J.JSArray(["Yes", "No"])), "Yes")
    breakoutUsesClose = J.seq(J.get(G_input, "select")("Breakout Uses Close", "Yes", J.JSArray(["Yes", "No"])), "Yes")
    useRVOLForBreakout = J.seq(J.get(G_input, "select")("Use RVOL for Breakout", "No", J.JSArray(["Yes", "No"])), "Yes")
    rvolLookback = J.get(G_input, "number")("RVOL Lookback", 20, J.obj(("min", 1)))
    rvolThreshold = J.get(G_input, "number")("RVOL Threshold", 1, J.obj(("min", 0.1)))
    G_assert(J.ge(confirmBars, 1), "Confirmation bars must be at least 1")
    G_assert(J.ge(J.get(G_close, "length"), 52), "Need at least 52 bars of data for this indicator")
    rollingHigh52 = G_highest(G_high, 52)
    rvol = (G_div(G_volume, G_sma(G_volume, rvolLookback)) if J.truthy(useRVOLForBreakout) else G_series_of(1))
    candidateActive = False
    candidateTop = None
    candidateBottom = None
    candidateHighIndex = None
    confirmCount = 0
    boxActive = False
    boxTop = None
    boxBottom = None
    boxBottomActive = False
    persistentBoxBottom = None
    prevRollingHigh = None
    rollingHighSeries = G_series_of(None)
    boxTopSeries = G_series_of(None)
    boxBottomSeries = G_series_of(None)
    boxFormedSignal = G_series_of(0)
    boxBreakoutSignal = G_series_of(0)
    boxBreakdownSignal = G_series_of(0)
    boxFormedLabels = G_series_of(None)
    boxBreakoutLabels = G_series_of(None)
    boxBreakdownLabels = G_series_of(None)
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        J.set(rollingHighSeries, i, J.get(rollingHigh52, i))
        if (J.truthy(boxBottomActive) and J.lt(J.get(G_close, i), persistentBoxBottom)):
            J.set(boxBreakdownSignal, i, 1)
            if J.truthy(showLabels):
                J.set(boxBreakdownLabels, i, "BD")
            boxBottomActive = False
            persistentBoxBottom = None
            if J.truthy(boxActive):
                boxActive = False
                boxTop = None
                boxBottom = None
        isNew52High = ((_t2 if J.truthy(_t2 := (prevRollingHigh is None)) else J.gt(J.get(G_high, i), prevRollingHigh)) if J.truthy(_t1 := J.seq(J.get(G_high, i), J.get(rollingHigh52, i))) else _t1)
        if ((J.truthy(isNew52High) and (not J.truthy(boxActive))) and (not J.truthy(candidateActive))):
            candidateActive = True
            candidateTop = J.get(G_high, i)
            candidateBottom = J.get(G_low, i)
            candidateHighIndex = i
            confirmCount = 0
            boxBottomActive = False
            persistentBoxBottom = None
        if (J.truthy(candidateActive) and J.gt(i, candidateHighIndex)):
            if J.gt(J.get(G_high, i), candidateTop):
                candidateTop = J.get(G_high, i)
                candidateBottom = J.get(G_low, i)
                candidateHighIndex = i
                confirmCount = 0
            else:
                confirmCount = J.inc(confirmCount)
                candidateBottom = J.get(G_Math, "min")(candidateBottom, J.get(G_low, i))
                if J.ge(confirmCount, confirmBars):
                    boxTop = candidateTop
                    boxBottom = candidateBottom
                    boxActive = True
                    candidateActive = False
                    boxBottomActive = True
                    persistentBoxBottom = boxBottom
                    j = candidateHighIndex
                    while J.le(j, i):
                        J.set(boxTopSeries, j, boxTop)
                        J.set(boxBottomSeries, j, boxBottom)
                        j = J.inc(j)
                    J.set(boxFormedSignal, i, 1)
                    if J.truthy(showLabels):
                        J.set(boxFormedLabels, i, "Box")
        if J.truthy(boxActive):
            J.set(boxTopSeries, i, boxTop)
            priceBreakout = (J.gt(J.get(G_close, i), boxTop) if J.truthy(breakoutUsesClose) else J.gt(J.get(G_high, i), boxTop))
            rvolCondition = ((J.ge(J.get(rvol, i), rvolThreshold) if J.truthy(_t3 := (J.get(rvol, i) is not None)) else _t3) if J.truthy(useRVOLForBreakout) else True)
            if (J.truthy(priceBreakout) and J.truthy(rvolCondition)):
                J.set(boxBreakoutSignal, i, 1)
                if J.truthy(showLabels):
                    J.set(boxBreakoutLabels, i, "BO")
                boxActive = False
                boxTop = None
                boxBottom = None
        if J.truthy(boxBottomActive):
            J.set(boxBottomSeries, i, persistentBoxBottom)
        prevRollingHigh = J.get(rollingHigh52, i)
        i = J.inc(i)
    G_paint(rollingHighSeries, J.obj(("name", "Rolling High 52"), ("color", "#888888"), ("thickness", 1), ("style", "line")))
    G_paint(boxTopSeries, J.obj(("name", "Box Top"), ("color", "#0066ff"), ("thickness", 2), ("style", "ladder")))
    G_paint(boxBottomSeries, J.obj(("name", "Box Bottom"), ("color", "#0066ff"), ("thickness", 2), ("style", "ladder")))
    G_paint((boxFormedLabels if J.truthy(showLabels) else G_series_of(None)), J.obj(("name", "Box labels"), ("style", "labels_above"), ("color", "#0066ff"), ("backgroundColor", "#0066ff"), ("fontSize", 10), ("verticalOffset", 5)))
    G_paint((boxBreakoutLabels if J.truthy(showLabels) else G_series_of(None)), J.obj(("name", "BO labels"), ("style", "labels_above"), ("color", "#00ff00"), ("backgroundColor", "#00ff00"), ("fontSize", 10), ("verticalOffset", 10)))
    G_paint((boxBreakdownLabels if J.truthy(showLabels) else G_series_of(None)), J.obj(("name", "BD labels"), ("style", "labels_below"), ("color", "#ff0000"), ("backgroundColor", "#ff0000"), ("fontSize", 10), ("verticalOffset", 5)))
    G_register_signal(boxFormedSignal, "Box Formed")
    G_register_signal(boxBreakoutSignal, "Box Breakout")
    G_register_signal(boxBreakdownSignal, "Box Breakdown")


register_store_indicator(
    script,
    name='darvas_box_indicator_TS',
    title='Darvas Box Indicator',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69a876-darvas-box-indicator/',
    position='price',
    inputs=[{'id': 'confirmation_bars', 'title': 'Confirmation Bars', 'type': 'number', 'default': 3}, {'id': 'show_labels', 'title': 'Show Labels', 'type': 'select_wide', 'default': 'Yes', 'options': ['Yes', 'No']}, {'id': 'breakout_uses_close', 'title': 'Breakout Uses Close', 'type': 'select_wide', 'default': 'Yes', 'options': ['Yes', 'No']}, {'id': 'use_rvol_for_breakout', 'title': 'Use RVOL for Breakout', 'type': 'select_wide', 'default': 'No', 'options': ['Yes', 'No']}, {'id': 'rvol_lookback', 'title': 'RVOL Lookback', 'type': 'number', 'default': 20}, {'id': 'rvol_threshold', 'title': 'RVOL Threshold', 'type': 'number', 'default': 1}],
    outputs=['rolling_high_52', 'box_top', 'box_bottom', 'box_labels', 'bo_labels', 'bd_labels', 'box_formed', 'box_breakout', 'box_breakdown'],
    signals=['box_formed', 'box_breakout', 'box_breakdown'],
    requires=[],
    parity='exact',
)
