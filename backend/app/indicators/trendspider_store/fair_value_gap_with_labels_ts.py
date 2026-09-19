"""
Fair Value Gap with Labels -- TrendSpider store indicator by TrendSpider Team.

Registered as "fair_value_gap_with_labels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/fair-value-gap-with-labels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_atr = G["atr"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_series_of = G["series_of"]
    G_describe_indicator("Fair Value Gap with Labels and Toggle", "price", J.obj(("shortName", "FVG")))
    gapFactor = G_input("Gap factor", 1, J.obj(("min", 0.01), ("max", 50)))
    labelsValues = J.JSArray(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])
    def _f1(label=J.undefined, *_args):
        return J.get(G_input, "boolean")(J.template("Show Gap ", label), True)
    whichToShow = J.get(labelsValues, "map")(_f1)
    def gapObject(*_args):
        return J.obj(("topPrice", None), ("bottomPrice", None), ("ascending", None), ("topLine", G_series_of(None)), ("bottomLine", G_series_of(None)), ("index", (-1)))
    maxGaps = 10
    gapArray = J.JSArray([])
    gapIndex = 0
    while J.lt(gapIndex, maxGaps):
        J.get(gapArray, "push")(gapObject())
        gapIndex = J.inc(gapIndex)
    gapBars = G_series_of(None)
    topDots = G_series_of(None)
    bottomDots = G_series_of(None)
    gapNumber = 10
    def getAvailableGapIndex(*_args):
        nonlocal gapNumber
        J.get(gapArray, "push")(gapObject())
        return ((_t1 := J.tonum(gapNumber)), (gapNumber := J.inc(_t1)))[0]
    priceAtr = G_atr(14)
    candleIndex = 2
    while J.lt(candleIndex, J.get(G_close, "length")):
        gapSize = (J.mul(gapFactor, J.get(priceAtr, candleIndex)) if (J.get(priceAtr, candleIndex) is not None) else None)
        isUpGap = (J.lt(J.get(G_high, J.sub(candleIndex, 1)), J.get(G_high, candleIndex)) if J.truthy(_t2 := (J.gt(J.get(G_high, J.sub(candleIndex, 2)), J.get(G_low, J.sub(candleIndex, 1))) if J.truthy(_t3 := (J.lt(J.get(G_low, candleIndex), J.get(G_high, J.sub(candleIndex, 1))) if J.truthy(_t4 := (J.gt(J.sub(J.get(G_low, candleIndex), J.get(G_high, J.sub(candleIndex, 2))), gapSize) if J.truthy(_t5 := (gapSize is not None)) else _t5)) else _t4)) else _t3)) else _t2)
        isDownGap = (J.gt(J.get(G_low, J.sub(candleIndex, 1)), J.get(G_low, candleIndex)) if J.truthy(_t6 := (J.gt(J.get(G_high, candleIndex), J.get(G_low, J.sub(candleIndex, 1))) if J.truthy(_t7 := (J.lt(J.get(G_low, J.sub(candleIndex, 2)), J.get(G_high, J.sub(candleIndex, 1))) if J.truthy(_t8 := (J.gt(J.sub(J.get(G_low, J.sub(candleIndex, 2)), J.get(G_high, candleIndex)), gapSize) if J.truthy(_t9 := (gapSize is not None)) else _t9)) else _t8)) else _t7)) else _t6)
        if (J.truthy(isUpGap) or J.truthy(isDownGap)):
            availableGapIndex = getAvailableGapIndex()
            J.set(J.get(gapArray, availableGapIndex), "index", candleIndex)
            if J.truthy(isUpGap):
                J.set(J.get(gapArray, availableGapIndex), "ascending", True)
                J.set(J.get(gapArray, availableGapIndex), "topPrice", J.get(G_low, candleIndex))
                J.set(J.get(gapArray, availableGapIndex), "bottomPrice", J.get(G_high, J.sub(candleIndex, 2)))
            elif J.truthy(isDownGap):
                J.set(J.get(gapArray, availableGapIndex), "ascending", False)
                J.set(J.get(gapArray, availableGapIndex), "topPrice", J.get(G_low, J.sub(candleIndex, 2)))
                J.set(J.get(gapArray, availableGapIndex), "bottomPrice", J.get(G_high, candleIndex))
            J.set(gapBars, candleIndex, J.obj(("high", J.get(J.get(gapArray, availableGapIndex), "topPrice")), ("low", J.get(J.get(gapArray, availableGapIndex), "bottomPrice"))))
            J.set(topDots, candleIndex, J.get(J.get(gapArray, availableGapIndex), "topPrice"))
            J.set(bottomDots, candleIndex, J.get(J.get(gapArray, availableGapIndex), "bottomPrice"))
        gapIndex_2 = 0
        while J.lt(gapIndex_2, gapNumber):
            if J.truthy(J.get(J.get(gapArray, gapIndex_2), "filled")):
                gapIndex_2 = J.inc(gapIndex_2)
                continue
            if ((J.lt(J.get(G_high, J.sub(candleIndex, 1)), J.get(J.get(gapArray, gapIndex_2), "bottomPrice")) and J.gt(J.get(G_low, candleIndex), J.get(J.get(gapArray, gapIndex_2), "topPrice"))) or (J.gt(J.get(G_low, J.sub(candleIndex, 1)), J.get(J.get(gapArray, gapIndex_2), "topPrice")) and J.lt(J.get(G_high, candleIndex), J.get(J.get(gapArray, gapIndex_2), "bottomPrice")))):
                J.set(J.get(gapArray, gapIndex_2), "ascending", (not J.truthy(J.get(J.get(gapArray, gapIndex_2), "ascending"))))
            elif (J.truthy(J.get(J.get(gapArray, gapIndex_2), "ascending")) and J.gt(J.get(J.get(gapArray, gapIndex_2), "topPrice"), J.get(G_low, candleIndex))):
                J.set(J.get(gapArray, gapIndex_2), "topPrice", J.get(G_low, candleIndex))
            elif ((not J.truthy(J.get(J.get(gapArray, gapIndex_2), "ascending"))) and J.lt(J.get(J.get(gapArray, gapIndex_2), "bottomPrice"), J.get(G_high, candleIndex))):
                J.set(J.get(gapArray, gapIndex_2), "bottomPrice", J.get(G_high, candleIndex))
            if J.le(J.get(J.get(gapArray, gapIndex_2), "topPrice"), J.get(J.get(gapArray, gapIndex_2), "bottomPrice")):
                J.set(J.get(J.get(gapArray, gapIndex_2), "topLine"), candleIndex, J.get(J.get(J.get(gapArray, gapIndex_2), "topLine"), J.sub(candleIndex, 1)))
                J.set(J.get(J.get(gapArray, gapIndex_2), "bottomLine"), candleIndex, J.get(J.get(J.get(gapArray, gapIndex_2), "bottomLine"), J.sub(candleIndex, 1)))
                J.set(J.get(gapArray, gapIndex_2), "filled", True)
            else:
                J.set(J.get(J.get(gapArray, gapIndex_2), "topLine"), candleIndex, J.get(J.get(gapArray, gapIndex_2), "topPrice"))
                J.set(J.get(J.get(gapArray, gapIndex_2), "bottomLine"), candleIndex, J.get(J.get(gapArray, gapIndex_2), "bottomPrice"))
            gapIndex_2 = J.inc(gapIndex_2)
        candleIndex = J.inc(candleIndex)
    candleIndex_2 = 0
    while J.lt(candleIndex_2, J.sub(J.get(J.get(gapArray, J.sub(gapNumber, maxGaps)), "index"), 1)):
        J.set(gapBars, candleIndex_2, J.obj(("high", None), ("low", None)))
        J.set(topDots, candleIndex_2, None)
        J.set(bottomDots, candleIndex_2, None)
        candleIndex_2 = J.inc(candleIndex_2)
    if J.truthy(J.get(whichToShow, 9)):
        G_fill(G_paint(J.get(J.get(gapArray, J.sub(gapNumber, maxGaps)), "topLine"), J.obj(("name", "J/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.sub(gapNumber, maxGaps)), "bottomLine"), J.obj(("name", "J/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "J")
    if J.truthy(J.get(whichToShow, 8)):
        G_fill(G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 1)), "topLine"), J.obj(("name", "I/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 1)), "bottomLine"), J.obj(("name", "I/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "I")
    if J.truthy(J.get(whichToShow, 7)):
        G_fill(G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 2)), "topLine"), J.obj(("name", "H/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 2)), "bottomLine"), J.obj(("name", "H/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "H")
    if J.truthy(J.get(whichToShow, 6)):
        G_fill(G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 3)), "topLine"), J.obj(("name", "G/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 3)), "bottomLine"), J.obj(("name", "G/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "G")
    if J.truthy(J.get(whichToShow, 5)):
        G_fill(G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 4)), "topLine"), J.obj(("name", "F/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 4)), "bottomLine"), J.obj(("name", "F/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "F")
    if J.truthy(J.get(whichToShow, 4)):
        G_fill(G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 5)), "topLine"), J.obj(("name", "E/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 5)), "bottomLine"), J.obj(("name", "E/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "E")
    if J.truthy(J.get(whichToShow, 3)):
        G_fill(G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 6)), "topLine"), J.obj(("name", "D/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 6)), "bottomLine"), J.obj(("name", "D/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "D")
    if J.truthy(J.get(whichToShow, 2)):
        G_fill(G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 7)), "topLine"), J.obj(("name", "C/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 7)), "bottomLine"), J.obj(("name", "C/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "C")
    if J.truthy(J.get(whichToShow, 1)):
        G_fill(G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 8)), "topLine"), J.obj(("name", "B/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 8)), "bottomLine"), J.obj(("name", "B/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "B")
    if J.truthy(J.get(whichToShow, 0)):
        G_fill(G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 9)), "topLine"), J.obj(("name", "A/Top"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), G_paint(J.get(J.get(gapArray, J.add(J.sub(gapNumber, maxGaps), 9)), "bottomLine"), J.obj(("name", "A/Bot"), ("color", "#1b65bf"), ("ignoreWhenScaling", True))), "#1b65bf", J.undefined, "A")
    def _f10(x=J.undefined, i=J.undefined, *_args):
        if (not J.truthy(J.get(whichToShow, J.sub(J.sub(maxGaps, i), 1)))):
            J.set(gapBars, J.get(x, "index"), None)
            J.set(topDots, J.get(x, "index"), None)
            J.set(bottomDots, J.get(x, "index"), None)
    J.get(J.get(gapArray, "slice")(J.neg(maxGaps)), "forEach")(_f10)
    G_paint(gapBars, J.obj(("name", "Gap Bar"), ("style", "columnrange")))
    topDotsRef = G_paint(topDots, J.obj(("name", "Top Dots"), ("color", "black"), ("style", "dotted"), ("thickness", 3)))
    G_paint(bottomDots, J.obj(("name", "Bottom Dots"), ("color", "black"), ("style", "dotted"), ("thickness", 3)))
    J.get(labelsValues, "reverse")()
    def _f11(x=J.undefined, i=J.undefined, *_args):
        if J.truthy(J.get(whichToShow, J.sub(J.sub(maxGaps, i), 1))):
            G_paint_label_at_line(topDotsRef, J.get(x, "index"), J.get(labelsValues, i), J.obj(("border_width", "1px"), ("border_color", "black"), ("border_radius", "50%"), ("background_color", "white")))
    J.get(J.get(gapArray, "slice")(J.neg(maxGaps)), "forEach")(_f11)


register_store_indicator(
    script,
    name='fair_value_gap_with_labels_TS',
    title='Fair Value Gap with Labels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/fair-value-gap-with-labels/',
    position='price',
    inputs=[{'id': 'gap_factor', 'title': 'Gap factor', 'type': 'number', 'default': 1}, {'id': 'show_gap_a', 'title': 'Show Gap A', 'type': 'boolean', 'default': True}, {'id': 'show_gap_b', 'title': 'Show Gap B', 'type': 'boolean', 'default': True}, {'id': 'show_gap_c', 'title': 'Show Gap C', 'type': 'boolean', 'default': True}, {'id': 'show_gap_d', 'title': 'Show Gap D', 'type': 'boolean', 'default': True}, {'id': 'show_gap_e', 'title': 'Show Gap E', 'type': 'boolean', 'default': True}, {'id': 'show_gap_f', 'title': 'Show Gap F', 'type': 'boolean', 'default': True}, {'id': 'show_gap_g', 'title': 'Show Gap G', 'type': 'boolean', 'default': True}, {'id': 'show_gap_h', 'title': 'Show Gap H', 'type': 'boolean', 'default': True}, {'id': 'show_gap_i', 'title': 'Show Gap I', 'type': 'boolean', 'default': True}, {'id': 'show_gap_j', 'title': 'Show Gap J', 'type': 'boolean', 'default': True}],
    outputs=['j_top', 'j_bot', 'i_top', 'i_bot', 'h_top', 'h_bot', 'g_top', 'g_bot', 'f_top', 'f_bot', 'e_top', 'e_bot', 'd_top', 'd_bot', 'c_top', 'c_bot', 'b_top', 'b_bot', 'a_top', 'a_bot', 'gap_bar', 'top_dots', 'bottom_dots'],
    signals=[],
    requires=[],
    parity='exact',
)
