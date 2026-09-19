"""
ATR Percentage -- TrendSpider store indicator by khaled elsokkary.

Registered as "atr_percentage_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68aa1a-atr-percentage/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Math = G["Math"]
    G_atrPercentage = G["atrPercentage"]
    G_atrPeriod = G["atrPeriod"]
    G_averageTrueRange = G["averageTrueRange"]
    G_avgAtrPercentage = G["avgAtrPercentage"]
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_highCloseRange = G["highCloseRange"]
    G_highLowRange = G["highLowRange"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowCloseRange = G["lowCloseRange"]
    G_paint = G["paint"]
    G_sma = G["sma"]
    G_trueRange = G["trueRange"]
    i = J.undefined
    G_describe_indicator("ATR/Price%")
    G_atrPeriod = G_input("ATR Period", 7)
    G_trueRange = J.JSArray([])
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        if J.seq(i, 0):
            J.set(G_trueRange, i, J.sub(J.get(G_high, i), J.get(G_low, i)))
        else:
            G_highLowRange = J.sub(J.get(G_high, i), J.get(G_low, i))
            G_highCloseRange = J.get(G_Math, "abs")(J.sub(J.get(G_high, i), J.get(G_close, J.sub(i, 1))))
            G_lowCloseRange = J.get(G_Math, "abs")(J.sub(J.get(G_low, i), J.get(G_close, J.sub(i, 1))))
            J.set(G_trueRange, i, J.get(G_Math, "max")(G_highLowRange, G_highCloseRange, G_lowCloseRange))
        i = J.inc(i)
    G_averageTrueRange = G_sma(G_trueRange, G_atrPeriod)
    G_atrPercentage = J.JSArray([])
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        J.set(G_atrPercentage, i, J.mul(J.div(J.get(G_averageTrueRange, i), J.get(G_close, i)), 100))
        i = J.inc(i)
    G_paint(G_atrPercentage, "ATR %", "blue")
    G_avgAtrPercentage = G_sma(G_atrPercentage, 20)
    G_paint(G_avgAtrPercentage, "20-period Avg ATR %", "red")
    G_paint(J.get(G_Array(J.get(G_close, "length")), "fill")(0), "Reference", "#00000001")
    G_describe_indicator("ATR Percentage", "lower")


register_store_indicator(
    script,
    name='atr_percentage_TS',
    title='ATR Percentage',
    developer='khaled elsokkary',
    url='https://trendspider.com/trading-tools-store/indicators/68aa1a-atr-percentage/',
    position='lower',
    inputs=[{'id': 'atr_period', 'title': 'ATR Period', 'type': 'number', 'default': 7}],
    outputs=['atr__', '20_period_avg_atr__', 'reference'],
    signals=[],
    requires=[],
    parity='exact',
)
