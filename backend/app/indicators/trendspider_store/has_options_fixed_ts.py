"""
Has Options - Fixed -- TrendSpider store indicator by Rock Regan.

Registered as "has_options_fixed_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a12b-has-options/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_String = G["String"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_paint_overlay = G["paint_overlay"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_describe_indicator("Has Options - Fixed")
    hasOptions = False
    optionsCount = 0
    errorMessage = ""
    try:
        optionsData = J.get(G_request, "unusual_options")(J.get(G_current, "ticker"))
        if ((J.truthy(optionsData) and J.truthy(J.get(G_Array, "isArray")(optionsData))) and J.gt(J.get(optionsData, "length"), 0)):
            def _f1(option=J.undefined, *_args):
                return ((_t4 if J.truthy(_t4 := J.seq(J.get(option, "type"), "CALL")) else J.seq(J.get(option, "type"), "PUT")) if J.truthy(_t1 := (J.get(option, "type") if J.truthy(_t2 := (J.get(option, "size") if J.truthy(_t3 := J.get(option, "strike")) else _t3)) else _t2)) else _t1)
            validOptions = J.get(optionsData, "filter")(_f1)
            hasOptions = J.gt(J.get(validOptions, "length"), 0)
            optionsCount = J.get(validOptions, "length")
        else:
            hasOptions = False
            optionsCount = 0
    except Exception as _e2:
        error = J.catch_value(_e2)
        hasOptions = False
        errorMessage = G_String(error)
    G_paint_overlay("HasOptions", J.obj(("position", "bottom_right"), ("offset_x", (-50)), ("offset_y", 0), ("order", "above_all")), J.obj(("background", "var(--background-color)"), ("border", ("1px solid #00FF00" if J.truthy(hasOptions) else "1px solid #FF0000")), ("borderRadius", "4px"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", (J.template(J.get(G_current, "ticker"), " Options: Error checking") if J.truthy(errorMessage) else J.template(J.get(G_current, "ticker"), " Options: ", (J.template("Yes\ud83d\udfe2 (", optionsCount, ")") if J.truthy(hasOptions) else "No\ud83d\udd34")))), ("color", ("yellow" if J.truthy(errorMessage) else ("lightgreen" if J.truthy(hasOptions) else "pink"))), ("fontWeight", "bold"), ("padding", "8px"))])))]))))
    G_register_signal(G_series_of((not (not J.truthy(errorMessage)))), "Has Options Error")
    G_register_signal(G_series_of((False if J.truthy(errorMessage) else hasOptions)), "Has Options")


register_store_indicator(
    script,
    name='has_options_fixed_TS',
    title='Has Options - Fixed',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/68a12b-has-options/',
    position='price',
    inputs=[],
    outputs=['has_options_error', 'has_options'],
    signals=['has_options_error', 'has_options'],
    requires=['unusual_options'],
    parity='exact',
)
