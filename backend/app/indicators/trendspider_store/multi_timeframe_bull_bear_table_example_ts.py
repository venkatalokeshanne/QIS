"""
Multi-Timeframe Bull/Bear Table Example -- TrendSpider store indicator by TrendSpider Team.

Registered as "multi_timeframe_bull_bear_table_example_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/multi-timeframe-bull-bear-table-example/)
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
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_time = G["time"]
    def calculateRecommendation(data=J.undefined, *_args):
        shortEMA = G_ema(J.get(data, "close"), emaShortLength)
        longEMA = G_ema(J.get(data, "close"), emaLongLength)
        latestClose = J.get(J.get(data, "close"), J.sub(J.get(J.get(data, "close"), "length"), 1))
        if (J.gt(latestClose, J.get(shortEMA, J.sub(J.get(shortEMA, "length"), 1))) and J.gt(latestClose, J.get(longEMA, J.sub(J.get(longEMA, "length"), 1)))):
            return J.obj(("label", "Strong Bullish"), ("color", "rgba(0, 255, 0, 0.8)"))
        elif (J.gt(latestClose, J.get(shortEMA, J.sub(J.get(shortEMA, "length"), 1))) and J.lt(latestClose, J.get(longEMA, J.sub(J.get(longEMA, "length"), 1)))):
            return J.obj(("label", "Bullish"), ("color", "rgba(0, 128, 0, 0.8)"))
        elif (J.lt(latestClose, J.get(shortEMA, J.sub(J.get(shortEMA, "length"), 1))) and J.gt(latestClose, J.get(longEMA, J.sub(J.get(longEMA, "length"), 1)))):
            return J.obj(("label", "Bearish"), ("color", "rgba(255, 0, 0, 0.8)"))
        elif (J.lt(latestClose, J.get(shortEMA, J.sub(J.get(shortEMA, "length"), 1))) and J.lt(latestClose, J.get(longEMA, J.sub(J.get(longEMA, "length"), 1)))):
            return J.obj(("label", "Strong Bearish"), ("color", "rgba(255, 69, 0, 0.8)"))
        else:
            return J.obj(("label", "Neutral"), ("color", "rgba(128, 128, 128, 0.8)"))
    G_describe_indicator("Multi-Timeframe Bull/Bear Recommendation Table Example", "price")
    emaShortLength = 5
    emaLongLength = 21
    timeframe1 = "60"
    timeframe2 = "D"
    timeframe3 = J.get(G_current, "resolution")
    dataTimeframe1 = J.get(G_request, "history")(J.get(G_constants, "ticker"), timeframe1)
    dataTimeframe2 = J.get(G_request, "history")(J.get(G_constants, "ticker"), timeframe2)
    dataTimeframe3 = J.obj(("close", G_close), ("time", G_time))
    recommendation1 = calculateRecommendation(dataTimeframe1)
    recommendation2 = calculateRecommendation(dataTimeframe2)
    recommendation3 = calculateRecommendation(dataTimeframe3)
    G_paint_overlay("Multi-Timeframe Recommendation Table", J.obj(("position", "bottom_right")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "1 Hour"), ("fontSize", "15px"), ("fontWeight", "bold"), ("textAlign", "center"), ("color", "white"), ("padding", "20px")), J.obj(("text", "Daily"), ("fontSize", "15px"), ("fontWeight", "bold"), ("textAlign", "center"), ("color", "white"), ("padding", "20px")), J.obj(("text", "Current"), ("fontSize", "15px"), ("fontWeight", "bold"), ("textAlign", "center"), ("color", "white"), ("padding", "20px"))]))), J.obj(("cells", J.JSArray([J.obj(("text", J.get(recommendation1, "label")), ("fontSize", "15px"), ("fontWeight", "bold"), ("textAlign", "center"), ("color", "white"), ("backgroundColor", J.get(recommendation1, "color")), ("padding", "10px")), J.obj(("text", J.get(recommendation2, "label")), ("fontSize", "15px"), ("fontWeight", "bold"), ("textAlign", "center"), ("color", "white"), ("backgroundColor", J.get(recommendation2, "color")), ("padding", "10px")), J.obj(("text", J.get(recommendation3, "label")), ("fontSize", "15px"), ("fontWeight", "bold"), ("textAlign", "center"), ("color", "white"), ("backgroundColor", J.get(recommendation3, "color")), ("padding", "10px"))])))]))))


register_store_indicator(
    script,
    name='multi_timeframe_bull_bear_table_example_TS',
    title='Multi-Timeframe Bull/Bear Table Example',
    developer='TrendSpider Team',
    url='https://trendspider.com/trading-tools-store/indicators/multi-timeframe-bull-bear-table-example/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='exact',
)
