"""
CNN Fear & Greed Index -- TrendSpider store indicator by TrendSpider.

Registered as "cnn_fear_greed_index_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69e799-cnn-fear-greed-index/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_close = G["close"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_horizontal_line = G["horizontal_line"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_request = G["request"]
    G_time = G["time"]
    G_describe_indicator("CNN Fear & Greed Index", "lower", J.obj(("decimals", 0), ("shortName", "CNN F&G")))
    ratingColors = J.obj(("extreme fear", "#cc2222"), ("fear", "#e07020"), ("neutral", "#888888"), ("greed", "#70bb50"), ("extreme greed", "#1a8c3a"))
    myData = J.get(G_request, "http")(J.template("https://production.dataviz.cnn.io/index/fearandgreed/graphdata"), 60, J.obj(("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"), ("accept", "application/json")))
    fngData = J.get(J.get(myData, "fear_and_greed_historical"), "data")
    def _f1(d=J.undefined, *_args):
        return J.div(J.get(d, "x"), 1000)
    fngTimestamps = J.get(fngData, "map")(_f1)
    def _f2(d=J.undefined, *_args):
        return J.get(d, "y")
    fngValues = J.get(fngData, "map")(_f2)
    def _f3(d=J.undefined, *_args):
        return J.get(d, "rating")
    fngRating = J.get(fngData, "map")(_f3)
    landedData = G_land_points_onto_series(fngTimestamps, fngValues, G_time, "ge")
    J.set(landedData, J.sub(J.get(G_close, "length"), 1), J.get(fngValues, J.sub(J.get(fngValues, "length"), 1)))
    mySeriesForPaint = G_interpolate_sparse_series(landedData)
    ratingSeries = G_interpolate_sparse_series(G_land_points_onto_series(fngTimestamps, fngRating, G_time, "ge"), "constant")
    def _f4(rating=J.undefined, *_args):
        return J.get(ratingColors, rating)
    myColorSeries = J.get(ratingSeries, "map")(_f4)
    bottom = G_paint(G_horizontal_line((-50)), J.obj(("hidden", True)))
    l25 = G_paint(G_horizontal_line(25), J.obj(("hidden", True)))
    l45 = G_paint(G_horizontal_line(45), J.obj(("hidden", True)))
    l55 = G_paint(G_horizontal_line(55), J.obj(("hidden", True)))
    l75 = G_paint(G_horizontal_line(75), J.obj(("hidden", True)))
    top = G_paint(G_horizontal_line(150), J.obj(("hidden", True)))
    G_fill(bottom, l25, J.get(ratingColors, "extreme fear"), 0.2, "Extreme fear")
    G_fill(l25, l45, J.get(ratingColors, "fear"), 0.2, "Fear")
    G_fill(l45, l55, J.get(ratingColors, "neutral"), 0.2, "Neutral")
    G_fill(l55, l75, J.get(ratingColors, "greed"), 0.2, "Greed")
    G_fill(l75, top, J.get(ratingColors, "extreme greed"), 0.2, "Extreme greed")
    myMainLine = G_paint(mySeriesForPaint, J.obj(("name", "Fear & Greed"), ("color", myColorSeries), ("thickness", 2), ("style", "line")))
    myCurrentScore = J.get(J.get(myData, "fear_and_greed"), "score")
    myCurrentRating = J.get(J.get(myData, "fear_and_greed"), "rating")
    myLabelBgColor = J.get(ratingColors, myCurrentRating)
    G_paint_label_at_line(myMainLine, J.sub(J.get(G_close, "length"), 1), J.template("F&G: ", J.get(myCurrentScore, "toFixed")(0), " (", myCurrentRating, ")"), J.obj(("color", "white"), ("background_color", myLabelBgColor), ("border_radius", 3), ("border_width", 1), ("border_color", "black"), ("vertical_align", "middle")))


register_store_indicator(
    script,
    name='cnn_fear_greed_index_TS',
    title='CNN Fear & Greed Index',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69e799-cnn-fear-greed-index/',
    position='lower',
    inputs=[],
    outputs=[],
    signals=[],
    requires=['http'],
    parity='aapl_d: both-error, syn_5m: both-error',
)
