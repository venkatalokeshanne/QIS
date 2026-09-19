"""
Per-session Volume-by-Price (VbP) -- TrendSpider store indicator by TrendSpider Team.

Registered as "per_session_volume_by_price_vbp_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/per-session-volume-by-price-vbp/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Error = G["Error"]
    G_Math = G["Math"]
    G_add = G["add"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_isNaN = G["isNaN"]
    G_library = G["library"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_prices = G["prices"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_sub = G["sub"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    def createVerticalRange(initialBottomPrice=J.undefined, initialTopPrice=J.undefined, *_args):
        top = G_series_of(None)
        bottom = G_series_of(None)
        bottomPrice = initialBottomPrice
        topPrice = initialTopPrice
        def _f1(newBottomPrice=J.undefined, newTopPrice=J.undefined, *_args):
            nonlocal bottomPrice, topPrice
            bottomPrice = newBottomPrice
            topPrice = newTopPrice
        def _f2(*_args):
            return J.obj(("bottomPrice", bottomPrice), ("topPrice", topPrice))
        def _f3(leftIndex=J.undefined, rightValuePointIndex=J.undefined, value=J.undefined, *_args):
            filledLength = J.get(G_Math, "round")(J.mul(value, J.sub(rightValuePointIndex, leftIndex)))
            if J.le(filledLength, 0):
                return J.undefined
            if (J.eq(filledLength, J.sub(rightValuePointIndex, leftIndex)) and J.ne(rightValuePointIndex, J.sub(J.get(G_time, "length"), 1))):
                filledLength = J.sub(filledLength, 1)
            def _f1(*_args):
                return topPrice
            J.get(top, "splice")(leftIndex, filledLength, *J.spread(J.get(J.JSArray([*J.spread(G_Array(filledLength))]), "map")(_f1)))
            def _f2(*_args):
                return bottomPrice
            J.get(bottom, "splice")(leftIndex, filledLength, *J.spread(J.get(J.JSArray([*J.spread(G_Array(filledLength))]), "map")(_f2)))
        def _f4(verticalMargin_2=J.undefined, color=J.undefined, title=J.undefined, *_args):
            G_fill(G_paint(G_sub(top, verticalMargin_2), J.obj(("hidden", True))), G_paint(G_add(bottom, verticalMargin_2), J.obj(("hidden", True))), color, 0.3, title)
        return J.obj(("setCurrentPriceRange", _f1), ("priceRange", _f2), ("setStripProgress", _f3), ("render", _f4))
    def identifyDays(*_args):
        days_2 = J.JSArray([])
        dayStartIndex = 0
        candleIndex_2 = 0
        while J.lt(candleIndex_2, J.get(G_time, "length")):
            if J.ne(J.get(G_time_of(J.get(G_time, dayStartIndex)), "dayOfYear"), J.get(G_time_of(J.get(G_time, candleIndex_2)), "dayOfYear")):
                J.get(days_2, "push")(J.obj(("from", dayStartIndex), ("to", candleIndex_2)))
                dayStartIndex = candleIndex_2
            candleIndex_2 = J.add(candleIndex_2, 1)
        if J.ne(dayStartIndex, J.get(G_time, "length")):
            J.get(days_2, "push")(J.obj(("from", dayStartIndex), ("to", J.get(G_time, "length"))))
        return days_2
    def volumeAtPriceRange(timeFrameData=J.undefined, fromCandleIndex=J.undefined, toCandleIndex=J.undefined, bottomPrice=J.undefined, topPrice=J.undefined, *_args):
        result = 0
        candleIndex_2 = fromCandleIndex
        while J.lt(candleIndex_2, toCandleIndex):
            candleLow = J.get(J.get(timeFrameData, "low"), candleIndex_2)
            candleHigh = J.get(J.get(timeFrameData, "high"), candleIndex_2)
            if J.eq(candleLow, candleHigh):
                candleIndex_2 = J.add(candleIndex_2, 1)
                continue
            def _f1(*_args):
                if (J.eq(candleLow, candleHigh) or J.eq(bottomPrice, topPrice)):
                    return 0
                if (J.gt(bottomPrice, candleHigh) or J.lt(topPrice, candleLow)):
                    return 0
                if (J.le(topPrice, candleHigh) and J.ge(bottomPrice, candleLow)):
                    return J.sub(topPrice, bottomPrice)
                if (J.le(candleHigh, topPrice) and J.ge(candleLow, bottomPrice)):
                    return J.sub(candleHigh, candleLow)
                if ((J.ge(topPrice, candleHigh) and J.ge(bottomPrice, candleLow)) and J.le(bottomPrice, candleHigh)):
                    return J.sub(candleHigh, bottomPrice)
                if ((J.le(bottomPrice, candleLow) and J.ge(topPrice, candleLow)) and J.le(topPrice, candleHigh)):
                    return J.sub(topPrice, candleLow)
            overlappingLength = _f1()
            volumeFraction = J.div(overlappingLength, J.sub(candleHigh, candleLow))
            result = J.add(result, J.mul(J.get(J.get(timeFrameData, "volume"), candleIndex_2), volumeFraction))
            candleIndex_2 = J.add(candleIndex_2, 1)
        return result
    def findValueArea(levels_2=J.undefined, maxVolume_2=J.undefined, *_args):
        def _f1(result=J.undefined, level=J.undefined, *_args):
            return J.add(result, J.get(level, "volume"))
        totalVolume = J.get(levels_2, "reduce")(_f1, 0)
        volumeAccumulated = maxVolume_2
        def _f2(level=J.undefined, *_args):
            return J.eq(J.get(level, "volume"), maxVolume_2)
        pointOfControlIndex = J.get(levels_2, "findIndex")(_f2)
        valueAreaTop_2 = pointOfControlIndex
        valueAreaBottom_2 = pointOfControlIndex
        steps = 0
        while True:
            def _f3(result=J.undefined, level=J.undefined, *_args):
                return J.add(result, J.get(level, "volume"))
            twoLevelsAboveVolume = J.get(J.get(levels_2, "slice")(J.add(valueAreaTop_2, 1), J.add(valueAreaTop_2, 3)), "reduce")(_f3, 0)
            def _f4(result=J.undefined, level=J.undefined, *_args):
                return J.add(result, J.get(level, "volume"))
            twoLevelsBelowVolume = J.get(J.get(levels_2, "slice")(J.sub(valueAreaBottom_2, 2), valueAreaBottom_2), "reduce")(_f4, 0)
            if J.gt(twoLevelsAboveVolume, twoLevelsBelowVolume):
                volumeAccumulated = J.add(volumeAccumulated, twoLevelsAboveVolume)
                valueAreaTop_2 = J.get(G_Math, "min")(J.sub(J.get(levels_2, "length"), 1), J.add(valueAreaTop_2, 2))
            else:
                volumeAccumulated = J.add(volumeAccumulated, twoLevelsBelowVolume)
                valueAreaBottom_2 = J.get(G_Math, "max")(0, J.sub(valueAreaBottom_2, 2))
            steps = J.add(steps, 1)
            if J.gt(steps, 10):
                break
            if not J.lt(volumeAccumulated, J.mul(VALUE_AREA_MIN_ACCUMULATED_VOLUME, totalVolume)):
                break
        return J.obj(("topPrice", J.get(J.get(J.get(J.get(levels_2, valueAreaTop_2), "range"), "priceRange")(), "topPrice")), ("pointOfControl", J.div(J.add(J.get(J.get(J.get(J.get(levels_2, pointOfControlIndex), "range"), "priceRange")(), "bottomPrice"), J.get(J.get(J.get(J.get(levels_2, pointOfControlIndex), "range"), "priceRange")(), "topPrice")), 2)), ("bottomPrice", J.get(J.get(J.get(J.get(levels_2, valueAreaBottom_2), "range"), "priceRange")(), "bottomPrice")))
    def computeVbpFromLowerTimeFrameData(ranges_2=J.undefined, day_2=J.undefined, highOfDay_2=J.undefined, lowOfDay_2=J.undefined, *_args):
        dayStartTimestamp_2 = J.get(G_time, J.get(day_2, "from"))
        dayEndTimestamp = J.get(G_time, J.get(day_2, "to"))
        levels_2 = J.JSArray([])
        for range in J.iter_of(ranges_2):
            if (J.gt(J.get(J.get(range, "priceRange")(), "bottomPrice"), lowOfDay_2) and J.lt(J.get(J.get(range, "priceRange")(), "bottomPrice"), highOfDay_2)):
                volumeAtRange = volumeAtPriceRange(lowerTimeFrameData, J.get(binarySearch, "lt")(J.get(lowerTimeFrameData, "time"), dayStartTimestamp_2), J.get(binarySearch, "ge")(J.get(lowerTimeFrameData, "time"), dayEndTimestamp), J.get(J.get(range, "priceRange")(), "bottomPrice"), J.get(J.get(range, "priceRange")(), "topPrice"))
                J.get(levels_2, "push")(J.obj(("range", range), ("volume", volumeAtRange)))
        return levels_2
    def computeVbpFromSameTimeFrameData(ranges_2=J.undefined, day_2=J.undefined, highOfDay_2=J.undefined, lowOfDay_2=J.undefined, *_args):
        levels_2 = J.JSArray([])
        for range in J.iter_of(ranges_2):
            if (J.gt(J.get(J.get(range, "priceRange")(), "bottomPrice"), lowOfDay_2) and J.lt(J.get(J.get(range, "priceRange")(), "bottomPrice"), highOfDay_2)):
                J.get(levels_2, "push")(J.obj(("range", range), ("volume", volumeAtPriceRange(G_prices, J.get(day_2, "from"), J.get(day_2, "to"), J.get(J.get(range, "priceRange")(), "bottomPrice"), J.get(J.get(range, "priceRange")(), "topPrice")))))
        return levels_2
    G_describe_indicator("Per-session VbP, combined TF", J.obj(("warmup", 200)))
    COLUMNS_NUMBER = 20
    VALUE_AREA_MIN_ACCUMULATED_VOLUME = 0.7
    NORMAL_COLUMN_COLOR = "#999"
    if J.truthy(G_isNaN(J.get(G_constants, "resolution"))):
        raise J.js_throw(G_Error("Only supported for intraday time frames"))
    binarySearch = G_library("binary-search-bounds")
    days = identifyDays()
    resolutionDivisor = (3 if J.lt(J.get(G_constants, "resolution"), 15) else 2)
    lowerTimeFrameData = J.get(G_request, "history")(J.get(G_constants, "ticker"), J.get(G_Math, "min")(J.get(G_Math, "round")(J.div(J.get(G_constants, "resolution"), resolutionDivisor)), 4))
    def _f1(*_args):
        return createVerticalRange(0, 0)
    ranges = J.get(J.JSArray([*J.spread(G_Array(COLUMNS_NUMBER))]), "map")(_f1)
    poc = G_series_of(None)
    valueAreaTop = G_series_of(None)
    valueAreaBottom = G_series_of(None)
    for day in J.iter_of(days):
        highOfDay = J.get(G_Math, "max")(*J.spread(J.get(G_high, "slice")(J.get(day, "from"), J.get(day, "to"))))
        lowOfDay = J.get(G_Math, "min")(*J.spread(J.get(G_low, "slice")(J.get(day, "from"), J.get(day, "to"))))
        stripHeight = J.div(J.sub(highOfDay, lowOfDay), COLUMNS_NUMBER)
        def _f2(range=J.undefined, rangeIndex=J.undefined, *_args):
            return J.get(range, "setCurrentPriceRange")(J.add(lowOfDay, J.mul(stripHeight, rangeIndex)), J.add(lowOfDay, J.mul(stripHeight, J.add(rangeIndex, 1))))
        J.get(ranges, "forEach")(_f2)
        dayStartTimestamp = J.get(G_time, J.get(day, "from"))
        useLowTimeFrameData = (J.gt(dayStartTimestamp, J.get(J.get(lowerTimeFrameData, "time"), 0)) if J.truthy(_t3 := lowerTimeFrameData) else _t3)
        levels = (computeVbpFromLowerTimeFrameData(ranges, day, highOfDay, lowOfDay) if J.truthy(useLowTimeFrameData) else computeVbpFromSameTimeFrameData(ranges, day, highOfDay, lowOfDay))
        if J.seq(J.get(levels, "length"), 0):
            continue
        def _f4(_p1=J.undefined, *_args):
            _t2 = J.require_object(_p1)
            volume = J.get(_t2, "volume")
            return volume
        maxVolume = J.get(G_Math, "max")(*J.spread(J.get(levels, "map")(_f4)))
        pointofControl = J.undefined
        def _f5(_p1=J.undefined, rangeIndex=J.undefined, *_args):
            _t2 = J.require_object(_p1)
            range = J.get(_t2, "range")
            volume = J.get(_t2, "volume")
            J.get(range, "setCurrentPriceRange")(J.add(lowOfDay, J.mul(stripHeight, rangeIndex)), J.add(lowOfDay, J.mul(stripHeight, J.add(rangeIndex, 1))))
            J.get(range, "setStripProgress")(J.get(day, "from"), J.get(day, "to"), J.div(volume, maxVolume))
        J.get(levels, "forEach")(_f5)
        valueArea = findValueArea(levels, maxVolume)
        candleIndex = J.get(day, "from")
        while J.lt(candleIndex, J.get(day, "to")):
            J.set(valueAreaTop, candleIndex, J.get(valueArea, "topPrice"))
            J.set(valueAreaBottom, candleIndex, J.get(valueArea, "bottomPrice"))
            J.set(poc, candleIndex, J.get(valueArea, "pointOfControl"))
            candleIndex = J.add(candleIndex, 1)
    chartHighestHigh = J.get(G_Math, "max")(*J.spread(G_high))
    chartLowestLow = J.get(G_Math, "min")(*J.spread(G_low))
    verticalMargin = J.div(J.sub(chartHighestHigh, chartLowestLow), J.mul(90, COLUMNS_NUMBER))
    def _f6(range=J.undefined, rangeIndex=J.undefined, *_args):
        return J.get(range, "render")(verticalMargin, NORMAL_COLUMN_COLOR, J.template("Level", J.add(rangeIndex, 1)))
    J.get(ranges, "forEach")(_f6)
    G_paint(poc, J.obj(("name", "PoC"), ("style", "ladder"), ("color", "#8b1cff")))
    G_fill(G_paint(valueAreaTop, J.obj(("name", "Value/Top"), ("style", "ladder"), ("color", "#1cc1ff"))), G_paint(valueAreaBottom, J.obj(("name", "Value/Bot"), ("style", "ladder"), ("color", "#1cc1ff"))), "#1cc1ff", 0.1, J.template("Value area"))


register_store_indicator(
    script,
    name='per_session_volume_by_price_vbp_TS',
    title='Per-session Volume-by-Price (VbP)',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/per-session-volume-by-price-vbp/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 200}],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='aapl_d: both-error, syn_5m: OK',
)
