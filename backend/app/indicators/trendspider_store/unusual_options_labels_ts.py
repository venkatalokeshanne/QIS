"""
Unusual Options Labels -- TrendSpider store indicator by James Chambers.

Registered as "unusual_options_labels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/unusual-options-labels/)
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
    G_console = G["console"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_time = G["time"]
    def fetchUnusualOptionsData(*_args):
        try:
            optionsData = J.get(G_request, "unusual_options")(J.get(G_constants, "ticker"))
            if ((not J.truthy(optionsData)) or J.seq(J.get(optionsData, "length"), 0)):
                return J.obj(("bullishSignals", J.get(G_Array(J.get(G_close, "length")), "fill")(None)), ("bearishSignals", J.get(G_Array(J.get(G_close, "length")), "fill")(None)), ("neutralSignals", J.get(G_Array(J.get(G_close, "length")), "fill")(None)))
            def _f1(trade=J.undefined, *_args):
                return (J.gt(J.get(trade, "costBasis"), minimumCostBasis) if J.truthy(_t1 := J.get(J.get(trade, "tags"), "includes")("bullish")) else _t1)
            bullishTrades = J.get(optionsData, "filter")(_f1)
            def _f2(trade=J.undefined, *_args):
                return (J.gt(J.get(trade, "costBasis"), minimumCostBasis) if J.truthy(_t1 := J.get(J.get(trade, "tags"), "includes")("bearish")) else _t1)
            bearishTrades = J.get(optionsData, "filter")(_f2)
            def _f3(trade=J.undefined, *_args):
                return (J.gt(J.get(trade, "costBasis"), minimumCostBasis) if J.truthy(_t1 := J.get(J.get(trade, "tags"), "includes")("neutral")) else _t1)
            neutralTrades = J.get(optionsData, "filter")(_f3)
            def _f4(item=J.undefined, *_args):
                return J.get(item, "timestamp")
            def _f5(*_args):
                return "Bullish"
            bullishSignals_2 = G_land_points_onto_series(J.get(bullishTrades, "map")(_f4), J.get(bullishTrades, "map")(_f5), G_time, "ge")
            def _f6(item=J.undefined, *_args):
                return J.get(item, "timestamp")
            def _f7(*_args):
                return "Bearish"
            bearishSignals_2 = G_land_points_onto_series(J.get(bearishTrades, "map")(_f6), J.get(bearishTrades, "map")(_f7), G_time, "ge")
            def _f8(item=J.undefined, *_args):
                return J.get(item, "timestamp")
            def _f9(*_args):
                return "Neutral"
            neutralSignals_2 = G_land_points_onto_series(J.get(neutralTrades, "map")(_f8), J.get(neutralTrades, "map")(_f9), G_time, "ge")
            return J.obj(("bullishSignals", bullishSignals_2), ("bearishSignals", bearishSignals_2), ("neutralSignals", neutralSignals_2))
        except Exception as _e10:
            error = J.catch_value(_e10)
            J.get(G_console, "error")("Error fetching or processing data:", error)
            return J.obj(("bullishSignals", J.get(G_Array(J.get(G_close, "length")), "fill")(None)), ("bearishSignals", J.get(G_Array(J.get(G_close, "length")), "fill")(None)), ("neutralSignals", J.get(G_Array(J.get(G_close, "length")), "fill")(None)))
    G_describe_indicator("Unusual Options Labels", "price")
    minimumCostBasis = J.get(G_input, "number")("Minimum Cost Basis", 100000)
    _t1 = J.require_object(fetchUnusualOptionsData())
    bullishSignals = J.get(_t1, "bullishSignals")
    bearishSignals = J.get(_t1, "bearishSignals")
    neutralSignals = J.get(_t1, "neutralSignals")
    G_paint(bullishSignals, J.obj(("style", "labels_above"), ("color", "green"), ("backgroundColor", "green"), ("backgroundBorderRadius", 3), ("name", "Bullish Signal")))
    G_paint(bearishSignals, J.obj(("style", "labels_below"), ("color", "red"), ("backgroundColor", "red"), ("backgroundBorderRadius", 3), ("name", "Bearish Signal")))
    G_paint(neutralSignals, J.obj(("style", "labels_above"), ("color", "gray"), ("backgroundColor", "gray"), ("backgroundBorderRadius", 3), ("name", "Neutral Signal")))
    def _f2(signal=J.undefined, *_args):
        return J.seq(signal, "Bullish")
    buySignal = J.get(bullishSignals, "map")(_f2)
    def _f3(signal=J.undefined, *_args):
        return J.seq(signal, "Bearish")
    sellSignal = J.get(bearishSignals, "map")(_f3)
    def _f4(signal=J.undefined, *_args):
        return J.seq(signal, "Neutral")
    neutralSignal = J.get(neutralSignals, "map")(_f4)
    G_register_signal(buySignal, "Bullish Unusual Options")
    G_register_signal(sellSignal, "Bearish Unusual Options")
    G_register_signal(neutralSignal, "Neutral Unusual Options")


register_store_indicator(
    script,
    name='unusual_options_labels_TS',
    title='Unusual Options Labels',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/unusual-options-labels/',
    position='price',
    inputs=[{'id': 'minimum_cost_basis', 'title': 'Minimum Cost Basis', 'type': 'number', 'default': 100000}],
    outputs=['bullish_signal', 'bearish_signal', 'neutral_signal', 'bullish_unusual_options', 'bearish_unusual_options', 'neutral_unusual_options'],
    signals=['bullish_unusual_options', 'bearish_unusual_options', 'neutral_unusual_options'],
    requires=['unusual_options'],
    parity='exact',
)
