"""
Ehlers Decycler -- TrendSpider store indicator by James Chambers.

Registered as "ehlers_decycler_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/ehlers-decycler/)
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
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    def Decycler(src_2=J.undefined, length_2=J.undefined, *_args):
        PIx2_Length = J.div(J.mul(J.get(G_Math, "PI"), 2), length_2)
        cos = J.get(G_Math, "cos")(PIx2_Length)
        alpha = (J.div(J.sub(J.add(cos, J.get(G_Math, "sin")(PIx2_Length)), 1), cos) if J.sne(cos, 0) else 0)
        decycler = G_series_of(None)
        i = 1
        while J.lt(i, J.get(src_2, "length")):
            if J.seq(i, 1):
                J.set(decycler, i, J.mul(J.div(alpha, 2), J.add(J.get(src_2, i), J.get(src_2, J.sub(i, 1)))))
            else:
                J.set(decycler, i, J.add(J.mul(J.div(alpha, 2), J.add(J.get(src_2, i), J.get(src_2, J.sub(i, 1)))), J.mul(J.sub(1, alpha), J.get(decycler, J.sub(i, 1)))))
            i = J.inc(i)
        return decycler
    def MA_Smart_Color(ma_2=J.undefined, smart_clr_ON_2=J.undefined, color_up=J.undefined, color_dn=J.undefined, clr=J.undefined, *_args):
        clr_ma_2 = G_series_of(None)
        i = 1
        while J.lt(i, J.get(ma_2, "length")):
            if (not J.truthy(smart_clr_ON_2)):
                J.set(clr_ma_2, i, clr)
            elif J.gt(J.get(ma_2, i), J.get(ma_2, J.sub(i, 1))):
                J.set(clr_ma_2, i, color_up)
            elif J.lt(J.get(ma_2, i), J.get(ma_2, J.sub(i, 1))):
                J.set(clr_ma_2, i, color_dn)
            else:
                J.set(clr_ma_2, i, J.get(clr_ma_2, J.sub(i, 1)))
            i = J.inc(i)
        return clr_ma_2
    G_describe_indicator("Ehlers Decycler", "price", J.obj(("shortName", "Decycler"), ("decimals", 2)))
    length = J.get(G_input, "number")("Length", 60, J.obj(("min", 1), ("max", 10000)))
    src = J.get(G_input, "select")("Source", "close", J.JSArray(["open", "high", "low", "close"]))
    clr_mono = J.get(G_input, "color")("Mono Color", "blue")
    clr_up = J.get(G_input, "color")("Up Color", "green")
    clr_dn = J.get(G_input, "color")("Down Color", "red")
    smart_clr_ON = J.get(G_input, "boolean")("Colorize", True)
    line_width = J.get(G_input, "number")("Line Width", 2, J.obj(("min", 1), ("max", 20)))
    priceSeries = J.get(J.obj(("open", G_open), ("high", G_high), ("low", G_low), ("close", G_close)), src)
    ma = Decycler(priceSeries, length)
    clr_ma = MA_Smart_Color(ma, smart_clr_ON, clr_up, clr_dn, clr_mono)
    G_paint(ma, J.obj(("name", "Decycler"), ("color", clr_ma), ("thickness", line_width)))
    def _f1(val=J.undefined, idx=J.undefined, *_args):
        return (J.gt(idx, 0) if J.truthy(_t1 := J.gt(val, J.get(ma, J.sub(idx, 1)))) else _t1)
    EVENT_up = G_for_every(ma, _f1)
    def _f2(val=J.undefined, idx=J.undefined, *_args):
        return (J.gt(idx, 0) if J.truthy(_t1 := J.lt(val, J.get(ma, J.sub(idx, 1)))) else _t1)
    EVENT_dn = G_for_every(ma, _f2)
    G_register_signal(EVENT_up, "Trend up")
    G_register_signal(EVENT_dn, "Trend down")


register_store_indicator(
    script,
    name='ehlers_decycler_TS',
    title='Ehlers Decycler',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/ehlers-decycler/',
    position='price',
    inputs=[{'id': 'length', 'title': 'Length', 'type': 'number', 'default': 60}, {'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close']}, {'id': 'mono_color', 'title': 'Mono Color', 'type': 'color', 'default': 'blue'}, {'id': 'up_color', 'title': 'Up Color', 'type': 'color', 'default': 'green'}, {'id': 'down_color', 'title': 'Down Color', 'type': 'color', 'default': 'red'}, {'id': 'colorize', 'title': 'Colorize', 'type': 'boolean', 'default': True}, {'id': 'line_width', 'title': 'Line Width', 'type': 'number', 'default': 2}],
    outputs=['decycler', 'trend_up', 'trend_down'],
    signals=['trend_up', 'trend_down'],
    requires=[],
    parity='exact',
)
