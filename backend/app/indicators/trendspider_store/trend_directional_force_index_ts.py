"""
Trend Directional Force Index -- TrendSpider store indicator by James Chambers.

Registered as "trend_directional_force_index_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/trend-directional-force-index/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: ULP, syn_5m: ULP.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_describe_indicator = G["describe_indicator"]
    G_ema = G["ema"]
    G_highest = G["highest"]
    G_horizontal_line = G["horizontal_line"]
    G_hullma = G["hullma"]
    G_input = G["input"]
    G_paint = G["paint"]
    G_prices = G["prices"]
    G_sma = G["sma"]
    G_vwma = G["vwma"]
    G_wma = G["wma"]
    def tema(src=J.undefined, len=J.undefined, *_args):
        ema1 = G_ema(src, len)
        ema2 = G_ema(ema1, len)
        ema3 = G_ema(ema2, len)
        return J.add(J.sub(J.mul(3, ema1), J.mul(3, ema2)), ema3)
    def ma(mode=J.undefined, src=J.undefined, len=J.undefined, *_args):
        _t1 = mode
        if J.seq(_t1, "ema"):
            _t2 = 0
        elif J.seq(_t1, "wma"):
            _t2 = 1
        elif J.seq(_t1, "vwma"):
            _t2 = 2
        elif J.seq(_t1, "hull"):
            _t2 = 3
        elif J.seq(_t1, "tema"):
            _t2 = 4
        else:
            _t2 = 5
        _c3 = False
        for _once in (0,):
            if _t2 <= 0:
                return G_ema(src, len)
            if _t2 <= 1:
                return G_wma(src, len)
            if _t2 <= 2:
                return G_vwma(src, len)
            if _t2 <= 3:
                return G_hullma(src, len)
            if _t2 <= 4:
                return tema(src, len)
            if _t2 <= 5:
                return G_sma(src, len)
            pass
    def tdfi(*_args):
        def _f1(p=J.undefined, *_args):
            return J.mul(p, 1000)
        mma = ma(mmaMode, J.get(price, "map")(_f1), mmaLength)
        smma = ma(smmaMode, mma, smmaLength)
        def _f2(m=J.undefined, idx=J.undefined, *_args):
            return J.sub(m, (_t1 if J.truthy(_t1 := J.get(mma, J.sub(idx, 1))) else 0))
        impetmma = J.get(mma, "map")(_f2)
        def _f3(s=J.undefined, idx=J.undefined, *_args):
            return J.sub(s, (_t1 if J.truthy(_t1 := J.get(smma, J.sub(idx, 1))) else 0))
        impetsmma = J.get(smma, "map")(_f3)
        def _f4(m=J.undefined, idx=J.undefined, *_args):
            return J.get(G_Math, "abs")(J.sub(m, J.get(smma, idx)))
        divma = J.get(mma, "map")(_f4)
        def _f5(im=J.undefined, idx=J.undefined, *_args):
            return J.div(J.add(im, J.get(impetsmma, idx)), 2)
        averimpet = J.get(impetmma, "map")(_f5)
        def _f6(d=J.undefined, idx=J.undefined, *_args):
            return J.mul(J.get(G_Math, "pow")(d, 1), J.get(G_Math, "pow")(J.get(averimpet, idx), nLength))
        tdf = J.get(divma, "map")(_f6)
        highestTdf = G_highest(J.get(tdf, "map")(J.get(G_Math, "abs")), J.mul(lookback, nLength))
        def _f7(t=J.undefined, idx=J.undefined, *_args):
            return J.div(t, J.get(highestTdf, idx))
        return J.get(tdf, "map")(_f7)
    G_describe_indicator("Trend Directional Force Index - TDFI - v2", "lower")
    lookback = J.get(G_input, "number")("Lookback Period", 13)
    mmaLength = J.get(G_input, "number")("MMA Length", 13)
    smmaLength = J.get(G_input, "number")("SMMA Length", 13)
    nLength = J.get(G_input, "number")("N Length", 3)
    filterHigh = J.get(G_input, "number")("Filter High", 0.05)
    filterLow = J.get(G_input, "number")("Filter Low", (-0.05))
    mmaMode = J.get(G_input, "select")("MMA Type", "ema", J.JSArray(["ema", "wma", "vwma", "hull", "tema"]))
    smmaMode = J.get(G_input, "select")("SMMA Type", "ema", J.JSArray(["ema", "wma", "vwma", "hull", "tema"]))
    price = J.get(G_prices, "close")
    signal = tdfi()
    def _f1(s=J.undefined, *_args):
        return ("green" if J.gt(s, filterHigh) else ("red" if J.lt(s, filterLow) else "gray"))
    signalColor = J.get(signal, "map")(_f1)
    G_paint(signal, J.obj(("style", "line"), ("color", signalColor), ("thickness", 2), ("name", "TDFI")))
    G_paint(G_horizontal_line(filterHigh), J.obj(("color", "black"), ("name", "Filter High"), ("style", "line")))
    G_paint(G_horizontal_line(filterLow), J.obj(("color", "black"), ("name", "Filter Low"), ("style", "line")))
    def _f2(s=J.undefined, *_args):
        return (filterHigh if J.gt(s, filterHigh) else None)
    aboveFilter = J.get(signal, "map")(_f2)
    def _f3(s=J.undefined, *_args):
        return (filterLow if J.lt(s, filterLow) else None)
    belowFilter = J.get(signal, "map")(_f3)
    G_paint(aboveFilter, J.obj(("style", "column"), ("color", "rgba(0,255,0,0.1)")))
    G_paint(belowFilter, J.obj(("style", "column"), ("color", "rgba(255,0,0,0.1)")))


register_store_indicator(
    script,
    name='trend_directional_force_index_TS',
    title='Trend Directional Force Index',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/trend-directional-force-index/',
    position='lower',
    inputs=[{'id': 'lookback_period', 'title': 'Lookback Period', 'type': 'number', 'default': 13}, {'id': 'mma_length', 'title': 'MMA Length', 'type': 'number', 'default': 13}, {'id': 'smma_length', 'title': 'SMMA Length', 'type': 'number', 'default': 13}, {'id': 'n_length', 'title': 'N Length', 'type': 'number', 'default': 3}, {'id': 'filter_high', 'title': 'Filter High', 'type': 'number', 'default': 0.05}, {'id': 'filter_low', 'title': 'Filter Low', 'type': 'number', 'default': -0.05}, {'id': 'mma_type', 'title': 'MMA Type', 'type': 'select_wide', 'default': 'ema', 'options': ['ema', 'wma', 'vwma', 'hull', 'tema']}, {'id': 'smma_type', 'title': 'SMMA Type', 'type': 'select_wide', 'default': 'ema', 'options': ['ema', 'wma', 'vwma', 'hull', 'tema']}],
    outputs=['tdfi', 'filter_high', 'filter_low', 'line_5', 'line_6'],
    signals=[],
    requires=[],
    parity='aapl_d: ULP, syn_5m: ULP',
)
