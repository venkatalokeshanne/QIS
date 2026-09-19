"""
Momentum Metrics Table -- TrendSpider store indicator by TrendSpider Team.

Registered as "momentum_metrics_table_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/momentum-metrics-table/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_cci = G["cci"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_high = G["high"]
    G_hlc3 = G["hlc3"]
    G_low = G["low"]
    G_mfi = G["mfi"]
    G_paint_overlay = G["paint_overlay"]
    G_rsi = G["rsi"]
    G_stochastic = G["stochastic"]
    G_sub = G["sub"]
    G_volume = G["volume"]
    G_describe_indicator("Momentum Metrics Table")
    def _f1(data=J.undefined, *_args):
        return G_rsi(data, 14)
    def _f2(data=J.undefined, *_args):
        macd = G_sub(G_ema(data, 12), G_ema(data, 26))
        signal = G_ema(macd, 9)
        return G_sub(macd, signal)
    def _f3(*_args):
        return G_stochastic(G_close, G_high, G_low, 14)
    def _f4(*_args):
        return G_cci(G_hlc3, 20)
    def _f5(*_args):
        return G_mfi(G_hlc3, G_volume, 14)
    metrics = J.JSArray([J.obj(("name", "RSI"), ("func", _f1)), J.obj(("name", "MACD"), ("func", _f2)), J.obj(("name", "Stochastic"), ("func", _f3)), J.obj(("name", "CCI"), ("func", _f4)), J.obj(("name", "MFI"), ("func", _f5))])
    def _f6(metric=J.undefined, *_args):
        return J.obj(("name", J.get(metric, "name")), ("value", (J.get(J.get(metric, "func")(), J.sub(J.get(J.get(metric, "func")(), "length"), 1)) if ((J.seq(J.get(metric, "name"), "Stochastic") or J.seq(J.get(metric, "name"), "CCI")) or J.seq(J.get(metric, "name"), "MFI")) else J.get(J.get(metric, "func")(G_close), J.sub(J.get(J.get(metric, "func")(G_close), "length"), 1)))))
    results = J.get(metrics, "map")(_f6)
    thresholds = J.obj(("RSI", J.obj(("bullish", 50), ("bearish", 50))), ("MACD", J.obj(("bullish", 0), ("bearish", 0))), ("Stochastic", J.obj(("bullish", 50), ("bearish", 50))), ("CCI", J.obj(("bullish", 0), ("bearish", 0))), ("MFI", J.obj(("bullish", 50), ("bearish", 50))))
    def _f7(result=J.undefined, index=J.undefined, *_args):
        return J.JSArray([J.obj(("text", ""), ("padding", "10px 25px"), ("backgroundColor", "transparent"), ("borderRight", "none")), J.obj(("text", J.get(result, "name")), ("padding", "10px 15px"), ("color", "var(--text-color)"), ("backgroundColor", ("rgba(255, 255, 255, 0.05)" if J.seq(J.mod(index, 2), 0) else "transparent")), ("borderRight", "1px solid rgba(255, 255, 255, 0.1)")), J.obj(("text", J.get(J.get(result, "value"), "toFixed")(2)), ("color", ("green" if J.gt(J.get(result, "value"), J.get(J.get(thresholds, J.get(result, "name")), "bullish")) else ("red" if J.lt(J.get(result, "value"), J.get(J.get(thresholds, J.get(result, "name")), "bearish")) else "var(--text-color)"))), ("padding", "10px 15px"), ("backgroundColor", ("rgba(255, 255, 255, 0.05)" if J.seq(J.mod(index, 2), 0) else "transparent")), ("borderRight", "1px solid rgba(255, 255, 255, 0.1)"), ("textAlign", "right")), J.obj(("text", ""), ("padding", "10px 25px"), ("backgroundColor", "transparent"), ("borderRight", "none"))])
    tableCells = J.get(results, "map")(_f7)
    def _f8(cell=J.undefined, *_args):
        return J.obj(("cells", cell))
    G_paint_overlay("Momentum Metrics", J.obj(("position", "bottom_right")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", ""), ("padding", "12px 25px"), ("backgroundColor", "transparent")), J.obj(("text", "Metric"), ("color", "var(--text-color)"), ("padding", "12px 18px"), ("fontWeight", "bold"), ("borderBottom", "2px solid var(--text-color)"), ("backgroundColor", "rgba(255, 255, 255, 0.1)")), J.obj(("text", "Value"), ("color", "var(--text-color)"), ("padding", "12px 18px"), ("fontWeight", "bold"), ("borderBottom", "2px solid var(--text-color)"), ("backgroundColor", "rgba(255, 255, 255, 0.1)"), ("textAlign", "right")), J.obj(("text", ""), ("padding", "12px 25px"), ("backgroundColor", "transparent"))]))), *J.spread(J.get(tableCells, "map")(_f8)), J.obj(("cells", J.JSArray([J.obj(("text", ""), ("padding", "12px 0"), ("borderRight", "none")), J.obj(("text", ""), ("padding", "12px 0"), ("borderRight", "none")), J.obj(("text", ""), ("padding", "12px 25px"), ("backgroundColor", "transparent")), J.obj(("text", ""), ("padding", "12px 25px"), ("backgroundColor", "transparent"))])))])), ("style", J.obj(("border", "2px solid var(--text-color)"), ("borderRadius", "6px"), ("margin", "50px 80px 50px 50px"), ("overflow", "hidden"), ("display", "inline-block")))))


register_store_indicator(
    script,
    name='momentum_metrics_table_TS',
    title='Momentum Metrics Table',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/momentum-metrics-table/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=[],
    parity='exact',
)
