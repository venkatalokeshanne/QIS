"""
Dynamo Cloud -- TrendSpider store indicator by Trade Seekers.

Registered as "dynamo_cloud_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689fc0-dynamo-cloud/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_close = G["close"]
    G_cmo = G["cmo"]
    G_color_cloud = G["color_cloud"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_paint = G["paint"]
    G_describe_indicator("Dynamo Cloud", J.obj(("decimals", 2)))
    colorUp = "#60935D"
    colorDown = "#D35F70"
    colorCounterAbove = "#902737"
    colorCounterBelow = "#13471d"
    lengthShort = 9
    lengthLong = 14
    lengthBalance = 28
    alphaShort = J.div(2, J.add(lengthShort, 1))
    alphaLong = J.div(2, J.add(lengthLong, 1))
    alphaBalance = J.div(2, J.add(lengthBalance, 1))
    priceCmoShort = G_cmo(G_close, lengthShort)
    priceCmoLong = G_cmo(G_close, lengthLong)
    priceCmoBalance = G_cmo(G_close, lengthBalance)
    def _f1(curPrice=J.undefined, cmoValue=J.undefined, prevValue=J.undefined, *_args):
        if ((curPrice is None) or (cmoValue is None)):
            return None
        if (prevValue is None):
            return curPrice
        absCmo = J.get(G_Math, "abs")(cmoValue)
        return J.add(J.mul(J.mul(curPrice, alphaShort), absCmo), J.mul(prevValue, J.sub(1, J.mul(alphaShort, absCmo))))
    vidyaShort = G_for_every(G_close, priceCmoShort, _f1)
    def _f2(curPrice=J.undefined, cmoValue=J.undefined, prevValue=J.undefined, *_args):
        if ((curPrice is None) or (cmoValue is None)):
            return None
        if (prevValue is None):
            return curPrice
        absCmo = J.get(G_Math, "abs")(cmoValue)
        return J.add(J.mul(J.mul(curPrice, alphaLong), absCmo), J.mul(prevValue, J.sub(1, J.mul(alphaLong, absCmo))))
    vidyaLong = G_for_every(G_close, priceCmoLong, _f2)
    def _f3(curPrice=J.undefined, cmoValue=J.undefined, prevValue=J.undefined, *_args):
        if ((curPrice is None) or (cmoValue is None)):
            return None
        if (prevValue is None):
            return curPrice
        absCmo = J.get(G_Math, "abs")(cmoValue)
        return J.add(J.mul(J.mul(curPrice, alphaBalance), absCmo), J.mul(prevValue, J.sub(1, J.mul(alphaBalance, absCmo))))
    vidyaBalance = G_for_every(G_close, priceCmoBalance, _f3)
    def _f4(s=J.undefined, l=J.undefined, b=J.undefined, *_args):
        return (colorUp if J.gt(s, l) else colorDown)
    shortColors = G_for_every(vidyaShort, vidyaLong, vidyaBalance, _f4)
    def _f5(s=J.undefined, l=J.undefined, b=J.undefined, *_args):
        return (colorCounterBelow if J.gt(s, b) else colorCounterAbove)
    balanceColors = G_for_every(vidyaShort, vidyaLong, vidyaBalance, _f5)
    G_paint(vidyaShort, "Short", shortColors)
    G_paint(vidyaLong, "Long", shortColors)
    G_paint(vidyaBalance, "Balance", balanceColors)
    G_color_cloud(vidyaShort, vidyaLong, colorUp, colorDown, "Up Trend", "Down Trend")
    G_color_cloud(vidyaBalance, vidyaLong, colorCounterAbove, colorCounterBelow, "Counter Trend Down", "Counter Trend Up")


register_store_indicator(
    script,
    name='dynamo_cloud_TS',
    title='Dynamo Cloud',
    developer='Trade Seekers',
    url='https://trendspider.com/trading-tools-store/indicators/689fc0-dynamo-cloud/',
    position='price',
    inputs=[],
    outputs=['short', 'long', 'balance', 'line_7', 'line_8', 'line_10', 'line_11', 'line_13', 'line_14', 'line_16', 'line_17'],
    signals=[],
    requires=[],
    parity='exact',
)
