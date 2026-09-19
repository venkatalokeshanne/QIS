"""
Robust Scaled Dema | Alpha Scope -- TrendSpider store indicator by Alpha Scope.

Registered as "robust_scaled_dema_alpha_scope_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69c70c-robust-scaled-dema-alpha-scope/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_for_every = G["for_every"]
    G_horizontal_line = G["horizontal_line"]
    G_input = G["input"]
    G_market = G["market"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_sliding_window_function = G["sliding_window_function"]
    G_sub = G["sub"]
    def percentile_linear(values=J.undefined, p=J.undefined, *_args):
        def _f1(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        sorted = J.get(J.JSArray([*J.spread(values)]), "sort")(_f1)
        n = J.get(sorted, "length")
        if J.seq(n, 0):
            return None
        if J.seq(n, 1):
            return J.get(sorted, 0)
        position = J.mul(J.sub(n, 1), J.div(p, 100))
        lower = J.get(G_Math, "floor")(position)
        upper = J.get(G_Math, "ceil")(position)
        weight = J.sub(position, lower)
        return J.add(J.mul(J.get(sorted, lower), J.sub(1, weight)), J.mul(J.get(sorted, upper), weight))
    G_describe_indicator("Robust Scaled Dema | Alpha Scope", "lower")
    src = J.get(G_market, J.get(G_input, "select")("Source", "close", J.get(G_constants, "price_source_options")))
    demalen = J.get(G_input, "number")("Dema Length", 25, J.obj(("min", 1), ("max", 500)))
    rslen = J.get(G_input, "number")("Robust Scaling Length", 40, J.obj(("min", 1), ("max", 500)))
    upperthreshold = J.get(G_input, "number")("Upper Threshold", 0.5, J.obj(("min", (-10)), ("max", 10)))
    lowerthreshold = J.get(G_input, "number")("Lower Threshold", 0, J.obj(("min", (-10)), ("max", 10)))
    ema1 = G_ema(src, demalen)
    ema2 = G_ema(ema1, demalen)
    dema = G_sub(G_mult(ema1, 2), ema2)
    def _f1(_window=J.undefined, *_args):
        q1 = percentile_linear(_window, 25)
        q3 = percentile_linear(_window, 75)
        median = percentile_linear(_window, 50)
        iqr = J.sub(q3, q1)
        if (J.seq(iqr, 0) or (iqr is None)):
            return None
        currentDema = J.get(_window, J.sub(J.get(_window, "length"), 1))
        return J.div(J.sub(currentDema, median), iqr)
    robustscaling = G_sliding_window_function(dema, rslen, _f1)
    def _f2(_rs=J.undefined, _prevAs=J.undefined, *_args):
        if (_rs is None):
            return (_t1 if J.truthy(_t1 := _prevAs) else 0)
        longCondition = J.gt(_rs, upperthreshold)
        shortCondition = J.lt(_rs, lowerthreshold)
        if (J.truthy(longCondition) and (not J.truthy(shortCondition))):
            return 1
        elif J.truthy(shortCondition):
            return (-1)
        else:
            return (_t2 if J.truthy(_t2 := _prevAs) else 0)
    as_ = G_for_every(robustscaling, _f2)
    COLOR_GREEN = "rgb(31, 211, 37)"
    COLOR_PURPLE = "rgb(188, 8, 219)"
    COLOR_NEUTRAL = "gray"
    def _f3(_as=J.undefined, *_args):
        if J.seq(_as, 1):
            return COLOR_GREEN
        if J.seq(_as, (-1)):
            return COLOR_PURPLE
        return COLOR_NEUTRAL
    lineColor = G_for_every(as_, _f3)
    G_paint(robustscaling, J.obj(("name", "Robust Scaled Dema"), ("color", lineColor), ("thickness", 2)))
    G_paint(G_horizontal_line(upperthreshold), J.obj(("name", "Upper Threshold"), ("color", COLOR_GREEN), ("style", "dotted")))
    G_paint(G_horizontal_line(lowerthreshold), J.obj(("name", "Lower Threshold"), ("color", COLOR_PURPLE), ("style", "dotted")))


register_store_indicator(
    script,
    name='robust_scaled_dema_alpha_scope_TS',
    title='Robust Scaled Dema | Alpha Scope',
    developer='Alpha Scope',
    url='https://trendspider.com/trading-tools-store/indicators/69c70c-robust-scaled-dema-alpha-scope/',
    position='lower',
    inputs=[{'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'dema_length', 'title': 'Dema Length', 'type': 'number', 'default': 25}, {'id': 'robust_scaling_length', 'title': 'Robust Scaling Length', 'type': 'number', 'default': 40}, {'id': 'upper_threshold', 'title': 'Upper Threshold', 'type': 'number', 'default': 0.5}, {'id': 'lower_threshold', 'title': 'Lower Threshold', 'type': 'number', 'default': 0}],
    outputs=['robust_scaled_dema', 'upper_threshold', 'lower_threshold'],
    signals=[],
    requires=[],
    parity='exact',
)
