"""
Congress Trades On Chart -- TrendSpider store indicator by TrendSpider Team.

Registered as "congress_trades_on_chart_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/us-house-and-senate-trades-on-chart/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Congress Trades On Chart")
    party = J.get(G_input, "select")("Party", "Any", J.JSArray(["Any", "R", "D"]))
    side = J.get(G_input, "select")("Side", "Any", J.JSArray(["Any", "Buy", "Sell"]))
    binarySearch = G_library("binary-search-bounds")
    data = J.get(G_request, "congress_trading")(J.get(G_current, "ticker"))
    buySignals = G_series_of(None)
    buys = G_series_of(None)
    sellSignals = G_series_of(None)
    sells = G_series_of(None)
    for report in J.iter_of(data):
        candleIndex = J.get(binarySearch, "ge")(G_time, J.get(report, "timestamp"))
        if J.lt(candleIndex, 0):
            continue
        if (J.ne(party, "Any") and J.ne(J.get(report, "party"), party)):
            continue
        if (J.eq(side, "Buy") and J.ne(J.get(report, "transaction"), "purchase")):
            continue
        if (J.eq(side, "Sell") and J.eq(J.get(report, "transaction"), "purchase")):
            continue
        if J.eq(J.get(report, "transaction"), "purchase"):
            J.set(buys, candleIndex, J.template("[", J.get(report, "party"), "] ", J.get(report, "representative"), "<br/>buy"))
            J.set(buySignals, candleIndex, True)
        else:
            J.set(sells, candleIndex, J.template("[", J.get(report, "party"), "]", J.get(report, "representative"), "<br/>sell"))
            J.set(sellSignals, candleIndex, True)
    G_paint(buys, J.obj(("style", "labels_below"), ("backgroundColor", "green"), ("color", "green"), ("verticalOffset", 20)))
    G_paint(sells, J.obj(("style", "labels_above"), ("backgroundColor", "red"), ("color", "red")))
    G_register_signal(buySignals, "Buys")
    G_register_signal(sellSignals, "Sells")


register_store_indicator(
    script,
    name='congress_trades_on_chart_TS',
    title='Congress Trades On Chart',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/us-house-and-senate-trades-on-chart/',
    position='price',
    inputs=[{'id': 'party', 'title': 'Party', 'type': 'select_wide', 'default': 'Any', 'options': ['Any', 'R', 'D']}, {'id': 'side', 'title': 'Side', 'type': 'select_wide', 'default': 'Any', 'options': ['Any', 'Buy', 'Sell']}],
    outputs=['line_1', 'line_2', 'buys', 'sells'],
    signals=['buys', 'sells'],
    requires=['congress_trading'],
    parity='exact',
)
