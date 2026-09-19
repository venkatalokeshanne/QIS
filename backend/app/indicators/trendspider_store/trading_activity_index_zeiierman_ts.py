"""
Trading Activity Index (Zeiierman) -- TrendSpider store indicator by Zeiierman Trading.

Registered as "trading_activity_index_zeiierman_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68e78d-trading-activity-index-zeiierman/)
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
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_lowest = G["lowest"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_sliding_window_function = G["sliding_window_function"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("Trading Activity Index (Zeiierman)", "lower", J.obj(("decimals", 0), ("shortName", "Trading Activity Index (Zeiierman)"), ("warmup", 1500)))
    myFormationWindow = J.get(G_input, "number")("Formation Window (bars)", 20, J.obj(("min", 2), ("max", 100)))
    myHistoryWindow = J.get(G_input, "number")("History Window (bars)", 252, J.obj(("min", 50), ("max", 1000)))
    myDollarVolume = G_mult(G_close, G_volume)
    myDollarVolumeAvg = G_sma(myDollarVolume, myFormationWindow)
    def _f1(_avgVol=J.undefined, *_args):
        return J.get(G_Math, "log")(J.get(G_Math, "max")(_avgVol, 1.0e-10))
    myVScale = J.get(myDollarVolumeAvg, "map")(_f1)
    def _f2(_window=J.undefined, *_args):
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        sorted = J.get(J.JSArray([*J.spread(_window)]), "sort")(_f1)
        pos = J.mul(J.sub(J.get(sorted, "length"), 1), 0.2)
        base = J.get(G_Math, "floor")(pos)
        rest = J.sub(pos, base)
        if (J.get(sorted, J.add(base, 1)) is not J.undefined):
            return J.add(J.get(sorted, base), J.mul(rest, J.sub(J.get(sorted, J.add(base, 1)), J.get(sorted, base))))
        return J.get(sorted, base)
    myP20 = G_sliding_window_function(myVScale, myHistoryWindow, _f2)
    def _f3(_window=J.undefined, *_args):
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        sorted = J.get(J.JSArray([*J.spread(_window)]), "sort")(_f1)
        pos = J.mul(J.sub(J.get(sorted, "length"), 1), 0.4)
        base = J.get(G_Math, "floor")(pos)
        rest = J.sub(pos, base)
        if (J.get(sorted, J.add(base, 1)) is not J.undefined):
            return J.add(J.get(sorted, base), J.mul(rest, J.sub(J.get(sorted, J.add(base, 1)), J.get(sorted, base))))
        return J.get(sorted, base)
    myP40 = G_sliding_window_function(myVScale, myHistoryWindow, _f3)
    def _f4(_window=J.undefined, *_args):
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        sorted = J.get(J.JSArray([*J.spread(_window)]), "sort")(_f1)
        pos = J.mul(J.sub(J.get(sorted, "length"), 1), 0.6)
        base = J.get(G_Math, "floor")(pos)
        rest = J.sub(pos, base)
        if (J.get(sorted, J.add(base, 1)) is not J.undefined):
            return J.add(J.get(sorted, base), J.mul(rest, J.sub(J.get(sorted, J.add(base, 1)), J.get(sorted, base))))
        return J.get(sorted, base)
    myP60 = G_sliding_window_function(myVScale, myHistoryWindow, _f4)
    def _f5(_window=J.undefined, *_args):
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        sorted = J.get(J.JSArray([*J.spread(_window)]), "sort")(_f1)
        pos = J.mul(J.sub(J.get(sorted, "length"), 1), 0.8)
        base = J.get(G_Math, "floor")(pos)
        rest = J.sub(pos, base)
        if (J.get(sorted, J.add(base, 1)) is not J.undefined):
            return J.add(J.get(sorted, base), J.mul(rest, J.sub(J.get(sorted, J.add(base, 1)), J.get(sorted, base))))
        return J.get(sorted, base)
    myP80 = G_sliding_window_function(myVScale, myHistoryWindow, _f5)
    myVMin = G_lowest(myVScale, myHistoryWindow)
    myVMax = G_highest(myVScale, myHistoryWindow)
    def _f6(_vscale=J.undefined, _vmin=J.undefined, _vmax=J.undefined, *_args):
        if J.seq(_vmax, _vmin):
            return 0.5
        return J.get(G_Math, "max")(0, J.get(G_Math, "min")(1, J.div(J.sub(_vscale, _vmin), J.sub(_vmax, _vmin))))
    myRank01 = G_for_every(myVScale, myVMin, myVMax, _f6)
    def _f7(_val=J.undefined, *_args):
        r1 = 173
        g1 = 216
        b1 = 230
        r2 = 255
        g2 = 69
        b2 = 0
        r = J.get(G_Math, "round")(J.add(r1, J.mul(J.sub(r2, r1), _val)))
        g = J.get(G_Math, "round")(J.add(g1, J.mul(J.sub(g2, g1), _val)))
        b = J.get(G_Math, "round")(J.add(b1, J.mul(J.sub(b2, b1), _val)))
        return J.template("rgb(", r, ", ", g, ", ", b, ")")
    myGradientColor = J.get(myRank01, "map")(_f7)
    def myBlueGradient(_val=J.undefined, *_args):
        r1 = 173
        g1 = 216
        b1 = 230
        r2 = 0
        g2 = 0
        b2 = 255
        r = J.get(G_Math, "round")(J.add(r1, J.mul(J.sub(r2, r1), _val)))
        g = J.get(G_Math, "round")(J.add(g1, J.mul(J.sub(g2, g1), _val)))
        b = J.get(G_Math, "round")(J.add(b1, J.mul(J.sub(b2, b1), _val)))
        return J.template("rgb(", r, ", ", g, ", ", b, ")")
    G_paint(myVScale, J.obj(("name", "Trading Activity"), ("style", "line"), ("color", myGradientColor)))
    G_paint(myP20, J.obj(("name", "P20"), ("style", "line"), ("color", myBlueGradient(0.2))))
    G_paint(myP40, J.obj(("name", "P40"), ("style", "line"), ("color", myBlueGradient(0.4))))
    G_paint(myP60, J.obj(("name", "P60"), ("style", "line"), ("color", myBlueGradient(0.6))))
    G_paint(myP80, J.obj(("name", "P80"), ("style", "line"), ("color", myBlueGradient(0.8))))


register_store_indicator(
    script,
    name='trading_activity_index_zeiierman_TS',
    title='Trading Activity Index (Zeiierman)',
    developer='Zeiierman Trading',
    url='https://trendspider.com/trading-tools-store/indicators/68e78d-trading-activity-index-zeiierman/',
    position='lower',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 1500}, {'id': 'formation_window__bars_', 'title': 'Formation Window (bars)', 'type': 'number', 'default': 20}, {'id': 'history_window__bars_', 'title': 'History Window (bars)', 'type': 'number', 'default': 252}],
    outputs=['trading_activity', 'p20', 'p40', 'p60', 'p80'],
    signals=[],
    requires=[],
    parity='exact',
)
