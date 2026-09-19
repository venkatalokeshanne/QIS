"""
Liquidity Levels -- TrendSpider store indicator by TrendSpider Team.

Registered as "liquidity_levels_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/liquidity-levels/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_describe_indicator = G["describe_indicator"]
    G_fractal_high = G["fractal_high"]
    G_fractal_low = G["fractal_low"]
    G_high = G["high"]
    G_horizontal_line = G["horizontal_line"]
    G_low = G["low"]
    G_paint = G["paint"]
    G_series_of = G["series_of"]
    G_describe_indicator("Liquidity Levels", "price", J.obj(("shortName", "Liquidity")))
    fractalHigh = G_fractal_high(G_high, 51)
    fractalLow = G_fractal_low(G_low, 51)
    remainingTopLines = 5
    remainingBottomLines = 5
    candleIndex = J.sub(J.get(G_high, "length"), 1)
    while J.ge(candleIndex, 0):
        if ((J.get(fractalHigh, candleIndex) is not None) and J.gt(remainingTopLines, 0)):
            G_paint(G_horizontal_line(J.get(G_high, candleIndex), candleIndex), J.add("Top line ", remainingTopLines), "red")
            remainingTopLines = J.dec(remainingTopLines)
        if ((J.get(fractalLow, candleIndex) is not None) and J.gt(remainingBottomLines, 0)):
            G_paint(G_horizontal_line(J.get(G_low, candleIndex), candleIndex), J.add("Bottom line ", remainingBottomLines), "green")
            remainingBottomLines = J.dec(remainingBottomLines)
        candleIndex = J.dec(candleIndex)
    while J.gt(remainingTopLines, 0):
        G_paint(G_series_of(None), J.add("Top line ", remainingTopLines), "red")
        remainingTopLines = J.dec(remainingTopLines)
    while J.gt(remainingBottomLines, 0):
        G_paint(G_series_of(None), J.add("Bottom line ", remainingBottomLines), "red")
        remainingBottomLines = J.dec(remainingBottomLines)


register_store_indicator(
    script,
    name='liquidity_levels_TS',
    title='Liquidity Levels',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/liquidity-levels/',
    position='price',
    inputs=[],
    outputs=['top_line_5', 'bottom_line_5', 'bottom_line_4', 'top_line_4', 'bottom_line_3', 'top_line_3', 'top_line_2', 'top_line_1', 'bottom_line_2', 'bottom_line_1'],
    signals=[],
    requires=[],
    parity='exact',
)
