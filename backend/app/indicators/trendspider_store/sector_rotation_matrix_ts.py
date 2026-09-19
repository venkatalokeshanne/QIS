"""
Sector Rotation Matrix -- TrendSpider store indicator by Gustivus.

Registered as "sector_rotation_matrix_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/696077-sector-rotation-matrix/)
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
    G_console = G["console"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("Sector Rotation Matrix", "lower", J.obj(("shortName", "SectorRotation")))
    sectors = J.get(G_input, "text")("Sectors (max 5, comma)", "XLK,XLF,XLV,XLE,XLI")
    benchmark = J.get(G_input, "symbol")("Benchmark", "SPY")
    rotationThreshold = J.get(G_input, "number")("Rotation Threshold", 1.5, J.obj(("min", 0.5), ("max", 3), ("step", 0.1)))
    displayMode = J.get(G_input, "select")("Display Mode", "Rotation Score", J.JSArray(["Rotation Score", "Relative Strength", "Volume Flow", "Combined Signal"]))
    def fetchSectorData(ticker=J.undefined, *_args):
        res = J.get(G_request, "history")(ticker, J.get(G_current, "resolution"))
        if J.truthy(J.get(res, "error")):
            J.get(G_console, "warn")(J.template("Error fetching ", ticker, ": ", J.get(res, "error")))
            return None
        return res
    def alignToChart(data=J.undefined, dataTime=J.undefined, chartTime_2=J.undefined, *_args):
        map = J.obj()
        i = 0
        while J.lt(i, J.get(dataTime, "length")):
            J.set(map, J.get(dataTime, i), J.get(data, i))
            i = J.inc(i)
        def _f1(t=J.undefined, *_args):
            return (None if J.nullish(_t1 := J.get(map, t)) else _t1)
        return J.get(chartTime_2, "map")(_f1)
    def createFilledArray(length=J.undefined, value=J.undefined, *_args):
        arr = J.JSArray([])
        i = 0
        while J.lt(i, length):
            J.get(arr, "push")(value)
            i = J.inc(i)
        return arr
    def createNullSeries(value=J.undefined, *_args):
        return createFilledArray(J.get(G_time, "length"), value)
    def calcRelativeStrength(sectorClose=J.undefined, benchClose=J.undefined, *_args):
        result = J.JSArray([])
        i = 0
        while J.lt(i, J.get(sectorClose, "length")):
            if J.lt(i, 20):
                J.get(result, "push")(None)
                i = J.inc(i)
                continue
            sectorStart = J.get(sectorClose, J.sub(i, 20))
            sectorEnd = J.get(sectorClose, i)
            benchStart = J.get(benchClose, J.sub(i, 20))
            benchEnd = J.get(benchClose, i)
            if (((J.truthy(sectorStart) and J.truthy(sectorEnd)) and J.truthy(benchStart)) and J.truthy(benchEnd)):
                sectorReturn = J.div(J.sub(sectorEnd, sectorStart), sectorStart)
                benchReturn = J.div(J.sub(benchEnd, benchStart), benchStart)
                J.get(result, "push")(J.mul(J.sub(J.div(J.add(1, sectorReturn), J.add(1, benchReturn)), 1), 100))
            else:
                J.get(result, "push")(None)
            i = J.inc(i)
        return result
    def calcVolumeIntensity(volume=J.undefined, closeData=J.undefined, *_args):
        result = J.JSArray([])
        i = 0
        while J.lt(i, J.get(volume, "length")):
            if J.lt(i, 20):
                J.get(result, "push")(None)
                i = J.inc(i)
                continue
            vwSum = 0
            volSum = 0
            validCount = 0
            j = J.sub(i, 19)
            while J.le(j, i):
                if (((J.gt(j, 0) and J.truthy(J.get(volume, j))) and J.truthy(J.get(closeData, j))) and J.truthy(J.get(closeData, J.sub(j, 1)))):
                    ret = J.div(J.sub(J.get(closeData, j), J.get(closeData, J.sub(j, 1))), J.get(closeData, J.sub(j, 1)))
                    vwSum = J.add(vwSum, J.mul(ret, J.get(volume, j)))
                    volSum = J.add(volSum, J.get(volume, j))
                    validCount = J.inc(validCount)
                j = J.inc(j)
            if (J.gt(validCount, 10) and J.gt(volSum, 0)):
                J.get(result, "push")(J.mul(J.div(vwSum, volSum), 1000))
            else:
                J.get(result, "push")(None)
            i = J.inc(i)
        return result
    def normalizeToZScore(series=J.undefined, *_args):
        result = J.JSArray([])
        i = 0
        while J.lt(i, J.get(series, "length")):
            if J.lt(i, 60):
                J.get(result, "push")(None)
                i = J.inc(i)
                continue
            window = J.JSArray([])
            j = J.sub(i, 59)
            while J.le(j, i):
                if (not J.nullish(J.get(series, j))):
                    J.get(window, "push")(J.get(series, j))
                j = J.inc(j)
            if J.lt(J.get(window, "length"), 20):
                J.get(result, "push")(None)
                i = J.inc(i)
                continue
            def _f1(a=J.undefined, b=J.undefined, *_args):
                return J.add(a, b)
            meanVal = J.div(J.get(window, "reduce")(_f1, 0), J.get(window, "length"))
            def _f2(v=J.undefined, *_args):
                return J.get(G_Math, "pow")(J.sub(v, meanVal), 2)
            squaredDiffs = J.get(window, "map")(_f2)
            def _f3(a=J.undefined, b=J.undefined, *_args):
                return J.add(a, b)
            varVal = J.div(J.get(squaredDiffs, "reduce")(_f3, 0), J.get(window, "length"))
            stdVal = J.get(G_Math, "sqrt")(varVal)
            if (J.seq(stdVal, 0) or (J.nullish(J.get(series, i)))):
                J.get(result, "push")(None)
            else:
                J.get(result, "push")(J.div(J.sub(J.get(series, i), meanVal), stdVal))
            i = J.inc(i)
        return result
    def smoothData(series=J.undefined, window=J.undefined, *_args):
        result = J.JSArray([])
        i = 0
        while J.lt(i, J.get(series, "length")):
            if J.lt(i, J.sub(window, 1)):
                J.get(result, "push")(None)
                i = J.inc(i)
                continue
            total = 0
            count = 0
            j = J.add(J.sub(i, window), 1)
            while J.le(j, i):
                if (not J.nullish(J.get(series, j))):
                    total = J.add(total, J.get(series, j))
                    count = J.inc(count)
                j = J.inc(j)
            J.get(result, "push")((J.div(total, count) if J.gt(count, 0) else None))
            i = J.inc(i)
        return result
    def _f1(s=J.undefined, *_args):
        return J.get(s, "trim")()
    sectorList = J.get(J.get(J.get(sectors, "split")(","), "map")(_f1), "slice")(0, 5)
    chartTime = G_time
    rotationScore = createFilledArray(J.get(chartTime, "length"), 0)
    primarySeries = createFilledArray(J.get(chartTime, "length"), 0)
    seriesName = "Market Rotation Intensity"
    seriesColor = "purple"
    sectorMetrics = J.obj()
    dashboardRows = J.JSArray([])
    hasError = False
    errorMessage = ""
    if J.gt(J.get(sectorList, "length"), 5):
        hasError = True
        errorMessage = "Max 5 sectors allowed"
    else:
        benchData = fetchSectorData(benchmark)
        if ((not J.truthy(benchData)) or (not J.truthy(J.get(benchData, "close")))):
            hasError = True
            errorMessage = "Cannot fetch benchmark"
        else:
            benchClose = alignToChart(J.get(benchData, "close"), J.get(benchData, "time"), chartTime)
            for ticker in J.iter_of(sectorList):
                data = fetchSectorData(ticker)
                if (not J.truthy(data)):
                    continue
                closeData = alignToChart(J.get(data, "close"), J.get(data, "time"), chartTime)
                volumeData = alignToChart(J.get(data, "volume"), J.get(data, "time"), chartTime)
                rs = calcRelativeStrength(closeData, benchClose)
                vi = calcVolumeIntensity(volumeData, closeData)
                rsZ = normalizeToZScore(rs)
                viZ = normalizeToZScore(vi)
                combined = J.JSArray([])
                i = 0
                while J.lt(i, J.get(rsZ, "length")):
                    if ((J.nullish(J.get(rsZ, i))) and (J.nullish(J.get(viZ, i)))):
                        J.get(combined, "push")(None)
                    elif (J.nullish(J.get(rsZ, i))):
                        J.get(combined, "push")(J.mul(J.get(viZ, i), 0.4))
                    elif (J.nullish(J.get(viZ, i))):
                        J.get(combined, "push")(J.mul(J.get(rsZ, i), 0.6))
                    else:
                        J.get(combined, "push")(J.add(J.mul(J.get(rsZ, i), 0.6), J.mul(J.get(viZ, i), 0.4)))
                    i = J.inc(i)
                smoothed = smoothData(combined, 3)
                J.set(sectorMetrics, ticker, J.obj(("relativeStrength", rs), ("volumeIntensity", vi), ("rsZScore", rsZ), ("viZScore", viZ), ("combined", smoothed)))
                i_2 = 0
                while J.lt(i_2, J.get(smoothed, "length")):
                    if ((not J.nullish(J.get(smoothed, i_2))) and J.gt(J.get(G_Math, "abs")(J.get(smoothed, i_2)), rotationThreshold)):
                        J.set(rotationScore, i_2, J.add(J.get(rotationScore, i_2), (1 if J.gt(J.get(smoothed, i_2), 0) else (-1))))
                    i_2 = J.inc(i_2)
    def getCurrentRankings(*_args):
        latest = J.obj()
        for _t1 in J.iter_of(J.get(G_Object, "entries")(sectorMetrics)):
            _t2 = J.iter_of(_t1)
            ticker_2 = (_t2[0] if 0 < len(_t2) else J.undefined)
            metrics = (_t2[1] if 1 < len(_t2) else J.undefined)
            val = J.get(J.get(metrics, "combined"), J.sub(J.get(J.get(metrics, "combined"), "length"), 1))
            if (not J.nullish(val)):
                J.set(latest, ticker_2, val)
        def _f3(a=J.undefined, b=J.undefined, *_args):
            return J.sub(J.get(b, 1), J.get(a, 1))
        def _f4(_p1=J.undefined, *_args):
            _t2 = J.iter_of(_p1)
            ticker_3 = (_t2[0] if 0 < len(_t2) else J.undefined)
            score = (_t2[1] if 1 < len(_t2) else J.undefined)
            return J.obj(("ticker", ticker_3), ("score", score))
        return J.get(J.get(J.get(G_Object, "entries")(latest), "sort")(_f3), "map")(_f4)
    rankings = getCurrentRankings()
    if (not J.truthy(hasError)):
        _t2 = displayMode
        if J.seq(_t2, "Rotation Score"):
            _t3 = 0
        elif J.seq(_t2, "Relative Strength"):
            _t3 = 1
        elif J.seq(_t2, "Volume Flow"):
            _t3 = 2
        elif J.seq(_t2, "Combined Signal"):
            _t3 = 3
        else:
            _t3 = 4
        _c4 = False
        for _once in (0,):
            if _t3 <= 0:
                primarySeries = rotationScore
                seriesName = "Market Rotation Intensity"
                seriesColor = "purple"
                break
            if _t3 <= 1:
                if (J.gt(J.get(rankings, "length"), 0) and J.truthy(J.get(sectorMetrics, J.get(J.get(rankings, 0), "ticker")))):
                    primarySeries = J.get(J.get(sectorMetrics, J.get(J.get(rankings, 0), "ticker")), "relativeStrength")
                    seriesName = J.template(J.get(J.get(rankings, 0), "ticker"), " Relative Strength")
                    seriesColor = "green"
                break
            if _t3 <= 2:
                volFlow = createFilledArray(J.get(chartTime, "length"), 0)
                count = 0
                for metrics in J.iter_of(J.get(G_Object, "values")(sectorMetrics)):
                    i_3 = 0
                    while J.lt(i_3, J.get(J.get(metrics, "viZScore"), "length")):
                        if (not J.nullish(J.get(J.get(metrics, "viZScore"), i_3))):
                            J.set(volFlow, i_3, J.add(J.get(volFlow, i_3), J.get(J.get(metrics, "viZScore"), i_3)))
                        i_3 = J.inc(i_3)
                    count = J.inc(count)
                def _f5(v=J.undefined, *_args):
                    return (J.div(v, count) if J.gt(count, 0) else 0)
                primarySeries = J.get(volFlow, "map")(_f5)
                seriesName = "Aggregate Volume Flow"
                seriesColor = "blue"
                break
            if _t3 <= 3:
                if (J.gt(J.get(rankings, "length"), 0) and J.truthy(J.get(sectorMetrics, J.get(J.get(rankings, 0), "ticker")))):
                    primarySeries = J.get(J.get(sectorMetrics, J.get(J.get(rankings, 0), "ticker")), "combined")
                    seriesName = J.template(J.get(J.get(rankings, 0), "ticker"), " Combined Signal")
                    seriesColor = "orange"
                break
            pass
    rotationSignal = J.JSArray([])
    i_4 = 0
    while J.lt(i_4, J.get(rotationScore, "length")):
        if J.lt(i_4, 2):
            J.get(rotationSignal, "push")(None)
            i_4 = J.inc(i_4)
            continue
        avgVal = J.div(J.add(J.get(rotationScore, i_4), J.get(rotationScore, J.sub(i_4, 1))), 2)
        if J.gt(J.get(G_Math, "abs")(avgVal), J.mul(J.get(sectorList, "length"), 0.3)):
            J.get(rotationSignal, "push")((1 if J.gt(avgVal, 0) else (-1)))
        else:
            J.get(rotationSignal, "push")(0)
        i_4 = J.inc(i_4)
    G_paint(primarySeries, J.obj(("name", seriesName), ("color", seriesColor), ("thickness", 3)))
    G_paint(G_horizontal_line(0), J.obj(("name", "Neutral"), ("color", "gray"), ("style", "dotted")))
    G_paint(G_horizontal_line(rotationThreshold), J.obj(("name", "Upper Threshold"), ("color", "green"), ("style", "dotted")))
    G_paint(G_horizontal_line(J.neg(rotationThreshold)), J.obj(("name", "Lower Threshold"), ("color", "red"), ("style", "dotted")))
    def _f6(s=J.undefined, *_args):
        return (1 if J.seq(s, 1) else None)
    bullishRotation = G_for_every(rotationSignal, _f6)
    def _f7(s=J.undefined, *_args):
        return (1 if J.seq(s, (-1)) else None)
    bearishRotation = G_for_every(rotationSignal, _f7)
    G_register_signal(bullishRotation, "Risk-On Rotation")
    G_register_signal(bearishRotation, "Risk-Off Rotation")
    lastIdx = J.sub(J.get(G_time, "length"), 1)
    currentRotation = (_t8 if J.truthy(_t8 := J.get(rotationScore, lastIdx)) else 0)
    regimeText = "NEUTRAL"
    regimeSymbol = "◆"
    regimeColor = "#808080"
    interpretText = (errorMessage if J.truthy(hasError) else "Balanced sector participation")
    if (not J.truthy(hasError)):
        if J.ge(currentRotation, 3):
            regimeText = "STRONG RISK-ON"
            regimeSymbol = "\ud83d\ude80"
            regimeColor = "#00FF88"
            interpretText = "Broad sector strength"
        elif J.ge(currentRotation, 2):
            regimeText = "MODERATE RISK-ON"
            regimeSymbol = "\ud83d\udcc8"
            regimeColor = "#00A8E1"
            interpretText = "Multiple sectors advancing"
        elif J.ge(currentRotation, 1):
            regimeText = "MILD RISK-ON"
            regimeSymbol = "↗️"
            regimeColor = "#87CEEB"
            interpretText = "Selective sector strength"
        elif J.le(currentRotation, (-3)):
            regimeText = "STRONG RISK-OFF"
            regimeSymbol = "⚠️"
            regimeColor = "#FC3D21"
            interpretText = "Broad sector weakness"
        elif J.le(currentRotation, (-2)):
            regimeText = "MODERATE RISK-OFF"
            regimeSymbol = "\ud83d\udcc9"
            regimeColor = "#FF6B35"
            interpretText = "Multiple sectors declining"
        elif J.le(currentRotation, (-1)):
            regimeText = "MILD RISK-OFF"
            regimeSymbol = "↘️"
            regimeColor = "#FFB347"
            interpretText = "Selective sector weakness"
    dashboardRows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "SECTOR ROTATION"), ("color", "#FFFFFF"), ("textAlign", "center"), ("fontWeight", "bold"), ("fontSize", 11), ("padding", 4))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(regimeSymbol, " ", regimeText)), ("color", regimeColor), ("textAlign", "center"), ("fontWeight", "bold"), ("fontSize", 12), ("padding", 4))]))), J.obj(("cells", J.JSArray([J.obj(("text", interpretText), ("color", "#FFFFFF"), ("textAlign", "center"), ("fontSize", 9), ("padding", 2))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template("Score: ", J.get(currentRotation, "toFixed")(1), " / ", J.get(sectorList, "length"))), ("color", "#FFFFFF"), ("textAlign", "center"), ("fontSize", 10), ("padding", 3))])))])
    if ((not J.truthy(hasError)) and J.gt(J.get(rankings, "length"), 0)):
        topRanked = J.get(rankings, 0)
        bottomRanked = J.get(rankings, J.sub(J.get(rankings, "length"), 1))
        J.get(dashboardRows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", "━━━━━━━━━━━━━━━"), ("color", "#606060"), ("textAlign", "center"), ("fontSize", 8), ("padding", 2))]))), J.obj(("cells", J.JSArray([J.obj(("text", "LEADING"), ("color", "#00A8E1"), ("textAlign", "center"), ("fontSize", 9))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(J.get(topRanked, "ticker"), ": ", J.get(J.get(topRanked, "score"), "toFixed")(2))), ("color", "#00FF88"), ("textAlign", "center"), ("fontSize", 10))]))), J.obj(("cells", J.JSArray([J.obj(("text", "LAGGING"), ("color", "#FF6B35"), ("textAlign", "center"), ("fontSize", 9))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.template(J.get(bottomRanked, "ticker"), ": ", J.get(J.get(bottomRanked, "score"), "toFixed")(2))), ("color", "#FC3D21"), ("textAlign", "center"), ("fontSize", 10))]))))
    G_paint_overlay("ROTATION_DASHBOARD", J.obj(("position", "center_right")), J.obj(("background", "#1a1a2eDD"), ("border", J.template("2px solid ", regimeColor)), ("borderRadius", 6), ("padding", 4), ("rows", dashboardRows)))
    def _f10(r=J.undefined, *_args):
        return J.get(r, "ticker")
    topSectors = (_t9 if J.truthy(_t9 := J.get(J.get(J.get(rankings, "slice")(0, 3), "map")(_f10), "join")(", ")) else "N/A")
    def _f12(r=J.undefined, *_args):
        return J.get(r, "ticker")
    bottomSectors = (_t11 if J.truthy(_t11 := J.get(J.get(J.get(rankings, "slice")((-3)), "map")(_f12), "join")(", ")) else "N/A")
    G_paint_overlay("overlay", J.obj(("position", "bottom_right")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("Leading: ", topSectors)), ("color", "green"), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template("Lagging: ", bottomSectors)), ("color", "red"), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template("Rotation: ", J.get(currentRotation, "toFixed")(1))), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5)), J.obj(("text", J.template("Tracking: ", J.get(sectorList, "length"), " sectors")), ("color", "var(--text-color)"), ("border", "solid var(--border-color) 1px"), ("padding", 5))])))]))))


register_store_indicator(
    script,
    name='sector_rotation_matrix_TS',
    title='Sector Rotation Matrix',
    developer='Gustivus',
    url='https://trendspider.com/trading-tools-store/indicators/696077-sector-rotation-matrix/',
    position='lower',
    inputs=[{'id': 'sectors__max_5__comma_', 'title': 'Sectors (max 5, comma)', 'type': 'text', 'default': 'XLK,XLF,XLV,XLE,XLI'}, {'id': 'sym-benchmark', 'title': 'Benchmark', 'type': 'symbol-search', 'default': 'SPY'}, {'id': 'rotation_threshold', 'title': 'Rotation Threshold', 'type': 'number', 'default': 1.5}, {'id': 'display_mode', 'title': 'Display Mode', 'type': 'select_wide', 'default': 'Rotation Score', 'options': ['Rotation Score', 'Relative Strength', 'Volume Flow', 'Combined Signal']}],
    outputs=['market_rotation_intensity', 'neutral', 'upper_threshold', 'lower_threshold', 'risk_on_rotation', 'risk_off_rotation'],
    signals=['risk_on_rotation', 'risk_off_rotation'],
    requires=['history'],
    parity='exact',
)
