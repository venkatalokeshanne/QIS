"""
Ripster Candle Rvol -- TrendSpider store indicator by Ripster G.

Registered as "ripster_candle_rvol_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/691ab8-ripster-candle-rvol/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_input = G["input"]
    G_mult = G["mult"]
    G_paint_overlay = G["paint_overlay"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("Ripster Candle Rvol")
    myAverageCandles = J.get(G_input, "number")("Average of Candles", 50, J.obj(("min", 1)))
    myLocation = "top_right"
    myCurrentCandleVolume = J.get(G_volume, J.sub(J.get(G_volume, "length"), 1))
    myAverageVolume = J.get(G_sma(G_volume, myAverageCandles), J.sub(J.get(G_volume, "length"), 1))
    myRelativeVolume = J.mul(J.div(myCurrentCandleVolume, myAverageVolume), 100)
    myRelativeVolumeSeries = G_div(G_volume, G_sma(G_volume, myAverageCandles))
    myRelativeVolumePercent = G_mult(myRelativeVolumeSeries, 100)
    previousRvol = G_shift(myRelativeVolumePercent, 1)
    def formatVolume(vol=J.undefined, *_args):
        return (J.add(J.get(J.div(vol, 1000000), "toFixed")(2), "M") if J.ge(vol, 1000000) else J.get(vol, "toString")())
    myLightGray = "#D3D3D3"
    myOrange = "orange"
    myRed = "red"
    myGreen = "green"
    myYellow = "yellow"
    myDarkBorder = "#333333"
    myRvolColor = (myRed if J.gt(myRelativeVolume, 200) else (myOrange if J.gt(myRelativeVolume, 100) else myYellow))
    myLastRvolColor = (myRed if J.gt(J.get(previousRvol, J.sub(J.get(previousRvol, "length"), 1)), 200) else (myOrange if J.gt(J.get(previousRvol, J.sub(J.get(previousRvol, "length"), 1)), 100) else myYellow))
    G_paint_overlay("Volume Table", J.obj(("position", myLocation), ("offset_x", (-100))), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", "Candle Vol"), ("color", "white"), ("background", myGreen), ("fontSize", 12), ("fontWeight", "bold"), ("border", J.template("solid ", myDarkBorder, " 1px")), ("padding", 8)), J.obj(("text", formatVolume(myCurrentCandleVolume)), ("color", "black"), ("background", myYellow), ("fontSize", 12), ("fontWeight", "bold"), ("border", J.template("solid ", myDarkBorder, " 1px")), ("padding", 8)), J.obj(("text", "Prev. Candle Rvol"), ("color", "white"), ("background", myGreen), ("fontSize", 12), ("fontWeight", "bold"), ("border", J.template("solid ", myDarkBorder, " 1px")), ("padding", 8))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Candle Rvol"), ("color", "white"), ("background", myGreen), ("fontSize", 12), ("fontWeight", "bold"), ("border", J.template("solid ", myDarkBorder, " 1px")), ("padding", 8)), J.obj(("text", J.add(J.get(myRelativeVolume, "toFixed")(2), "%")), ("color", "black"), ("background", myRvolColor), ("fontSize", 12), ("fontWeight", "bold"), ("border", J.template("solid ", myDarkBorder, " 1px")), ("padding", 8)), J.obj(("text", (J.add(J.get(J.get(previousRvol, J.sub(J.get(previousRvol, "length"), 1)), "toFixed")(2), "%") if J.truthy(J.get(previousRvol, J.sub(J.get(previousRvol, "length"), 1))) else "N/A")), ("color", "black"), ("background", myLastRvolColor), ("fontSize", 12), ("fontWeight", "bold"), ("border", J.template("solid ", myDarkBorder, " 1px")), ("padding", 8))])))])), ("cellPadding", 0), ("rowGap", 1), ("border", J.template("solid ", myDarkBorder, " 6px")), ("borderRadius", 4)))


register_store_indicator(
    script,
    name='ripster_candle_rvol_TS',
    title='Ripster Candle Rvol',
    developer='Ripster G',
    url='https://trendspider.com/trading-tools-store/indicators/691ab8-ripster-candle-rvol/',
    position='price',
    inputs=[{'id': 'average_of_candles', 'title': 'Average of Candles', 'type': 'number', 'default': 50}],
    outputs=[],
    signals=[],
    requires=[],
    parity='exact',
)
