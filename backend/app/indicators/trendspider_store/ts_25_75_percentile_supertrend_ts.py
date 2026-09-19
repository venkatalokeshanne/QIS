"""
25-75 Percentile SuperTrend -- TrendSpider store indicator by Alpha Scope.

Registered as "25_75_percentile_supertrend_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/699f45-25-75-percentile-supertrend/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_add = G["add"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_market = G["market"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_sliding_window_function = G["sliding_window_function"]
    G_sub = G["sub"]
    G_describe_indicator("25-75 Percentile SuperTrend")
    subject = J.get(G_input, "number")("Supertrend length", 14, J.obj(("min", 2)))
    myMult = J.get(G_input, "number")("Multiplier", 1, J.obj(("min", 0), ("max", 10)))
    slen = J.get(G_input, "number")("Percentile length", 27, J.obj(("min", 1), ("max", 300)))
    priceSourceOptions = J.JSArray(["high", "low", "close", "open", "hl2", "hlc3", "ohlc4"])
    src_2575_input = J.get(G_input, "select")("Median smoothing source", "high", priceSourceOptions)
    src_2575 = J.get(G_market, src_2575_input)
    def percentile_nearest_rank(series=J.undefined, length=J.undefined, percentile=J.undefined, *_args):
        def _f1(window=J.undefined, *_args):
            def _f1(a=J.undefined, b=J.undefined, *_args):
                return J.sub(a, b)
            sorted = J.get(J.JSArray([*J.spread(window)]), "sort")(_f1)
            index = J.sub(J.get(G_Math, "ceil")(J.mul(J.div(percentile, 100), J.get(sorted, "length"))), 1)
            return J.get(sorted, J.get(G_Math, "max")(0, index))
        return G_sliding_window_function(series, length, _f1)
    smooth_lower = percentile_nearest_rank(src_2575, slen, 25)
    smooth_upper = percentile_nearest_rank(src_2575, slen, 75)
    myAtr = G_atr(G_high, G_low, G_close, subject)
    src_long = smooth_upper
    src_short = smooth_lower
    upper_initial = G_add(src_long, G_mult(myAtr, myMult))
    lower_initial = G_sub(src_short, G_mult(myAtr, myMult))
    def _f1(u=J.undefined, l=J.undefined, c=J.undefined, prev=J.undefined, idx=J.undefined, *_args):
        if (J.seq(idx, 0) or (not J.truthy(prev))):
            return J.obj(("upper", u), ("lower", l), ("dist", 1), ("st", u))
        pl = J.get(prev, "lower")
        pu = J.get(prev, "upper")
        new_lower = (l if (J.gt(l, pl) or J.lt(J.get(G_close, J.sub(idx, 1)), pl)) else pl)
        new_upper = (u if (J.lt(u, pu) or J.gt(J.get(G_close, J.sub(idx, 1)), pu)) else pu)
        dist_2 = J.undefined
        if J.seq(J.get(prev, "st"), pu):
            dist_2 = ((-1) if J.gt(c, new_upper) else 1)
        else:
            dist_2 = (1 if J.lt(c, new_lower) else (-1))
        st = (new_lower if J.seq(dist_2, (-1)) else new_upper)
        return J.obj(("upper", new_upper), ("lower", new_lower), ("dist", dist_2), ("st", st))
    supertrend_result = G_for_every(upper_initial, lower_initial, G_close, _f1)
    def _f2(r=J.undefined, *_args):
        return (J.get(r, "st") if J.truthy(r) else None)
    x = J.get(supertrend_result, "map")(_f2)
    def _f3(r=J.undefined, *_args):
        return (J.get(r, "dist") if J.truthy(r) else None)
    dist = J.get(supertrend_result, "map")(_f3)
    def _f4(d=J.undefined, prev_d=J.undefined, *_args):
        return (True if (J.ge(prev_d, 0) and J.lt(d, 0)) else False)
    ST_L = G_for_every(dist, _f4)
    def _f5(d=J.undefined, prev_d=J.undefined, *_args):
        return (True if (J.le(prev_d, 0) and J.gt(d, 0)) else False)
    ST_S = G_for_every(dist, _f5)
    def _f6(long=J.undefined, short=J.undefined, prev_state=J.undefined, *_args):
        if (J.truthy(long) and (not J.truthy(short))):
            return 1
        if J.truthy(short):
            return (-1)
        return (_t1 if J.truthy(_t1 := prev_state) else 0)
    Mattes = G_for_every(ST_L, ST_S, _f6)
    def _f7(m=J.undefined, *_args):
        return ("#2da2fc" if J.seq(m, 1) else ("#713bf9" if J.seq(m, (-1)) else "gray"))
    syscol = J.get(Mattes, "map")(_f7)
    BlueTransparent = "rgba(45, 162, 252, 0.5)"
    PurpleTransparent = "rgba(113, 59, 249, 0.5)"
    G_color_candles(syscol)
    def _f8(d=J.undefined, i=J.undefined, *_args):
        return (J.get(x, i) if J.lt(d, 0) else None)
    upTrendSeries = J.get(dist, "map")(_f8)
    def _f9(d=J.undefined, i=J.undefined, *_args):
        return (J.get(x, i) if J.ge(d, 0) else None)
    downTrendSeries = J.get(dist, "map")(_f9)
    upTrendLine = G_paint(upTrendSeries, J.obj(("name", "Up Trend"), ("color", "#2da2fc"), ("style", "line")))
    downTrendLine = G_paint(downTrendSeries, J.obj(("name", "Down Trend"), ("color", "#713bf9"), ("style", "line")))
    middleLine = G_div(G_add(smooth_lower, smooth_upper), 2)
    middleLinePainted = G_paint(middleLine, J.obj(("color", syscol), ("name", "Middle"), ("hidden", True)))
    G_fill(middleLinePainted, upTrendLine, BlueTransparent)
    G_fill(middleLinePainted, downTrendLine, PurpleTransparent)


register_store_indicator(
    script,
    name='25_75_percentile_supertrend_TS',
    title='25-75 Percentile SuperTrend',
    developer='Alpha Scope',
    url='https://trendspider.com/trading-tools-store/indicators/699f45-25-75-percentile-supertrend/',
    position='price',
    inputs=[{'id': 'supertrend_length', 'title': 'Supertrend length', 'type': 'number', 'default': 14}, {'id': 'multiplier', 'title': 'Multiplier', 'type': 'number', 'default': 1}, {'id': 'percentile_length', 'title': 'Percentile length', 'type': 'number', 'default': 27}, {'id': 'median_smoothing_source', 'title': 'Median smoothing source', 'type': 'select_wide', 'default': 'high', 'options': ['high', 'low', 'close', 'open', 'hl2', 'hlc3', 'ohlc4']}],
    outputs=['cdl', 'up_trend', 'down_trend', 'middle'],
    signals=[],
    requires=[],
    parity='exact',
)
