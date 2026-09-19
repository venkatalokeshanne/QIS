"""
Slim Ribbon -- TrendSpider store indicator by Jared Crean.

Registered as "slim_ribbon_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a4ebc-slim-ribbon/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_market = G["market"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_describe_indicator("Slim Ribbon", "price")
    priceSource = G_input("Price source", "close", J.get(G_constants, "price_source_options"))
    superfastLen = J.get(G_input, "number")("Superfast EMA length", 8, J.obj(("min", 1), ("max", 200)))
    fastLen = J.get(G_input, "number")("Fast EMA length", 13, J.obj(("min", 1), ("max", 200)))
    slowLen = J.get(G_input, "number")("Slow EMA length", 21, J.obj(("min", 1), ("max", 200)))
    paintCandles = J.get(G_input, "boolean")("Color candles", True)
    showArrows = J.get(G_input, "boolean")("Show signal arrows", True)
    buyColor = J.get(G_input, "color")("Buy color", "#1B5E20")
    sellColor = J.get(G_input, "color")("Sell color", "#EF5350")
    neutralColor = J.get(G_input, "color")("Neutral color", "#FFD54F")
    price = J.get(G_market, priceSource)
    emaSuperfast = G_ema(price, superfastLen)
    emaFast = G_ema(price, fastLen)
    emaSlow = G_ema(price, slowLen)
    buyState = G_series_of(0)
    sellState = G_series_of(0)
    buyStartMarks = G_series_of(None)
    buyStopMarks = G_series_of(None)
    sellStartMarks = G_series_of(None)
    sellStopMarks = G_series_of(None)
    candleColors = G_series_of(None)
    i = 0
    while J.lt(i, J.get(G_close, "length")):
        prevBuy = (J.get(buyState, J.sub(i, 1)) if J.gt(i, 0) else 0)
        prevSell = (J.get(sellState, J.sub(i, 1)) if J.gt(i, 0) else 0)
        buy = (J.gt(J.get(G_low, i), J.get(emaSuperfast, i)) if J.truthy(_t1 := (J.gt(J.get(emaFast, i), J.get(emaSlow, i)) if J.truthy(_t2 := J.gt(J.get(emaSuperfast, i), J.get(emaFast, i))) else _t2)) else _t1)
        stopBuy = J.le(J.get(emaSuperfast, i), J.get(emaFast, i))
        sell = (J.lt(J.get(G_high, i), J.get(emaSuperfast, i)) if J.truthy(_t3 := (J.lt(J.get(emaFast, i), J.get(emaSlow, i)) if J.truthy(_t4 := J.lt(J.get(emaSuperfast, i), J.get(emaFast, i))) else _t4)) else _t3)
        stopSell = J.ge(J.get(emaSuperfast, i), J.get(emaFast, i))
        J.set(buyState, i, (1 if J.truthy(buy) else (0 if J.truthy(stopBuy) else prevBuy)))
        J.set(sellState, i, (1 if J.truthy(sell) else (0 if J.truthy(stopSell) else prevSell)))
        if J.truthy(showArrows):
            if (J.seq(prevBuy, 0) and J.seq(J.get(buyState, i), 1)):
                J.set(buyStartMarks, i, J.get(J.get(G_constants, "icons"), "arrow_up"))
            if (J.seq(prevBuy, 1) and J.seq(J.get(buyState, i), 0)):
                J.set(buyStopMarks, i, J.get(J.get(G_constants, "icons"), "arrow_down"))
            if (J.seq(prevSell, 0) and J.seq(J.get(sellState, i), 1)):
                J.set(sellStartMarks, i, J.get(J.get(G_constants, "icons"), "arrow_down"))
            if (J.seq(prevSell, 1) and J.seq(J.get(sellState, i), 0)):
                J.set(sellStopMarks, i, J.get(J.get(G_constants, "icons"), "arrow_up"))
        if J.truthy(paintCandles):
            J.set(candleColors, i, (buyColor if J.seq(J.get(buyState, i), 1) else (sellColor if J.seq(J.get(sellState, i), 1) else neutralColor)))
        i = J.add(i, 1)
    G_paint(emaSuperfast, J.obj(("name", "Superfast EMA"), ("color", "#2196F3"), ("thickness", 2)))
    G_paint(emaFast, J.obj(("name", "Fast EMA"), ("color", "#FF9800"), ("thickness", 2)))
    G_paint(emaSlow, J.obj(("name", "Slow EMA"), ("color", "#E91E63"), ("thickness", 2)))
    G_paint(buyStartMarks, J.obj(("style", "labels_below"), ("color", buyColor), ("name", "Buy Signal")))
    G_paint(buyStopMarks, J.obj(("style", "labels_above"), ("color", neutralColor), ("name", "Momentum Down")))
    G_paint(sellStartMarks, J.obj(("style", "labels_above"), ("color", sellColor), ("name", "Sell Signal")))
    G_paint(sellStopMarks, J.obj(("style", "labels_below"), ("color", neutralColor), ("name", "Momentum Up")))
    G_color_candles(candleColors)
    G_register_signal(buyState, "Buy Momentum")
    G_register_signal(sellState, "Sell Momentum")


register_store_indicator(
    script,
    name='slim_ribbon_TS',
    title='Slim Ribbon',
    developer='Jared Crean',
    url='https://trendspider.com/trading-tools-store/indicators/6a4ebc-slim-ribbon/',
    position='price',
    inputs=[{'id': 'price_source', 'title': 'Price source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}, {'id': 'superfast_ema_length', 'title': 'Superfast EMA length', 'type': 'number', 'default': 8}, {'id': 'fast_ema_length', 'title': 'Fast EMA length', 'type': 'number', 'default': 13}, {'id': 'slow_ema_length', 'title': 'Slow EMA length', 'type': 'number', 'default': 21}, {'id': 'color_candles', 'title': 'Color candles', 'type': 'boolean', 'default': True}, {'id': 'show_signal_arrows', 'title': 'Show signal arrows', 'type': 'boolean', 'default': True}, {'id': 'buy_color', 'title': 'Buy color', 'type': 'color', 'default': '#1B5E20'}, {'id': 'sell_color', 'title': 'Sell color', 'type': 'color', 'default': '#EF5350'}, {'id': 'neutral_color', 'title': 'Neutral color', 'type': 'color', 'default': '#FFD54F'}],
    outputs=['superfast_ema', 'fast_ema', 'slow_ema', 'buy_signal', 'momentum_down', 'sell_signal', 'momentum_up', 'cdl', 'buy_momentum', 'sell_momentum'],
    signals=['buy_momentum', 'sell_momentum'],
    requires=[],
    parity='exact',
)
