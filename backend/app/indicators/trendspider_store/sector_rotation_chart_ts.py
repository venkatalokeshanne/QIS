"""
Sector Rotation Chart -- TrendSpider store indicator by TrendSpider.

Registered as "sector_rotation_chart_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69a731-sector-rotation-chart/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_Object = G["Object"]
    G_Promise = G["Promise"]
    G_assert = G["assert"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_isFinite = G["isFinite"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_describe_indicator("Sector Rotation Chart v6", "price")
    VERBOSE_INPUT_OPTIONS = J.obj(("hide_in_legend", True))
    tinycolor = G_library("tinycolor2")
    def withAlpha(color=J.undefined, alpha=J.undefined, *_args):
        return J.get(J.get(tinycolor(color), "setAlpha")(alpha), "toRgbString")()
    enableSector1 = J.get(G_input, "boolean")("Show 1", True, VERBOSE_INPUT_OPTIONS)
    mySector1 = J.get(G_input, "symbol")("Symbol 1", "XLE", VERBOSE_INPUT_OPTIONS)
    myColor1 = J.get(G_input, "color")("Color 1", "#FF5722", VERBOSE_INPUT_OPTIONS)
    enableSector2 = J.get(G_input, "boolean")("Show 2", True, VERBOSE_INPUT_OPTIONS)
    mySector2 = J.get(G_input, "symbol")("Symbol 2", "XLB", VERBOSE_INPUT_OPTIONS)
    myColor2 = J.get(G_input, "color")("Color 2", "#795548", VERBOSE_INPUT_OPTIONS)
    enableSector3 = J.get(G_input, "boolean")("Show 3", True, VERBOSE_INPUT_OPTIONS)
    mySector3 = J.get(G_input, "symbol")("Symbol 3", "XLI", VERBOSE_INPUT_OPTIONS)
    myColor3 = J.get(G_input, "color")("Color 3", "#607D8B", VERBOSE_INPUT_OPTIONS)
    enableSector4 = J.get(G_input, "boolean")("Show 4", True, VERBOSE_INPUT_OPTIONS)
    mySector4 = J.get(G_input, "symbol")("Symbol 4", "XLY", VERBOSE_INPUT_OPTIONS)
    myColor4 = J.get(G_input, "color")("Color 4", "#FFA500", VERBOSE_INPUT_OPTIONS)
    enableSector5 = J.get(G_input, "boolean")("Show 5", False, VERBOSE_INPUT_OPTIONS)
    mySector5 = J.get(G_input, "symbol")("Symbol 5", "XLP", VERBOSE_INPUT_OPTIONS)
    myColor5 = J.get(G_input, "color")("Color 5", "#28A745", VERBOSE_INPUT_OPTIONS)
    enableSector6 = J.get(G_input, "boolean")("Show 6", True, VERBOSE_INPUT_OPTIONS)
    mySector6 = J.get(G_input, "symbol")("Symbol 6", "XLV", VERBOSE_INPUT_OPTIONS)
    myColor6 = J.get(G_input, "color")("Color 6", "#DC3545", VERBOSE_INPUT_OPTIONS)
    enableSector7 = J.get(G_input, "boolean")("Show 7", True, VERBOSE_INPUT_OPTIONS)
    mySector7 = J.get(G_input, "symbol")("Symbol 7", "XLF", VERBOSE_INPUT_OPTIONS)
    myColor7 = J.get(G_input, "color")("Color 7", "#1E90FF", VERBOSE_INPUT_OPTIONS)
    enableSector8 = J.get(G_input, "boolean")("Show 8", True, VERBOSE_INPUT_OPTIONS)
    mySector8 = J.get(G_input, "symbol")("Symbol 8", "XLK", VERBOSE_INPUT_OPTIONS)
    myColor8 = J.get(G_input, "color")("Color 8", "#00BCD4", VERBOSE_INPUT_OPTIONS)
    enableSector9 = J.get(G_input, "boolean")("Show 9", False, VERBOSE_INPUT_OPTIONS)
    mySector9 = J.get(G_input, "symbol")("Symbol 9", "XLC", VERBOSE_INPUT_OPTIONS)
    myColor9 = J.get(G_input, "color")("Color 9", "#9C27B0", VERBOSE_INPUT_OPTIONS)
    enableSector10 = J.get(G_input, "boolean")("Show 10", False, VERBOSE_INPUT_OPTIONS)
    mySector10 = J.get(G_input, "symbol")("Symbol 10", "XLU", VERBOSE_INPUT_OPTIONS)
    myColor10 = J.get(G_input, "color")("Color 10", "#6366F1", VERBOSE_INPUT_OPTIONS)
    enableSector11 = J.get(G_input, "boolean")("Show 11", False, VERBOSE_INPUT_OPTIONS)
    mySector11 = J.get(G_input, "symbol")("Symbol 11", "XLRE", VERBOSE_INPUT_OPTIONS)
    myColor11 = J.get(G_input, "color")("Color 11", "#009688", VERBOSE_INPUT_OPTIONS)
    myBenchmark = J.get(G_input, "symbol")("Benchmark", "VTI")
    myCalcTimeframe = J.get(G_input, "select")("Timeframe", "Weekly", J.JSArray(["Weekly", "Monthly"]))
    myHistoryLength = J.get(G_input, "number")("Tail length", 5, J.obj(("min", 2), ("max", 100)))
    mySolidBackground = J.get(G_input, "boolean")("Solid background", True)
    myOctantColor1 = J.get(G_input, "color")("Slice: Strong leader", "#32CD32", VERBOSE_INPUT_OPTIONS)
    myOctantColor2 = J.get(G_input, "color")("Slice: Accelerating", "#9ACD32", VERBOSE_INPUT_OPTIONS)
    myOctantColor3 = J.get(G_input, "color")("Slice: Turning up", "#4DD0E1", VERBOSE_INPUT_OPTIONS)
    myOctantColor4 = J.get(G_input, "color")("Slice: Bottoming", "#AAAAAA", VERBOSE_INPUT_OPTIONS)
    myOctantColor5 = J.get(G_input, "color")("Slice: Deep laggard", "#DC3545", VERBOSE_INPUT_OPTIONS)
    myOctantColor6 = J.get(G_input, "color")("Slice: Falling", "#E57373", VERBOSE_INPUT_OPTIONS)
    myOctantColor7 = J.get(G_input, "color")("Slice: Rolling over", "#FFA726", VERBOSE_INPUT_OPTIONS)
    myOctantColor8 = J.get(G_input, "color")("Slice: Losing steam", "#AAAAAA", VERBOSE_INPUT_OPTIONS)
    CHART_SIZE_MAP = J.obj(("small", J.obj(("w", 450), ("h", 300))), ("medium", J.obj(("w", 600), ("h", 400))), ("large", J.obj(("w", 900), ("h", 600))), ("xlarge", J.obj(("w", 1200), ("h", 800))))
    tableDimensions = J.get(CHART_SIZE_MAP, J.get(G_input, "select")("Chart size", "medium", J.get(G_Object, "keys")(CHART_SIZE_MAP)))
    def _f1(sector=J.undefined, *_args):
        return J.get(sector, "enabled")
    SECTORS = J.get(J.JSArray([J.obj(("ticker", mySector1), ("color", myColor1), ("enabled", enableSector1)), J.obj(("ticker", mySector2), ("color", myColor2), ("enabled", enableSector2)), J.obj(("ticker", mySector3), ("color", myColor3), ("enabled", enableSector3)), J.obj(("ticker", mySector4), ("color", myColor4), ("enabled", enableSector4)), J.obj(("ticker", mySector5), ("color", myColor5), ("enabled", enableSector5)), J.obj(("ticker", mySector6), ("color", myColor6), ("enabled", enableSector6)), J.obj(("ticker", mySector7), ("color", myColor7), ("enabled", enableSector7)), J.obj(("ticker", mySector8), ("color", myColor8), ("enabled", enableSector8)), J.obj(("ticker", mySector9), ("color", myColor9), ("enabled", enableSector9)), J.obj(("ticker", mySector10), ("color", myColor10), ("enabled", enableSector10)), J.obj(("ticker", mySector11), ("color", myColor11), ("enabled", enableSector11))]), "filter")(_f1)
    myDataResolution = ("W" if J.seq(myCalcTimeframe, "Weekly") else "M")
    def _f2(sector=J.undefined, *_args):
        return J.get(sector, "ticker")
    allSymbolsToFetch = J.JSArray([myBenchmark, *J.spread(J.get(SECTORS, "map")(_f2))])
    def _f3(ticker=J.undefined, *_args):
        return J.get(G_request, "history")(ticker, myDataResolution)
    allDataPromises = J.get(allSymbolsToFetch, "map")(_f3)
    allDataResults = J.undefined
    try:
        allDataResults = J.get(G_Promise, "all")(allDataPromises)
    except Exception as _e4:
        exception = J.catch_value(_e4)
        raise J.js_throw("Failed to fetch historical data. This may be due to an invalid ticker symbol or network issue.")
    benchmarkData = J.get(allDataResults, 0)
    G_assert((not J.truthy(J.get(benchmarkData, "error"))), J.template("Error fetching ", myBenchmark, " data: ", J.get(benchmarkData, "error")))
    def computeChangePercentValue(dataSeries=J.undefined, value=J.undefined, dummy=J.undefined, index=J.undefined, *_args):
        return (None if J.lt(index, myHistoryLength) else J.div(J.sub(value, J.get(dataSeries, J.sub(index, myHistoryLength))), J.get(dataSeries, J.sub(index, myHistoryLength))))
    benchmarkChange = G_for_every(J.get(benchmarkData, "close"), J.get(computeChangePercentValue, "bind")(None, J.get(benchmarkData, "close")))
    sectorRSData = J.JSArray([])
    sectorRSMomentumData = J.JSArray([])
    sectorVolumeData = J.JSArray([])
    i = 0
    while J.lt(i, J.get(SECTORS, "length")):
        sector = J.get(SECTORS, i)
        thisDataSeries = J.get(allDataResults, J.add(i, 1))
        sectorPrice = G_land_points_onto_series(J.get(thisDataSeries, "time"), J.get(thisDataSeries, "close"), J.get(benchmarkData, "time"))
        volumeTail = J.get(J.get(thisDataSeries, "volume"), "slice")(J.neg(J.add(myHistoryLength, 1)))
        maxSectorVolume = J.get(G_Math, "max")(*J.spread(volumeTail))
        minSectorVolume = J.get(G_Math, "min")(*J.spread(volumeTail))
        sectorVolumeRange = J.get(G_Math, "max")(1, J.sub(maxSectorVolume, minSectorVolume))
        def _f5(value=J.undefined, *_args):
            return J.div(J.sub(value, minSectorVolume), sectorVolumeRange)
        sectorVolume = J.get(volumeTail, "map")(_f5)
        sectorPriceChange = G_for_every(sectorPrice, J.get(computeChangePercentValue, "bind")(None, sectorPrice))
        EPSILON = 1
        def _f6(_sectorChange=J.undefined, _benchmarkChange=J.undefined, *_args):
            if ((_sectorChange is None) or (_benchmarkChange is None)):
                return None
            return J.div(J.add(_sectorChange, EPSILON), J.add(_benchmarkChange, EPSILON))
        myRelativeStrength = G_for_every(sectorPriceChange, benchmarkChange, _f6)
        def _f7(_currentRS=J.undefined, _prevOutput=J.undefined, _index=J.undefined, *_args):
            if (J.lt(_index, 1) or (_currentRS is None)):
                return None
            previousRS = J.get(myRelativeStrength, J.sub(_index, 1))
            if ((previousRS is None) or J.seq(previousRS, 0)):
                return None
            return J.mul(J.div(_currentRS, previousRS), 100)
        myRSMomentum = G_for_every(myRelativeStrength, _f7)
        J.get(sectorRSData, "push")(J.get(myRelativeStrength, "slice")(J.neg(myHistoryLength)))
        J.get(sectorRSMomentumData, "push")(J.get(myRSMomentum, "slice")(J.neg(myHistoryLength)))
        J.get(sectorVolumeData, "push")(sectorVolume)
        i = J.inc(i)
    CX = 100
    CY = 100
    HALF_RANGE = 10
    AXIS_PAD = 1.05
    INNER_RADIUS_FRAC = 0.18
    ASPECT = J.div(J.get(tableDimensions, "w"), J.get(tableDimensions, "h"))
    minX = J.sub(CX, J.mul(J.mul(HALF_RANGE, AXIS_PAD), ASPECT))
    maxX = J.add(CX, J.mul(J.mul(HALF_RANGE, AXIS_PAD), ASPECT))
    minY = J.sub(CY, J.mul(HALF_RANGE, AXIS_PAD))
    maxY = J.add(CY, J.mul(HALF_RANGE, AXIS_PAD))
    DEG = J.div(J.get(G_Math, "PI"), 180)
    OCT_APOTHEM = J.get(G_Math, "cos")(J.mul(22.5, DEG))
    def polarToXY(angleDeg=J.undefined, radiusFrac=J.undefined, *_args):
        norm = J.mod(J.add(J.mod(angleDeg, 360), 360), 360)
        offsetFromEdgeCenter = J.sub(norm, J.add(J.mul(J.get(G_Math, "floor")(J.div(norm, 45)), 45), 22.5))
        t = J.div(J.mul(J.mul(radiusFrac, HALF_RANGE), OCT_APOTHEM), J.get(G_Math, "cos")(J.mul(offsetFromEdgeCenter, DEG)))
        return J.obj(("x", J.add(CX, J.mul(t, J.get(G_Math, "cos")(J.mul(angleDeg, DEG))))), ("y", J.add(CY, J.mul(t, J.get(G_Math, "sin")(J.mul(angleDeg, DEG))))))
    def wrapDelta(delta=J.undefined, *_args):
        return J.sub(J.mod(J.add(J.mod(delta, 360), 540), 360), 180)
    def radiusAt(stepIndex=J.undefined, totalSteps=J.undefined, *_args):
        return (1 if J.le(totalSteps, 1) else J.add(INNER_RADIUS_FRAC, J.mul(J.sub(1, INNER_RADIUS_FRAC), J.div(stepIndex, J.sub(totalSteps, 1)))))
    def screenRotation(fromPt=J.undefined, toPt=J.undefined, *_args):
        dxScreen = J.mul(J.div(J.sub(J.get(toPt, "x"), J.get(fromPt, "x")), J.sub(maxX, minX)), J.get(tableDimensions, "w"))
        dyScreen = J.mul(J.div(J.neg(J.sub(J.get(toPt, "y"), J.get(fromPt, "y"))), J.sub(maxY, minY)), J.get(tableDimensions, "h"))
        return J.add(J.div(J.get(G_Math, "atan2")(dyScreen, dxScreen), DEG), 90)
    MIN_DOT_SIZE = 0.5
    MAX_DOT_SIZE = 6
    INTERP_DEGREES_PER_DOT = 2
    MIN_DOTS_PER_SEGMENT = 10
    chartDatasets = J.JSArray([])
    labelAnnotations = J.obj()
    placedLabels = J.JSArray([])
    i_2 = 0
    while J.lt(i_2, J.get(SECTORS, "length")):
        sectorTicker = J.get(J.get(SECTORS, i_2), "ticker")
        sectorColor = J.get(J.get(SECTORS, i_2), "color")
        observations = J.JSArray([])
        candleIdx = 0
        while J.lt(candleIdx, J.get(J.get(sectorRSData, i_2), "length")):
            rsValue = J.get(J.get(sectorRSData, i_2), candleIdx)
            momentumValue = J.get(J.get(sectorRSMomentumData, i_2), candleIdx)
            if ((((rsValue is None) or (momentumValue is None)) or (not J.truthy(G_isFinite(rsValue)))) or (not J.truthy(G_isFinite(momentumValue)))):
                candleIdx = J.inc(candleIdx)
                continue
            J.get(observations, "push")(J.obj(("rawAngle", J.div(J.get(G_Math, "atan2")(J.sub(momentumValue, 100), J.sub(J.mul(rsValue, 100), 100)), DEG)), ("volume", (0 if J.nullish(_t8 := J.get(J.get(sectorVolumeData, i_2), candleIdx)) else _t8))))
            candleIdx = J.inc(candleIdx)
        if J.lt(J.get(observations, "length"), 2):
            i_2 = J.inc(i_2)
            continue
        angles = J.JSArray([J.get(J.get(observations, 0), "rawAngle")])
        k = 1
        while J.lt(k, J.get(observations, "length")):
            J.get(angles, "push")(J.add(J.get(angles, J.sub(k, 1)), wrapDelta(J.sub(J.get(J.get(observations, k), "rawAngle"), J.get(angles, J.sub(k, 1))))))
            k = J.inc(k)
        totalSteps = J.get(angles, "length")
        interpData = J.JSArray([])
        interpRadii = J.JSArray([])
        arrowData = J.JSArray([])
        arrowRotations = J.JSArray([])
        k_2 = 0
        while J.lt(k_2, J.sub(totalSteps, 1)):
            angleSpan = J.get(G_Math, "abs")(J.sub(J.get(angles, J.add(k_2, 1)), J.get(angles, k_2)))
            steps = J.get(G_Math, "max")(MIN_DOTS_PER_SEGMENT, J.get(G_Math, "round")(J.div(angleSpan, INTERP_DEGREES_PER_DOT)))
            vol1 = J.get(J.get(observations, k_2), "volume")
            vol2 = J.get(J.get(observations, J.add(k_2, 1)), "volume")
            s = 0
            while J.lt(s, steps):
                t = J.div(s, steps)
                angle = J.add(J.get(angles, k_2), J.mul(J.sub(J.get(angles, J.add(k_2, 1)), J.get(angles, k_2)), t))
                radius = radiusAt(J.add(k_2, t), totalSteps)
                J.get(interpData, "push")(polarToXY(angle, radius))
                vol = J.add(vol1, J.mul(J.sub(vol2, vol1), t))
                J.get(interpRadii, "push")(J.add(MIN_DOT_SIZE, J.mul(vol, J.sub(MAX_DOT_SIZE, MIN_DOT_SIZE))))
                s = J.inc(s)
            midAngle = J.add(J.get(angles, k_2), J.mul(J.sub(J.get(angles, J.add(k_2, 1)), J.get(angles, k_2)), 0.5))
            midRadius = radiusAt(J.add(k_2, 0.5), totalSteps)
            tangentStep = 0.02
            tangentAngle = J.add(J.get(angles, k_2), J.mul(J.sub(J.get(angles, J.add(k_2, 1)), J.get(angles, k_2)), J.add(0.5, tangentStep)))
            tangentRadius = radiusAt(J.add(J.add(k_2, 0.5), tangentStep), totalSteps)
            midPoint = polarToXY(midAngle, midRadius)
            aheadPoint = polarToXY(tangentAngle, tangentRadius)
            J.get(arrowData, "push")(midPoint)
            J.get(arrowRotations, "push")(screenRotation(midPoint, aheadPoint))
            k_2 = J.inc(k_2)
        J.get(chartDatasets, "push")(J.obj(("label", J.template(sectorTicker, "_interp")), ("data", interpData), ("showLine", False), ("borderWidth", 0), ("backgroundColor", withAlpha(sectorColor, 0.7)), ("borderColor", withAlpha(sectorColor, 0.7)), ("pointRadius", interpRadii), ("pointStyle", "circle")))
        J.get(chartDatasets, "push")(J.obj(("label", J.template(sectorTicker, "_arrows")), ("data", arrowData), ("showLine", False), ("borderWidth", 0), ("backgroundColor", sectorColor), ("borderColor", sectorColor), ("pointRadius", 5), ("pointStyle", "triangle"), ("rotation", arrowRotations)))
        def _f9(angle_2=J.undefined, k_3=J.undefined, *_args):
            return polarToXY(angle_2, radiusAt(k_3, totalSteps))
        markerData = J.get(angles, "map")(_f9)
        def _f10(__=J.undefined, pointIndex=J.undefined, *_args):
            return (5 if J.seq(pointIndex, J.sub(totalSteps, 1)) else 2)
        J.get(chartDatasets, "push")(J.obj(("label", sectorTicker), ("data", markerData), ("showLine", False), ("borderWidth", 0), ("backgroundColor", sectorColor), ("borderColor", sectorColor), ("pointRadius", J.get(markerData, "map")(_f10)), ("pointStyle", "circle")))
        lastPoint = J.get(markerData, J.sub(totalSteps, 1))
        netRotation = J.get(G_Math, "round")(J.sub(J.get(angles, J.sub(totalSteps, 1)), J.get(angles, 0)))
        LABEL_X_CLEARANCE = 2.4
        LABEL_Y_CLEARANCE = 0.9
        LABEL_STACK_PX = 14
        nearTop = J.gt(J.get(lastPoint, "y"), J.add(CY, J.mul(0.8, HALF_RANGE)))
        stackDir = (1 if J.truthy(nearTop) else (-1))
        yAdjust = J.mul(10, stackDir)
        collided = True
        guard = 0
        while (J.truthy(collided) and J.lt(guard, 12)):
            def _f11(placed=J.undefined, *_args):
                return (J.lt(J.get(G_Math, "abs")(J.sub(yAdjust, J.get(placed, "yAdjust"))), LABEL_STACK_PX) if J.truthy(_t1 := (J.lt(J.get(G_Math, "abs")(J.sub(J.get(lastPoint, "y"), J.get(placed, "y"))), LABEL_Y_CLEARANCE) if J.truthy(_t2 := J.lt(J.get(G_Math, "abs")(J.sub(J.get(lastPoint, "x"), J.get(placed, "x"))), LABEL_X_CLEARANCE)) else _t2)) else _t1)
            collided = J.get(placedLabels, "some")(_f11)
            if J.truthy(collided):
                yAdjust = J.add(yAdjust, J.mul(LABEL_STACK_PX, stackDir))
            guard = J.inc(guard)
        J.get(placedLabels, "push")(J.obj(("x", J.get(lastPoint, "x")), ("y", J.get(lastPoint, "y")), ("yAdjust", yAdjust)))
        J.set(labelAnnotations, J.template("label_", i_2), J.obj(("type", "label"), ("xValue", J.get(lastPoint, "x")), ("yValue", J.get(lastPoint, "y")), ("content", J.JSArray([J.template(sectorTicker, " ", ("+" if J.gt(netRotation, 0) else ""), netRotation, "u00B0")])), ("color", sectorColor), ("font", J.obj(("size", 11), ("weight", "bold"))), ("position", J.obj(("x", "center"), ("y", ("bottom" if J.truthy(nearTop) else "top")))), ("textStrokeColor", ("black" if J.truthy(mySolidBackground) else "var(--background-color)")), ("textStrokeWidth", 2), ("xAdjust", 0), ("yAdjust", yAdjust)))
        i_2 = J.inc(i_2)
    ringAnnotations = J.obj()
    MAX_RINGS = 8
    totalPeriods = myHistoryLength
    ringCount = J.get(G_Math, "min")(J.sub(totalPeriods, 1), MAX_RINGS)
    ringIdx = 1
    while J.le(ringIdx, ringCount):
        periodPos = J.div(J.mul(ringIdx, J.sub(totalPeriods, 1)), ringCount)
        frac = radiusAt(periodPos, totalPeriods)
        rx = J.mul(frac, HALF_RANGE)
        ry = J.mul(frac, HALF_RANGE)
        periodsBack = J.get(G_Math, "round")(J.sub(J.sub(totalPeriods, 1), periodPos))
        isNowRing = J.seq(periodsBack, 0)
        recency = J.div(ringIdx, ringCount)
        ringColor = ("rgba(255, 255, 255, 0.7)" if J.truthy(isNowRing) else J.template("rgba(160, 160, 160, ", J.get(J.add(0.15, J.mul(0.35, recency)), "toFixed")(2), ")"))
        ringPts = J.JSArray([])
        v = 0
        while J.le(v, 8):
            J.get(ringPts, "push")(polarToXY(J.mul(v, 45), frac))
            v = J.inc(v)
        J.get(chartDatasets, "push")(J.obj(("label", J.template("_ring_", ringIdx)), ("data", ringPts), ("showLine", True), ("fill", False), ("borderColor", ringColor), ("borderWidth", (1.5 if J.truthy(isNowRing) else 1)), ("pointRadius", 0), ("pointHitRadius", 0), ("tension", 0), ("order", 98)))
        J.set(ringAnnotations, J.template("ring_", ringIdx, "_label"), J.obj(("type", "label"), ("xValue", CX), ("yValue", J.add(CY, J.mul(frac, HALF_RANGE))), ("content", J.JSArray([("now" if J.truthy(isNowRing) else J.template("-", periodsBack))])), ("color", ("rgba(255, 255, 255, 0.8)" if J.truthy(isNowRing) else J.template("rgba(170, 170, 170, ", J.get(J.add(0.3, J.mul(0.4, recency)), "toFixed")(2), ")"))), ("font", J.obj(("size", 9))), ("position", J.obj(("x", "center"), ("y", "start"))), ("drawTime", "beforeDatasetsDraw")))
        ringIdx = J.inc(ringIdx)
    OCTANTS = J.JSArray([J.obj(("centerAngle", 22.5), ("label", "Strong leader"), ("color", myOctantColor1), ("fillAlpha", 0.1)), J.obj(("centerAngle", 67.5), ("label", "Accelerating"), ("color", myOctantColor2), ("fillAlpha", 0.07)), J.obj(("centerAngle", 112.5), ("label", "Turning up"), ("color", myOctantColor3), ("fillAlpha", 0.07)), J.obj(("centerAngle", 157.5), ("label", "Bottoming"), ("color", myOctantColor4), ("fillAlpha", 0.05)), J.obj(("centerAngle", 202.5), ("label", "Deep laggard"), ("color", myOctantColor5), ("fillAlpha", 0.1)), J.obj(("centerAngle", 247.5), ("label", "Falling"), ("color", myOctantColor6), ("fillAlpha", 0.07)), J.obj(("centerAngle", 292.5), ("label", "Rolling over"), ("color", myOctantColor7), ("fillAlpha", 0.07)), J.obj(("centerAngle", 337.5), ("label", "Losing steam"), ("color", myOctantColor8), ("fillAlpha", 0.05))])
    octantAnnotations = J.obj()
    def _f12(boundaryAngle=J.undefined, idx=J.undefined, *_args):
        edge = polarToXY(boundaryAngle, 1)
        J.set(octantAnnotations, J.template("octantBoundary_", idx), J.obj(("type", "line"), ("xMin", CX), ("xMax", J.get(edge, "x")), ("yMin", CY), ("yMax", J.get(edge, "y")), ("borderColor", "rgba(128, 128, 128, 0.25)"), ("borderWidth", 1), ("borderDash", J.JSArray([4, 4])), ("drawTime", "beforeDatasetsDraw")))
    J.get(J.JSArray([45, 135, 225, 315]), "forEach")(_f12)
    def _f13(octant=J.undefined, idx=J.undefined, *_args):
        labelPoint = polarToXY(J.get(octant, "centerAngle"), 1.1)
        J.set(octantAnnotations, J.template("octantLabel_", idx), J.obj(("type", "label"), ("xValue", J.get(labelPoint, "x")), ("yValue", J.get(labelPoint, "y")), ("position", J.obj(("x", "center"), ("y", "center"))), ("content", J.JSArray([J.get(octant, "label")])), ("color", J.get(octant, "color")), ("font", J.obj(("size", 12), ("weight", "bold"))), ("padding", 5)))
        wedgeData = J.JSArray([J.obj(("x", CX), ("y", CY))])
        startAngle = J.sub(J.get(octant, "centerAngle"), 22.5)
        ARC_STEP_DEG = 3
        a = 0
        while J.le(a, 45):
            J.get(wedgeData, "push")(polarToXY(J.add(startAngle, a), 1))
            a = J.add(a, ARC_STEP_DEG)
        J.get(wedgeData, "push")(J.obj(("x", CX), ("y", CY)))
        J.get(chartDatasets, "push")(J.obj(("label", J.template("_octant_fill_", idx)), ("data", wedgeData), ("showLine", True), ("fill", "shape"), ("backgroundColor", withAlpha(J.get(octant, "color"), J.get(octant, "fillAlpha"))), ("borderWidth", 0), ("borderColor", "transparent"), ("pointRadius", 0), ("pointHitRadius", 0), ("tension", 0), ("order", 99)))
    J.get(OCTANTS, "forEach")(_f13)
    G_paint_overlay("Chart", J.obj(("position", "bottom_left"), ("offset_x", 0), ("offset_y", 0), ("order", "above_all")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("chart", J.obj(("width", J.template(J.get(tableDimensions, "w"), "px")), ("height", J.template(J.get(tableDimensions, "h"), "px")), ("type", "scatter"), ("options", J.obj(("showLine", False), ("scales", J.obj(("x", J.obj(("type", "linear"), ("min", minX), ("max", maxX), ("ticks", J.obj(("display", False))), ("title", J.obj(("display", False))), ("border", J.obj(("display", False))), ("grid", J.obj(("display", False))))), ("y", J.obj(("type", "linear"), ("min", minY), ("max", maxY), ("ticks", J.obj(("display", False))), ("title", J.obj(("display", False))), ("border", J.obj(("display", False))), ("grid", J.obj(("display", False))))))), ("plugins", J.obj(("legend", J.obj(("display", False))), ("annotation", J.obj(("annotations", J.obj(*J.obj_spread((J.obj(("chartBackground", J.obj(("type", "box"), ("xMin", minX), ("xMax", maxX), ("yMin", minY), ("yMax", maxY), ("backgroundColor", "rgba(0, 0, 0, 0.92)"), ("borderWidth", 0), ("drawTime", "beforeDraw")))) if J.truthy(mySolidBackground) else J.obj())), *J.obj_spread(ringAnnotations), ("verticalLine", J.obj(("type", "line"), ("xMin", CX), ("xMax", CX), ("yMin", J.sub(CY, HALF_RANGE)), ("yMax", J.add(CY, HALF_RANGE)), ("borderColor", "rgba(128, 128, 128, 0.5)"), ("borderWidth", 2), ("borderDash", J.JSArray([5, 5])), ("drawTime", "beforeDatasetsDraw"))), ("horizontalLine", J.obj(("type", "line"), ("yMin", CY), ("yMax", CY), ("xMin", J.sub(CX, HALF_RANGE)), ("xMax", J.add(CX, HALF_RANGE)), ("borderColor", "rgba(128, 128, 128, 0.5)"), ("borderWidth", 2), ("borderDash", J.JSArray([5, 5])), ("drawTime", "beforeDatasetsDraw"))), *J.obj_spread(octantAnnotations), *J.obj_spread(labelAnnotations))))))))), ("data", J.obj(("datasets", chartDatasets))))))])))]))))


register_store_indicator(
    script,
    name='sector_rotation_chart_TS',
    title='Sector Rotation Chart',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69a731-sector-rotation-chart/',
    position='price',
    inputs=[{'id': 'show_1', 'title': 'Show 1', 'type': 'boolean', 'default': True}, {'id': 'sym-symbol_1', 'title': 'Symbol 1', 'type': 'symbol-search', 'default': 'XLE'}, {'id': 'color_1', 'title': 'Color 1', 'type': 'color', 'default': '#FF5722'}, {'id': 'show_2', 'title': 'Show 2', 'type': 'boolean', 'default': True}, {'id': 'sym-symbol_2', 'title': 'Symbol 2', 'type': 'symbol-search', 'default': 'XLB'}, {'id': 'color_2', 'title': 'Color 2', 'type': 'color', 'default': '#795548'}, {'id': 'show_3', 'title': 'Show 3', 'type': 'boolean', 'default': True}, {'id': 'sym-symbol_3', 'title': 'Symbol 3', 'type': 'symbol-search', 'default': 'XLI'}, {'id': 'color_3', 'title': 'Color 3', 'type': 'color', 'default': '#607D8B'}, {'id': 'show_4', 'title': 'Show 4', 'type': 'boolean', 'default': True}, {'id': 'sym-symbol_4', 'title': 'Symbol 4', 'type': 'symbol-search', 'default': 'XLY'}, {'id': 'color_4', 'title': 'Color 4', 'type': 'color', 'default': '#FFA500'}, {'id': 'show_5', 'title': 'Show 5', 'type': 'boolean', 'default': False}, {'id': 'sym-symbol_5', 'title': 'Symbol 5', 'type': 'symbol-search', 'default': 'XLP'}, {'id': 'color_5', 'title': 'Color 5', 'type': 'color', 'default': '#28A745'}, {'id': 'show_6', 'title': 'Show 6', 'type': 'boolean', 'default': True}, {'id': 'sym-symbol_6', 'title': 'Symbol 6', 'type': 'symbol-search', 'default': 'XLV'}, {'id': 'color_6', 'title': 'Color 6', 'type': 'color', 'default': '#DC3545'}, {'id': 'show_7', 'title': 'Show 7', 'type': 'boolean', 'default': True}, {'id': 'sym-symbol_7', 'title': 'Symbol 7', 'type': 'symbol-search', 'default': 'XLF'}, {'id': 'color_7', 'title': 'Color 7', 'type': 'color', 'default': '#1E90FF'}, {'id': 'show_8', 'title': 'Show 8', 'type': 'boolean', 'default': True}, {'id': 'sym-symbol_8', 'title': 'Symbol 8', 'type': 'symbol-search', 'default': 'XLK'}, {'id': 'color_8', 'title': 'Color 8', 'type': 'color', 'default': '#00BCD4'}, {'id': 'show_9', 'title': 'Show 9', 'type': 'boolean', 'default': False}, {'id': 'sym-symbol_9', 'title': 'Symbol 9', 'type': 'symbol-search', 'default': 'XLC'}, {'id': 'color_9', 'title': 'Color 9', 'type': 'color', 'default': '#9C27B0'}, {'id': 'show_10', 'title': 'Show 10', 'type': 'boolean', 'default': False}, {'id': 'sym-symbol_10', 'title': 'Symbol 10', 'type': 'symbol-search', 'default': 'XLU'}, {'id': 'color_10', 'title': 'Color 10', 'type': 'color', 'default': '#6366F1'}, {'id': 'show_11', 'title': 'Show 11', 'type': 'boolean', 'default': False}, {'id': 'sym-symbol_11', 'title': 'Symbol 11', 'type': 'symbol-search', 'default': 'XLRE'}, {'id': 'color_11', 'title': 'Color 11', 'type': 'color', 'default': '#009688'}, {'id': 'sym-benchmark', 'title': 'Benchmark', 'type': 'symbol-search', 'default': 'VTI'}, {'id': 'timeframe', 'title': 'Timeframe', 'type': 'select_wide', 'default': 'Weekly', 'options': ['Weekly', 'Monthly']}, {'id': 'tail_length', 'title': 'Tail length', 'type': 'number', 'default': 5}, {'id': 'solid_background', 'title': 'Solid background', 'type': 'boolean', 'default': True}, {'id': 'slice__strong_leader', 'title': 'Slice: Strong leader', 'type': 'color', 'default': '#32CD32'}, {'id': 'slice__accelerating', 'title': 'Slice: Accelerating', 'type': 'color', 'default': '#9ACD32'}, {'id': 'slice__turning_up', 'title': 'Slice: Turning up', 'type': 'color', 'default': '#4DD0E1'}, {'id': 'slice__bottoming', 'title': 'Slice: Bottoming', 'type': 'color', 'default': '#AAAAAA'}, {'id': 'slice__deep_laggard', 'title': 'Slice: Deep laggard', 'type': 'color', 'default': '#DC3545'}, {'id': 'slice__falling', 'title': 'Slice: Falling', 'type': 'color', 'default': '#E57373'}, {'id': 'slice__rolling_over', 'title': 'Slice: Rolling over', 'type': 'color', 'default': '#FFA726'}, {'id': 'slice__losing_steam', 'title': 'Slice: Losing steam', 'type': 'color', 'default': '#AAAAAA'}, {'id': 'chart_size', 'title': 'Chart size', 'type': 'select_wide', 'default': 'medium', 'options': ['small', 'medium', 'large', 'xlarge']}],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='exact',
)
