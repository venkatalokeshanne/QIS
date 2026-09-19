"""
Nancy Pelosi Insider Trades -- TrendSpider store indicator by TrendSpider Team.

Registered as "nancy_pelosi_insider_trades_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/nancy-pelosi-insider-trades/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_describe_indicator("Nancy Pelosi Trade Tracker")
    binarySearch = G_library("binary-search-bounds")
    data = J.get(G_request, "congress_trading")(J.get(G_current, "ticker"))
    G_assert((not J.truthy(J.get(data, "error"))), J.template("Error fetching data: ", J.get(data, "error")))
    myBuySignals = G_series_of(None)
    myBuys = G_series_of(None)
    mySellSignals = G_series_of(None)
    mySells = G_series_of(None)
    for report in J.iter_of(data):
        candleIndex = J.get(binarySearch, "ge")(G_time, J.get(report, "timestamp"))
        if J.lt(candleIndex, 0):
            continue
        if J.sne(J.get(report, "representative"), "Nancy Pelosi"):
            continue
        if J.seq(J.get(report, "transaction"), "purchase"):
            J.set(myBuys, candleIndex, J.template("Nancy Pelosi<br/>buy"))
            J.set(myBuySignals, candleIndex, True)
        else:
            J.set(mySells, candleIndex, J.template("Nancy Pelosi<br/>sell"))
            J.set(mySellSignals, candleIndex, True)
    G_paint(myBuys, J.obj(("style", "labels_below"), ("backgroundColor", "green"), ("color", "white"), ("verticalOffset", 20)))
    G_paint(mySells, J.obj(("style", "labels_above"), ("backgroundColor", "red"), ("color", "white")))
    G_register_signal(myBuySignals, "Pelosi Buys")
    G_register_signal(mySellSignals, "Pelosi Sells")


register_store_indicator(
    script,
    name='nancy_pelosi_insider_trades_TS',
    title='Nancy Pelosi Insider Trades',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/nancy-pelosi-insider-trades/',
    position='price',
    inputs=[],
    outputs=['line_1', 'line_2', 'pelosi_buys', 'pelosi_sells'],
    signals=['pelosi_buys', 'pelosi_sells'],
    requires=['congress_trading'],
    parity='exact',
)
