"""
KDJ J-Cross -- TrendSpider store indicator by Rock Regan.

Registered as "kdj_j_cross_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68c361-kdj-j-cross/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_register_signal = G["register_signal"]
    G_wildma = G["wildma"]
    G_describe_indicator("KDJ J-Cross", "price", J.obj(("shortName", "KDJ J-Cross")))
    len = J.get(G_input, "number")("KDJ Length", 9, J.obj(("min", 1), ("max", 300), ("step", 1)))
    smooth = J.get(G_input, "number")("Signal Smoothing (Wilder)", 3, J.obj(("min", 1), ("max", 100), ("step", 1)))
    thresh = J.get(G_input, "number")("J Midline Threshold", 50, J.obj(("min", (-200)), ("max", 200), ("step", 1)))
    colTrendUp = J.get(G_input, "color")("Trend Up (J>mid, no cross)", "#3399ff")
    colTrendDown = J.get(G_input, "color")("Trend Down (J<mid, no cross)", "#66ccff")
    colXUp = J.get(G_input, "color")("Crossover Up (prev<=mid→>mid)", "#00ff66")
    colXDown = J.get(G_input, "color")("Crossover Down (prev>=mid→<mid)", "#ffcc00")
    hi = G_highest(G_high, len)
    lo = G_lowest(G_low, len)
    kRaw = J.JSArray([])
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        range = J.sub(J.get(hi, i), J.get(lo, i))
        kVal = ((J.get(kRaw, J.sub(i, 1)) if J.gt(i, 0) else 50) if J.seq(range, 0) else J.div(J.mul(J.sub(J.get(G_close, i), J.get(lo, i)), 100), range))
        J.get(kRaw, "push")(kVal)
        i = J.inc(i)
    K = G_wildma(kRaw, smooth)
    D = G_wildma(K, smooth)
    J_ = J.JSArray([])
    i_2 = 0
    while J.lt(i_2, J.get(G_close, "length")):
        J.get(J_, "push")(J.sub(J.mul(3, J.get(K, i_2)), J.mul(2, J.get(D, i_2))))
        i_2 = J.inc(i_2)
    colors = J.JSArray([])
    crossOver = J.get(G_Array(J.get(G_close, "length")), "fill")(0)
    crossUnder = J.get(G_Array(J.get(G_close, "length")), "fill")(0)
    i_3 = 0
    while J.lt(i_3, J.get(G_close, "length")):
        j = J.get(J_, i_3)
        pj = (J.get(J_, J.sub(i_3, 1)) if J.gt(i_3, 0) else j)
        justCrossUp = (J.gt(j, thresh) if J.truthy(_t1 := J.le(pj, thresh)) else _t1)
        justCrossDown = (J.lt(j, thresh) if J.truthy(_t2 := J.ge(pj, thresh)) else _t2)
        if J.truthy(justCrossUp):
            J.get(colors, "push")(colXUp)
            J.set(crossOver, i_3, 1)
        elif J.truthy(justCrossDown):
            J.get(colors, "push")(colXDown)
            J.set(crossUnder, i_3, 1)
        else:
            J.get(colors, "push")((colTrendUp if J.gt(j, thresh) else colTrendDown))
        i_3 = J.inc(i_3)
    G_color_candles(colors)
    G_register_signal(crossOver, J.template("Bullish Signal: J crossed above ", thresh, "."))
    G_register_signal(crossUnder, J.template("Bearish Signal: J crossed below ", thresh, "."))


register_store_indicator(
    script,
    name='kdj_j_cross_TS',
    title='KDJ J-Cross',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/68c361-kdj-j-cross/',
    position='price',
    inputs=[{'id': 'kdj_length', 'title': 'KDJ Length', 'type': 'number', 'default': 9}, {'id': 'signal_smoothing__wilder_', 'title': 'Signal Smoothing (Wilder)', 'type': 'number', 'default': 3}, {'id': 'j_midline_threshold', 'title': 'J Midline Threshold', 'type': 'number', 'default': 50}, {'id': 'trend_up__j_mid__no_cross_', 'title': 'Trend Up (J>mid, no cross)', 'type': 'color', 'default': '#3399ff'}, {'id': 'trend_down__j_mid__no_cross_', 'title': 'Trend Down (J<mid, no cross)', 'type': 'color', 'default': '#66ccff'}, {'id': 'crossover_up__prev__mid__mid_', 'title': 'Crossover Up (prev<=mid→>mid)', 'type': 'color', 'default': '#00ff66'}, {'id': 'crossover_down__prev__mid__mid_', 'title': 'Crossover Down (prev>=mid→<mid)', 'type': 'color', 'default': '#ffcc00'}],
    outputs=['cdl', 'bullish_signal__j_crossed_above_50_', 'bearish_signal__j_crossed_below_50_'],
    signals=['bullish_signal__j_crossed_above_50_', 'bearish_signal__j_crossed_below_50_'],
    requires=[],
    parity='exact',
)
