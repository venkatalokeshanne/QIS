"""
VbP from Earnings Indicator -- TrendSpider store indicator by TrendSpider Team.

Registered as "vbp_from_earnings_indicator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6860a2-vbp-from-earnings/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Math = G["Math"]
    G_add = G["add"]
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_high = G["high"]
    G_library = G["library"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_prices = G["prices"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_sub = G["sub"]
    G_time = G["time"]
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
    def computeVbpFromSameTimeFrameData(ranges_2=J.undefined, day=J.undefined, highOfDay=J.undefined, lowOfDay=J.undefined, *_args):
        levels_2 = J.JSArray([])
        for range in J.iter_of(ranges_2):
            if (J.gt(J.get(J.get(range, "priceRange")(), "bottomPrice"), lowOfDay) and J.lt(J.get(J.get(range, "priceRange")(), "bottomPrice"), highOfDay)):
                J.get(levels_2, "push")(J.obj(("range", range), ("volume", volumeAtPriceRange(G_prices, J.get(day, "from"), J.get(day, "to"), J.get(J.get(range, "priceRange")(), "bottomPrice"), J.get(J.get(range, "priceRange")(), "topPrice")))))
        return levels_2
    G_describe_indicator("VbP from Earnings", J.obj(("warmup", 200)))
    COLUMNS_NUMBER = 20
    VALUE_AREA_MIN_ACCUMULATED_VOLUME = 0.7
    NORMAL_COLUMN_COLOR = "#999"
    binarySearch = G_library("binary-search-bounds")
    earningsData = J.get(G_request, "earnings")(J.get(G_current, "ticker"))
    G_assert((not J.truthy(J.get(earningsData, "error"))), J.template("Error fetching earnings data: ", J.get(earningsData, "error")))
    def _f1(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(b, "timestamp"), J.get(a, "timestamp"))
    sortedEarnings = J.get(earningsData, "sort")(_f1)
    def _f2(e=J.undefined, *_args):
        return J.le(J.get(e, "timestamp"), J.get(G_time, J.sub(J.get(G_time, "length"), 1)))
    mostRecentEarnings = J.get(sortedEarnings, "find")(_f2)
    def _f3(e=J.undefined, *_args):
        return J.gt(J.get(e, "timestamp"), J.get(G_time, J.sub(J.get(G_time, "length"), 1)))
    nextEarnings = J.get(sortedEarnings, "find")(_f3)
    G_assert(mostRecentEarnings, "No recent earnings data found")
    startIndex = J.get(binarySearch, "ge")(G_time, J.get(mostRecentEarnings, "timestamp"))
    endIndex = (J.get(binarySearch, "ge")(G_time, J.get(nextEarnings, "timestamp")) if J.truthy(nextEarnings) else J.get(G_time, "length"))
    def _f4(*_args):
        return createVerticalRange(0, 0)
    ranges = J.get(J.JSArray([*J.spread(G_Array(COLUMNS_NUMBER))]), "map")(_f4)
    poc = G_series_of(None)
    valueAreaTop = G_series_of(None)
    valueAreaBottom = G_series_of(None)
    highOfPeriod = J.get(G_Math, "max")(*J.spread(J.get(G_high, "slice")(startIndex, endIndex)))
    lowOfPeriod = J.get(G_Math, "min")(*J.spread(J.get(G_low, "slice")(startIndex, endIndex)))
    stripHeight = J.div(J.sub(highOfPeriod, lowOfPeriod), COLUMNS_NUMBER)
    def _f5(range=J.undefined, rangeIndex=J.undefined, *_args):
        return J.get(range, "setCurrentPriceRange")(J.add(lowOfPeriod, J.mul(stripHeight, rangeIndex)), J.add(lowOfPeriod, J.mul(stripHeight, J.add(rangeIndex, 1))))
    J.get(ranges, "forEach")(_f5)
    levels = computeVbpFromSameTimeFrameData(ranges, J.obj(("from", startIndex), ("to", endIndex)), highOfPeriod, lowOfPeriod)
    if J.gt(J.get(levels, "length"), 0):
        def _f6(_p1=J.undefined, *_args):
            _t2 = J.require_object(_p1)
            volume = J.get(_t2, "volume")
            return volume
        maxVolume = J.get(G_Math, "max")(*J.spread(J.get(levels, "map")(_f6)))
        def _f7(_p1=J.undefined, rangeIndex=J.undefined, *_args):
            _t2 = J.require_object(_p1)
            range = J.get(_t2, "range")
            volume = J.get(_t2, "volume")
            J.get(range, "setCurrentPriceRange")(J.add(lowOfPeriod, J.mul(stripHeight, rangeIndex)), J.add(lowOfPeriod, J.mul(stripHeight, J.add(rangeIndex, 1))))
            J.get(range, "setStripProgress")(startIndex, endIndex, J.div(volume, maxVolume))
        J.get(levels, "forEach")(_f7)
        valueArea = findValueArea(levels, maxVolume)
        candleIndex = startIndex
        while J.lt(candleIndex, endIndex):
            J.set(valueAreaTop, candleIndex, J.get(valueArea, "topPrice"))
            J.set(valueAreaBottom, candleIndex, J.get(valueArea, "bottomPrice"))
            J.set(poc, candleIndex, J.get(valueArea, "pointOfControl"))
            candleIndex = J.add(candleIndex, 1)
    chartHighestHigh = J.get(G_Math, "max")(*J.spread(G_high))
    chartLowestLow = J.get(G_Math, "min")(*J.spread(G_low))
    verticalMargin = J.div(J.sub(chartHighestHigh, chartLowestLow), J.mul(90, COLUMNS_NUMBER))
    def _f8(range=J.undefined, rangeIndex=J.undefined, *_args):
        return J.get(range, "render")(verticalMargin, NORMAL_COLUMN_COLOR, J.template("Level", J.add(rangeIndex, 1)))
    J.get(ranges, "forEach")(_f8)
    G_paint(poc, J.obj(("name", "PoC"), ("style", "ladder"), ("color", "#8b1cff")))
    G_fill(G_paint(valueAreaTop, J.obj(("name", "Value/Top"), ("style", "ladder"), ("color", "#1cc1ff"))), G_paint(valueAreaBottom, J.obj(("name", "Value/Bot"), ("style", "ladder"), ("color", "#1cc1ff"))), "#1cc1ff", 0.1, J.template("Value area"))


register_store_indicator(
    script,
    name='vbp_from_earnings_indicator_TS',
    title='VbP from Earnings Indicator',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/6860a2-vbp-from-earnings/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 200}],
    outputs=['line_1', 'line_2', 'line_4', 'line_5', 'line_7', 'line_8', 'line_10', 'line_11', 'line_13', 'line_14', 'line_16', 'line_17', 'line_19', 'line_20', 'line_22', 'line_23', 'line_25', 'line_26', 'line_28', 'line_29', 'line_31', 'line_32', 'line_34', 'line_35', 'line_37', 'line_38', 'line_40', 'line_41', 'line_43', 'line_44', 'line_46', 'line_47', 'line_49', 'line_50', 'line_52', 'line_53', 'line_55', 'line_56', 'line_58', 'line_59', 'poc', 'value_top', 'value_bot'],
    signals=[],
    requires=['earnings'],
    parity='exact',
)
