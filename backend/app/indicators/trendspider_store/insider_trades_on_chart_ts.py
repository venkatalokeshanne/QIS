"""
Insider Trades On Chart -- TrendSpider store indicator by TrendSpider Team.

Registered as "insider_trades_on_chart_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/insider-trading-indicator/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_time = G["time"]
    def plotInsiderActions(ticker=J.undefined, *_args):
        trades = J.get(G_request, "insider_trading")(ticker)
        def _f1(item=J.undefined, *_args):
            return J.eq(J.get(item, "transaction"), "buy")
        buys = J.get(J.get(trades, "transactions"), "filter")(_f1)
        def _f2(item=J.undefined, *_args):
            return J.eq(J.get(item, "transaction"), "sell")
        sells = J.get(J.get(trades, "transactions"), "filter")(_f2)
        def _f3(item=J.undefined, *_args):
            return (_t1 if J.truthy(_t1 := J.eq(J.get(item, "transaction"), "gift")) else J.eq(J.get(item, "transaction"), "award"))
        gifts = J.get(J.get(trades, "transactions"), "filter")(_f3)
        def _f4(item=J.undefined, *_args):
            return J.get(item, "timestamp")
        def _f5(*_args):
            return ("buy" if J.eq(ticker, J.get(G_constants, "ticker")) else J.template(ticker, " buy"))
        buysLanded = G_land_points_onto_series(J.get(buys, "map")(_f4), J.get(buys, "map")(_f5), G_time, "ge")
        def _f6(item=J.undefined, *_args):
            return J.get(item, "timestamp")
        def _f7(*_args):
            return ("sell" if J.eq(ticker, J.get(G_constants, "ticker")) else J.template(ticker, " sell"))
        sellsLanded = G_land_points_onto_series(J.get(sells, "map")(_f6), J.get(sells, "map")(_f7), G_time, "ge")
        def _f8(item=J.undefined, *_args):
            return J.get(item, "timestamp")
        def _f9(*_args):
            return ("gift" if J.eq(ticker, J.get(G_constants, "ticker")) else J.template(ticker, " gift"))
        giftsLanded = G_land_points_onto_series(J.get(gifts, "map")(_f8), J.get(gifts, "map")(_f9), G_time, "ge")
        G_paint(sellsLanded, J.obj(("style", "labels_above"), ("color", "red"), ("backgroundBorderRadius", 4), ("backgroundColor", "red")))
        G_paint(buysLanded, J.obj(("style", "labels_below"), ("color", "green"), ("backgroundBorderRadius", 4), ("backgroundColor", "green")))
        G_paint(giftsLanded, J.obj(("style", "labels_below"), ("color", "blue"), ("backgroundBorderRadius", 4), ("backgroundColor", "blue")))
        def _f10(label=J.undefined, *_args):
            return (label is not None)
        buySignals = J.get(buysLanded, "map")(_f10)
        def _f11(label=J.undefined, *_args):
            return (label is not None)
        sellSignals = J.get(sellsLanded, "map")(_f11)
        def _f12(label=J.undefined, *_args):
            return (label is not None)
        giftSignals = J.get(giftsLanded, "map")(_f12)
        G_register_signal(buySignals, "Buy Signal")
        G_register_signal(sellSignals, "Sell Signal")
        G_register_signal(giftSignals, "Gift Signal")
    G_describe_indicator("Insider Trades On Chart")
    plotInsiderActions(J.get(G_constants, "ticker"))


register_store_indicator(
    script,
    name='insider_trades_on_chart_TS',
    title='Insider Trades On Chart',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/insider-trading-indicator/',
    position='price',
    inputs=[],
    outputs=['line_1', 'line_2', 'line_3', 'buy_signal', 'sell_signal', 'gift_signal'],
    signals=['buy_signal', 'sell_signal', 'gift_signal'],
    requires=['insider_trading'],
    parity='exact',
)
