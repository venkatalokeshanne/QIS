"""
Prior Day High/Low Fib Levels v2.6 -- TrendSpider store indicator by James.

Registered as "prior_day_high_low_fib_levels_v2_6_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a7c92-prior-day-high-low-fib-levels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_shift = G["shift"]
    G_time = G["time"]
    def isGolden(f=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.lt(J.get(G_Math, "abs")(J.sub(f, 0.618)), 0.02)) else J.lt(J.get(G_Math, "abs")(J.sub(f, 0.786)), 0.02))) else J.lt(J.get(G_Math, "abs")(J.sub(f, 1.618)), 0.02))
    def isBoundary(f=J.undefined, *_args):
        return (_t1 if J.truthy(_t1 := J.le(f, 0.001)) else J.ge(f, 0.999))
    def colorForFib(f=J.undefined, *_args):
        if J.truthy(isGolden(f)):
            return C_GOLD
        if J.truthy(isBoundary(f)):
            return C_ANCHOR
        return C_LEVEL
    def thicknessForFib(f=J.undefined, *_args):
        if (J.truthy(isGolden(f)) or J.truthy(isBoundary(f))):
            return 2
        return 1
    def styleForFib(f=J.undefined, *_args):
        return ("dotted" if J.lt(J.get(G_Math, "abs")(J.sub(f, 0.5)), 0.02) else "line")
    def applyBreaks(series=J.undefined, *_args):
        if (not J.truthy(breakSessions)):
            return series
        def _f1(v=J.undefined, i=J.undefined, *_args):
            return (None if J.truthy(J.get(sessionEnd, i)) else v)
        return J.get(series, "map")(_f1)
    def buildLevel(fib=J.undefined, mode=J.undefined, *_args):
        def _f1(priorLow=J.undefined, i=J.undefined, *_args):
            priorHigh = J.get(intradayHigh, i)
            if ((priorLow is None) or (priorHigh is None)):
                return None
            range = J.sub(priorHigh, priorLow)
            if J.seq(mode, "up"):
                return J.add(priorLow, J.mul(range, fib))
            if J.seq(mode, "down"):
                return J.sub(priorHigh, J.mul(range, fib))
            return (J.sub(priorHigh, J.mul(range, fib)) if J.truthy(fromHigh) else J.add(priorLow, J.mul(range, fib)))
        return J.get(intradayLow, "map")(_f1)
    def paintLevel(fib=J.undefined, mode=J.undefined, seriesName=J.undefined, showLine=J.undefined, *_args):
        visible = (True if (showLine is J.undefined) else showLine)
        G_paint((applyBreaks(G_interpolate_sparse_series(buildLevel(fib, mode), "constant")) if J.truthy(visible) else G_series_of(None)), J.obj(("style", (styleForFib(fib) if J.seq(mode, "retrace") else "dotted")), ("color", colorForFib(fib)), ("thickness", thicknessForFib(fib)), ("name", seriesName)))
    G_describe_indicator("Prior Day High/Low Fib Levels v2.5")
    G_assert((not J.truthy(J.get(J.JSArray(["D", "W", "M", "Q", "Y"]), "includes")(J.get(G_constants, "resolution")))), J.template("not applicable to \"", J.get(G_constants, "resolution"), "\" charts"))
    showHL = J.get(G_input, "boolean")("Show Prior Day High/Low", True)
    breakSessions = J.get(G_input, "boolean")("Break Lines at Session End", True)
    fromHigh = J.get(G_input, "boolean")("Measure From High", False)
    fib1 = J.get(G_input, "number")("Fib Level 1", 0, J.obj(("min", 0), ("max", 1)))
    fib2 = J.get(G_input, "number")("Fib Level 2", 0.236, J.obj(("min", 0), ("max", 1)))
    fib3 = J.get(G_input, "number")("Fib Level 3", 0.382, J.obj(("min", 0), ("max", 1)))
    fib4 = J.get(G_input, "number")("Fib Level 4", 0.5, J.obj(("min", 0), ("max", 1)))
    fib5 = J.get(G_input, "number")("Fib Level 5", 0.618, J.obj(("min", 0), ("max", 1)))
    fib6 = J.get(G_input, "number")("Fib Level 6", 0.786, J.obj(("min", 0), ("max", 1)))
    fib7 = J.get(G_input, "number")("Fib Level 7", 1, J.obj(("min", 0), ("max", 1)))
    fibArray = J.JSArray([fib1, fib2, fib3, fib4, fib5, fib6, fib7])
    showExt = J.get(G_input, "boolean")("Show Extensions", False)
    ext1 = J.get(G_input, "number")("Extension 1", 1.272, J.obj(("min", 1), ("max", 5)))
    ext2 = J.get(G_input, "number")("Extension 2", 1.618, J.obj(("min", 1), ("max", 5)))
    ext3 = J.get(G_input, "number")("Extension 3", 2, J.obj(("min", 1), ("max", 5)))
    extArray = J.JSArray([ext1, ext2, ext3])
    C_ANCHOR = "#607d8b"
    C_LEVEL = "#90a4ae"
    C_GOLD = "#c9a227"
    data = J.get(G_request, "history")(J.get(G_constants, "ticker"), "D")
    priorDayHigh = G_shift(J.get(data, "high"), 1)
    priorDayLow = G_shift(J.get(data, "low"), 1)
    intradayHigh = G_land_points_onto_series(J.get(data, "time"), priorDayHigh, G_time)
    intradayLow = G_land_points_onto_series(J.get(data, "time"), priorDayLow, G_time)
    dayStamp = G_interpolate_sparse_series(G_land_points_onto_series(J.get(data, "time"), J.get(data, "time"), G_time), "constant")
    lastIdx = J.sub(J.get(dayStamp, "length"), 1)
    def _f1(d=J.undefined, i=J.undefined, *_args):
        if J.ge(i, lastIdx):
            return False
        return J.sne(J.get(dayStamp, J.add(i, 1)), d)
    sessionEnd = J.get(dayStamp, "map")(_f1)
    G_paint((applyBreaks(G_interpolate_sparse_series(intradayHigh, "constant")) if J.truthy(showHL) else G_series_of(None)), J.obj(("style", "line"), ("color", C_ANCHOR), ("thickness", 2), ("name", "Prior Day High")))
    G_paint((applyBreaks(G_interpolate_sparse_series(intradayLow, "constant")) if J.truthy(showHL) else G_series_of(None)), J.obj(("style", "line"), ("color", C_ANCHOR), ("thickness", 2), ("name", "Prior Day Low")))
    fibNames = J.JSArray(["Fib 1", "Fib 2", "Fib 3", "Fib 4", "Fib 5", "Fib 6", "Fib 7"])
    def _f2(f=J.undefined, index=J.undefined, *_args):
        return paintLevel(f, "retrace", J.get(fibNames, index), True)
    J.get(fibArray, "forEach")(_f2)
    upNames = J.JSArray(["Ext Up 1", "Ext Up 2", "Ext Up 3"])
    downNames = J.JSArray(["Ext Down 1", "Ext Down 2", "Ext Down 3"])
    def _f3(f=J.undefined, index=J.undefined, *_args):
        paintLevel(f, "up", J.get(upNames, index), showExt)
        paintLevel(f, "down", J.get(downNames, index), showExt)
    J.get(extArray, "forEach")(_f3)


register_store_indicator(
    script,
    name='prior_day_high_low_fib_levels_v2_6_TS',
    title='Prior Day High/Low Fib Levels v2.6',
    developer='James',
    url='https://trendspider.com/trading-tools-store/indicators/6a7c92-prior-day-high-low-fib-levels/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='aapl_d: both-error, syn_5m: OK',
)
