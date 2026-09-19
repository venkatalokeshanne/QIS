"""
Dividend Efficiency Indicator -- TrendSpider store indicator by TrendSpider Team.

Registered as "dividend_efficiency_indicator_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/dividend-efficiency-indicator/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_request = G["request"]
    G_describe_indicator("Dividend Efficiency Indicator", "lower")
    investmentCapital = J.get(G_input, "number")("Starting Capital", 10000, J.obj(("min", 1), ("max", 1000000)))
    fundamentalData = J.get(G_request, "fundamental")(J.get(G_constants, "ticker"), J.JSArray(["dividends_per_share"]), 1)
    recentDividend = (J.get(J.get(J.get(fundamentalData, "dividends_per_share"), 0), "value") if J.gt(J.get(J.get(fundamentalData, "dividends_per_share"), "length"), 0) else 0)
    def _f1(price=J.undefined, *_args):
        sharesPurchasable = J.div(investmentCapital, price)
        totalDividendIncome = J.mul(sharesPurchasable, recentDividend)
        return totalDividendIncome
    dividendEfficiencySeries = J.get(G_close, "map")(_f1)
    G_paint(dividendEfficiencySeries, J.obj(("color", "green"), ("style", "line"), ("name", "Dividend Efficiency")))


register_store_indicator(
    script,
    name='dividend_efficiency_indicator_TS',
    title='Dividend Efficiency Indicator',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/dividend-efficiency-indicator/',
    position='lower',
    inputs=[{'id': 'starting_capital', 'title': 'Starting Capital', 'type': 'number', 'default': 10000}],
    outputs=['dividend_efficiency'],
    signals=[],
    requires=['fundamental'],
    parity='exact',
)
