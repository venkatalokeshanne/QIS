"""
ALMA Channels with Signals -- TrendSpider store indicator by Kodexius.

Registered as "alma_channels_with_signals_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68e750-hurst-alma-channels-with-signals-kodexius/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_add = G["add"]
    G_alma = G["alma"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_for_every = G["for_every"]
    G_high = G["high"]
    G_input = G["input"]
    G_low = G["low"]
    G_market = G["market"]
    G_mult = G["mult"]
    G_paint = G["paint"]
    G_shift = G["shift"]
    G_sub = G["sub"]
    G_describe_indicator("ALMA Channels with Signals")
    scl_t = J.get(G_input, "number")("Short Length", 14, J.obj(("min", 1), ("max", 500)))
    mcl_t = J.get(G_input, "number")("Medium Length", 30, J.obj(("min", 1), ("max", 500)))
    lcl_t = J.get(G_input, "number")("Long Length", 60, J.obj(("min", 1), ("max", 500)))
    scm = J.get(G_input, "number")("Short Multiplier", 2, J.obj(("min", 0.1), ("max", 10)))
    mcm = J.get(G_input, "number")("Medium Multiplier", 4, J.obj(("min", 0.1), ("max", 10)))
    lcm = J.get(G_input, "number")("Long Multiplier", 8, J.obj(("min", 0.1), ("max", 10)))
    priceSource = J.get(G_input, "select")("Source", "close", J.get(G_constants, "price_source_options"))
    src = J.get(G_market, priceSource)
    scl = J.get(G_Math, "floor")(J.div(scl_t, 2))
    mcl = J.get(G_Math, "floor")(J.div(mcl_t, 2))
    lcl = J.get(G_Math, "floor")(J.div(lcl_t, 2))
    ma_scl = G_alma(src, scl, 0.85, 6)
    ma_mcl = G_alma(src, mcl, 0.85, 6)
    ma_lcl = G_alma(src, lcl, 0.85, 6)
    scm_off = G_mult(G_atr(G_high, G_low, G_close, scl), scm)
    mcm_off = G_mult(G_atr(G_high, G_low, G_close, mcl), mcm)
    lcm_off = G_mult(G_atr(G_high, G_low, G_close, lcl), lcm)
    scl_2 = J.get(G_Math, "floor")(J.div(scl, 2))
    mcl_2 = J.get(G_Math, "floor")(J.div(mcl, 2))
    lcl_2 = J.get(G_Math, "floor")(J.div(lcl, 2))
    ma_scl_shifted = G_shift(ma_scl, scl_2)
    ma_mcl_shifted = G_shift(ma_mcl, mcl_2)
    ma_lcl_shifted = G_shift(ma_lcl, lcl_2)
    sct = G_add(ma_scl_shifted, scm_off)
    scb = G_sub(ma_scl_shifted, scm_off)
    mct = G_add(ma_mcl_shifted, mcm_off)
    mcb = G_sub(ma_mcl_shifted, mcm_off)
    lct = G_add(ma_lcl_shifted, lcm_off)
    lcb = G_sub(ma_lcl_shifted, lcm_off)
    sct_line = G_paint(sct, J.obj(("color", "#306e43"), ("name", "ShortCycleBandTop")))
    scb_line = G_paint(scb, J.obj(("color", "#306e43"), ("name", "ShortCycleBandBottom")))
    def _f1(t=J.undefined, b=J.undefined, *_args):
        return J.div(J.add(t, b), 2)
    G_paint(G_for_every(sct, scb, _f1), J.obj(("color", "green"), ("name", "ShortCycleMedian"), ("style", "line")))
    mct_line = G_paint(mct, J.obj(("color", "#3e56a7"), ("name", "MediumCycleBandTop")))
    mcb_line = G_paint(mcb, J.obj(("color", "#3e56a7"), ("name", "MediumCycleBandBottom")))
    def _f2(t=J.undefined, b=J.undefined, *_args):
        return J.div(J.add(t, b), 2)
    G_paint(G_for_every(mct, mcb, _f2), J.obj(("color", "blue"), ("name", "MediumCycleMedian"), ("style", "line")))
    lct_line = G_paint(lct, J.obj(("color", "#940e0e"), ("name", "LongCycleBandTop")))
    lcb_line = G_paint(lcb, J.obj(("color", "#940e0e"), ("name", "LongCycleBandBottom")))
    def _f3(t=J.undefined, b=J.undefined, *_args):
        return J.div(J.add(t, b), 2)
    G_paint(G_for_every(lct, lcb, _f3), J.obj(("color", "red"), ("name", "LongCycleMedian"), ("style", "line")))
    G_fill(sct_line, scb_line, "green", 0.1)
    G_fill(mct_line, mcb_line, "blue", 0.1)
    G_fill(lct_line, lcb_line, "red", 0.1)
    def _f4(_low=J.undefined, _scb=J.undefined, _mcb=J.undefined, _lcb=J.undefined, *_args):
        return (_low if (((J.lt(_low, _scb) and J.lt(_low, _mcb)) and J.gt(_low, _lcb)) and J.gt(_scb, _mcb)) else None)
    shortTriangleBottom = G_for_every(G_low, scb, mcb, lcb, _f4)
    def _f5(_low=J.undefined, _scb=J.undefined, _mcb=J.undefined, _lcb=J.undefined, *_args):
        return (_low if (((J.lt(_low, _scb) and J.lt(_low, _mcb)) and J.gt(_low, _lcb)) and J.lt(_scb, _mcb)) else None)
    mediumTriangleBottom = G_for_every(G_low, scb, mcb, lcb, _f5)
    def _f6(_low=J.undefined, _lcb=J.undefined, _scb=J.undefined, _mcb=J.undefined, *_args):
        return (_low if ((J.lt(_low, _lcb) and J.lt(_low, _scb)) and J.lt(_low, _mcb)) else None)
    longTriangleBottom = G_for_every(G_low, lcb, scb, mcb, _f6)
    def _f7(_high=J.undefined, _sct=J.undefined, _mct=J.undefined, _lct=J.undefined, *_args):
        return (_high if (((J.gt(_high, _sct) and J.gt(_high, _mct)) and J.lt(_high, _lct)) and J.lt(_sct, _mct)) else None)
    shortTriangleTop = G_for_every(G_high, sct, mct, lct, _f7)
    def _f8(_high=J.undefined, _sct=J.undefined, _mct=J.undefined, _lct=J.undefined, *_args):
        return (_high if (((J.gt(_high, _sct) and J.gt(_high, _mct)) and J.lt(_high, _lct)) and J.gt(_sct, _mct)) else None)
    mediumTriangleTop = G_for_every(G_high, sct, mct, lct, _f8)
    def _f9(_high=J.undefined, _lct=J.undefined, _sct=J.undefined, _mct=J.undefined, *_args):
        return (_high if ((J.gt(_high, _lct) and J.gt(_high, _sct)) and J.gt(_high, _mct)) else None)
    longTriangleTop = G_for_every(G_high, lct, sct, mct, _f9)
    def _f10(value=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "arrow_up") if (value is not None) else None)
    shortArrowBottom = J.get(shortTriangleBottom, "map")(_f10)
    def _f11(value=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "arrow_up") if (value is not None) else None)
    mediumArrowBottom = J.get(mediumTriangleBottom, "map")(_f11)
    def _f12(value=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "arrow_up") if (value is not None) else None)
    longArrowBottom = J.get(longTriangleBottom, "map")(_f12)
    def _f13(value=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "arrow_down") if (value is not None) else None)
    shortArrowTop = J.get(shortTriangleTop, "map")(_f13)
    def _f14(value=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "arrow_down") if (value is not None) else None)
    mediumArrowTop = J.get(mediumTriangleTop, "map")(_f14)
    def _f15(value=J.undefined, *_args):
        return (J.get(J.get(G_constants, "icons"), "arrow_down") if (value is not None) else None)
    longArrowTop = J.get(longTriangleTop, "map")(_f15)
    G_paint(shortArrowBottom, J.obj(("style", "labels_below"), ("color", "green"), ("name", "Short Triangle Bottom"), ("fontSize", 20)))
    G_paint(mediumArrowBottom, J.obj(("style", "labels_below"), ("color", "green"), ("name", "Medium Triangle Bottom"), ("fontSize", 20)))
    G_paint(longArrowBottom, J.obj(("style", "labels_below"), ("color", "green"), ("name", "Long Triangle Bottom"), ("fontSize", 20)))
    G_paint(shortArrowTop, J.obj(("style", "labels_above"), ("color", "red"), ("name", "Short Triangle Top"), ("fontSize", 20)))
    G_paint(mediumArrowTop, J.obj(("style", "labels_above"), ("color", "red"), ("name", "Medium Triangle Top"), ("fontSize", 20)))
    G_paint(longArrowTop, J.obj(("style", "labels_above"), ("color", "red"), ("name", "Long Triangle Top"), ("fontSize", 20)))


register_store_indicator(
    script,
    name='alma_channels_with_signals_TS',
    title='ALMA Channels with Signals',
    developer='Kodexius',
    url='https://trendspider.com/trading-tools-store/indicators/68e750-hurst-alma-channels-with-signals-kodexius/',
    position='price',
    inputs=[{'id': 'short_length', 'title': 'Short Length', 'type': 'number', 'default': 14}, {'id': 'medium_length', 'title': 'Medium Length', 'type': 'number', 'default': 30}, {'id': 'long_length', 'title': 'Long Length', 'type': 'number', 'default': 60}, {'id': 'short_multiplier', 'title': 'Short Multiplier', 'type': 'number', 'default': 2}, {'id': 'medium_multiplier', 'title': 'Medium Multiplier', 'type': 'number', 'default': 4}, {'id': 'long_multiplier', 'title': 'Long Multiplier', 'type': 'number', 'default': 8}, {'id': 'source', 'title': 'Source', 'type': 'select_wide', 'default': 'close', 'options': ['open', 'high', 'low', 'close', 'hl2', 'oc2', 'hlc3', 'ohlc4', 'wclose']}],
    outputs=['shortcyclebandtop', 'shortcyclebandbottom', 'shortcyclemedian', 'mediumcyclebandtop', 'mediumcyclebandbottom', 'mediumcyclemedian', 'longcyclebandtop', 'longcyclebandbottom', 'longcyclemedian', 'short_triangle_bottom', 'medium_triangle_bottom', 'long_triangle_bottom', 'short_triangle_top', 'medium_triangle_top', 'long_triangle_top'],
    signals=[],
    requires=[],
    parity='exact',
)
