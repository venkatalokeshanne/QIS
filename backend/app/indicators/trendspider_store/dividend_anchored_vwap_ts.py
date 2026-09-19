"""
Dividend Anchored VWAP -- TrendSpider store indicator by TrendSpider Team.

Registered as "dividend_anchored_vwap_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/dividend-anchored-vwap/)
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
    G_request = G["request"]
    G_time = G["time"]
    G_vwap = G["vwap"]
    G_describe_indicator("Dividends Anchored VWAP", "price", J.obj(("shortName", "DivAVWAP")))
    binarySearch = G_library("binary-search-bounds")
    dividends = J.get(G_request, "dividends")(J.get(G_current, "ticker"))
    dateType = J.get(G_input, "select")("Dividend Date Type", "Ex-Dividend", J.JSArray(["Ex-Dividend", "Declaration", "Record"]))
    def _f1(dividend=J.undefined, *_args):
        if (J.seq(dateType, "Ex-Dividend") and J.seq(J.get(dividend, "type"), "ex-date")):
            return True
        if (J.seq(dateType, "Declaration") and J.seq(J.get(dividend, "type"), "declaration")):
            return True
        if (J.seq(dateType, "Record") and J.seq(J.get(dividend, "type"), "record")):
            return True
        return False
    selectedDividends = J.get(dividends, "filter")(_f1)
    if J.gt(J.get(selectedDividends, "length"), 0):
        lastDividendDate = J.get(J.get(selectedDividends, J.sub(J.get(selectedDividends, "length"), 1)), "timestamp")
        lastDividendIndex = J.get(binarySearch, "lt")(G_time, lastDividendDate)
        if J.ge(lastDividendIndex, 0):
            G_paint(G_vwap(lastDividendIndex), J.obj(("color", "purple"), ("thickness", 2), ("name", J.template("VWAP/", dateType))))


register_store_indicator(
    script,
    name='dividend_anchored_vwap_TS',
    title='Dividend Anchored VWAP',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/dividend-anchored-vwap/',
    position='price',
    inputs=[{'id': 'dividend_date_type', 'title': 'Dividend Date Type', 'type': 'select_wide', 'default': 'Ex-Dividend', 'options': ['Ex-Dividend', 'Declaration', 'Record']}],
    outputs=['vwap_ex_dividend'],
    signals=[],
    requires=['dividends'],
    parity='exact',
)
