"""
True Daily SMA Pack -- TrendSpider store indicator by LetitBrew!.

Registered as "true_daily_sma_pack_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69d62d-true-daily-sma-pack/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_paint = G["paint"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_sma = G["sma"]
    G_time = G["time"]
    def makeDailySma(length=J.undefined, *_args):
        dailySma = G_sma(J.get(dailyData, "close"), length)
        landed = G_land_points_onto_series(J.get(dailyData, "time"), dailySma, G_time, "le")
        return G_interpolate_sparse_series(landed, "constant")
    def rgba(hex=J.undefined, alphaPct=J.undefined, *_args):
        alpha = J.div(alphaPct, 100)
        h = J.get(hex, "replace")("#", "")
        r = G_parseInt(J.get(h, "substring")(0, 2), 16)
        g = G_parseInt(J.get(h, "substring")(2, 4), 16)
        b = G_parseInt(J.get(h, "substring")(4, 6), 16)
        return J.template("rgba(", r, ", ", g, ", ", b, ", ", alpha, ")")
    G_describe_indicator("True Daily SMA Pack")
    show10 = J.get(G_input, "boolean")("Show 10 DMA", True)
    show20 = J.get(G_input, "boolean")("Show 20 DMA", True)
    show50 = J.get(G_input, "boolean")("Show 50 DMA", True)
    show100 = J.get(G_input, "boolean")("Show 100 DMA", True)
    show200 = J.get(G_input, "boolean")("Show 200 DMA", True)
    opacity = J.get(G_input, "number")("Opacity %", 70, J.obj(("min", 0), ("max", 100)))
    color10 = J.get(G_input, "color")("10 DMA Color", "#00bcd4")
    color20 = J.get(G_input, "color")("20 DMA Color", "#4caf50")
    color50 = J.get(G_input, "color")("50 DMA Color", "#2196f3")
    color100 = J.get(G_input, "color")("100 DMA Color", "#9c27b0")
    color200 = J.get(G_input, "color")("200 DMA Color", "#e53935")
    dailyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "D")
    G_assert((not J.truthy(J.get(dailyData, "error"))), J.template("Error fetching daily data: ", J.get(dailyData, "error")))
    ma10 = (makeDailySma(10) if J.truthy(show10) else G_series_of(None))
    G_paint(ma10, J.obj(("name", "10 DMA"), ("color", G_series_of(rgba(color10, opacity)))))
    ma20 = (makeDailySma(20) if J.truthy(show20) else G_series_of(None))
    G_paint(ma20, J.obj(("name", "20 DMA"), ("color", G_series_of(rgba(color20, opacity)))))
    ma50 = (makeDailySma(50) if J.truthy(show50) else G_series_of(None))
    G_paint(ma50, J.obj(("name", "50 DMA"), ("color", G_series_of(rgba(color50, opacity)))))
    ma100 = (makeDailySma(100) if J.truthy(show100) else G_series_of(None))
    G_paint(ma100, J.obj(("name", "100 DMA"), ("color", G_series_of(rgba(color100, opacity)))))
    ma200 = (makeDailySma(200) if J.truthy(show200) else G_series_of(None))
    G_paint(ma200, J.obj(("name", "200 DMA"), ("color", G_series_of(rgba(color200, opacity)))))


register_store_indicator(
    script,
    name='true_daily_sma_pack_TS',
    title='True Daily SMA Pack',
    developer='LetitBrew!',
    url='https://trendspider.com/trading-tools-store/indicators/69d62d-true-daily-sma-pack/',
    position='price',
    inputs=[{'id': 'show_10_dma', 'title': 'Show 10 DMA', 'type': 'boolean', 'default': True}, {'id': 'show_20_dma', 'title': 'Show 20 DMA', 'type': 'boolean', 'default': True}, {'id': 'show_50_dma', 'title': 'Show 50 DMA', 'type': 'boolean', 'default': True}, {'id': 'show_100_dma', 'title': 'Show 100 DMA', 'type': 'boolean', 'default': True}, {'id': 'show_200_dma', 'title': 'Show 200 DMA', 'type': 'boolean', 'default': True}, {'id': 'opacity__', 'title': 'Opacity %', 'type': 'number', 'default': 70}, {'id': '10_dma_color', 'title': '10 DMA Color', 'type': 'color', 'default': '#00bcd4'}, {'id': '20_dma_color', 'title': '20 DMA Color', 'type': 'color', 'default': '#4caf50'}, {'id': '50_dma_color', 'title': '50 DMA Color', 'type': 'color', 'default': '#2196f3'}, {'id': '100_dma_color', 'title': '100 DMA Color', 'type': 'color', 'default': '#9c27b0'}, {'id': '200_dma_color', 'title': '200 DMA Color', 'type': 'color', 'default': '#e53935'}],
    outputs=['10_dma', '20_dma', '50_dma', '100_dma', '200_dma'],
    signals=[],
    requires=['history'],
    parity='exact',
)
