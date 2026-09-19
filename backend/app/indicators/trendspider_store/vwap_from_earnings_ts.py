"""
VWAP from Earnings -- TrendSpider store indicator by TrendSpider Team.

Registered as "vwap_from_earnings_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/vwap-from-earnings/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: OK.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_candles = G["candles"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_vwap = G["vwap"]
    G_describe_indicator("VWAP from Earnings", J.obj(("warmup", 1000)))
    binarySearch = G_library("binary-search-bounds")
    earnings = J.get(G_request, "earnings")(J.get(G_current, "ticker"))
    result = G_series_of(None)
    def _f1(report=J.undefined, *_args):
        return J.get(binarySearch, "le")(G_time, J.get(report, "timestamp"))
    def _f2(index=J.undefined, *_args):
        return J.ge(index, 0)
    earningsDatesLanded = J.get(J.get(earnings, "map")(_f1), "filter")(_f2)
    reportIndex = 0
    while J.lt(reportIndex, J.get(earningsDatesLanded, "length")):
        fromCandle = J.get(earningsDatesLanded, reportIndex)
        toCandle = (_t3 if J.truthy(_t3 := J.get(earningsDatesLanded, J.add(reportIndex, 1))) else J.sub(J.get(G_candles, "length"), 1))
        vwapComputed = G_vwap(fromCandle, toCandle)
        candleIndex = fromCandle
        while J.le(candleIndex, toCandle):
            J.set(result, candleIndex, J.get(vwapComputed, candleIndex))
            candleIndex = J.add(candleIndex, 1)
        reportIndex = J.add(reportIndex, 1)
    G_paint(result, J.obj(("color", "grey"), ("name", "AVWAP/Earnings")))


register_store_indicator(
    script,
    name='vwap_from_earnings_TS',
    title='VWAP from Earnings',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/vwap-from-earnings/',
    position='price',
    inputs=[{'id': 'warmup', 'title': 'Warmup', 'type': 'number', 'default': 1000}],
    outputs=[],
    signals=[],
    requires=['earnings'],
    parity='aapl_d: both-error, syn_5m: OK',
)
