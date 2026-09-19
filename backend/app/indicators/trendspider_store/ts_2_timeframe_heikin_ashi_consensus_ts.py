"""
2-Timeframe Heikin Ashi Consensus -- TrendSpider store indicator by James.

Registered as "2_timeframe_heikin_ashi_consensus_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6a918f-2-timeframe-heikin-ashi-consensus/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Promise = G["Promise"]
    G_assert = G["assert"]
    G_color_candles = G["color_candles"]
    G_constants = G["constants"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_land_points_onto_series = G["land_points_onto_series"]
    G_register_signal = G["register_signal"]
    G_request = G["request"]
    G_shift = G["shift"]
    G_time = G["time"]
    def getHeikinAshiState(timeframe=J.undefined, *_args):
        data = J.get(G_request, "history")(J.get(G_current, "ticker"), timeframe)
        G_assert((not J.truthy(J.get(data, "error"))), J.template("Error fetching ", timeframe, " timeframe data: ", J.get(data, "error")))
        haOpen = J.JSArray([])
        haClose = J.JSArray([])
        state = J.JSArray([])
        i = 0
        while J.lt(i, J.get(J.get(data, "close"), "length")):
            currentHaClose = J.div(J.add(J.add(J.add(J.get(J.get(data, "open"), i), J.get(J.get(data, "high"), i)), J.get(J.get(data, "low"), i)), J.get(J.get(data, "close"), i)), 4)
            currentHaOpen = (J.div(J.add(J.get(J.get(data, "open"), i), J.get(J.get(data, "close"), i)), 2) if J.seq(i, 0) else J.div(J.add(J.get(haOpen, J.sub(i, 1)), J.get(haClose, J.sub(i, 1))), 2))
            J.set(haOpen, i, currentHaOpen)
            J.set(haClose, i, currentHaClose)
            if J.gt(currentHaClose, currentHaOpen):
                J.set(state, i, 1)
            elif J.lt(currentHaClose, currentHaOpen):
                J.set(state, i, (-1))
            else:
                J.set(state, i, 0)
            i = J.inc(i)
        stateToUse = (state if J.truthy(allowRepainting) else G_shift(state, 1))
        landedState = G_land_points_onto_series(J.get(data, "time"), stateToUse, G_time, "le")
        return G_interpolate_sparse_series(landedState, "constant")
    G_describe_indicator("2-Timeframe Heikin Ashi Consensus", "price", J.obj(("shortName", "2TF HA Consensus"), ("description", "Colors chart candles based on Heikin Ashi direction across two selectable timeframes. Green = both bullish, Red = both bearish, Gray = mixed/neutral. IMPORTANT: Repainting Mode controls behavior. OFF - Confirmed Candles Only uses only fully completed candles from each selected timeframe and does not repaint. ON - Live (Repaints) uses currently forming candles, so candle colors and signals can change until those timeframe candles close.")))
    timeframe1 = J.get(G_input, "select")("Timeframe 1", "15", J.get(G_constants, "time_frames"))
    timeframe2 = J.get(G_input, "select")("Timeframe 2", "60", J.get(G_constants, "time_frames"))
    repaintMode = J.get(G_input, "select")("Repainting Mode", "OFF - Confirmed Candles Only", J.JSArray(["OFF - Confirmed Candles Only", "ON - Live (Repaints)"]))
    allowRepainting = J.seq(repaintMode, "ON - Live (Repaints)")
    _t1 = J.iter_of(J.get(G_Promise, "all")(J.JSArray([getHeikinAshiState(timeframe1), getHeikinAshiState(timeframe2)])))
    haState1 = (_t1[0] if 0 < len(_t1) else J.undefined)
    haState2 = (_t1[1] if 1 < len(_t1) else J.undefined)
    def _f2(state1=J.undefined, state2=J.undefined, *_args):
        if (J.seq(state1, 1) and J.seq(state2, 1)):
            return "green"
        if (J.seq(state1, (-1)) and J.seq(state2, (-1))):
            return "red"
        return "gray"
    candleColors = G_for_every(haState1, haState2, _f2)
    G_color_candles(candleColors)
    def _f3(state1=J.undefined, state2=J.undefined, *_args):
        return (J.seq(state2, 1) if J.truthy(_t1 := J.seq(state1, 1)) else _t1)
    bothGreen = G_for_every(haState1, haState2, _f3)
    def _f4(state1=J.undefined, state2=J.undefined, *_args):
        return (J.seq(state2, (-1)) if J.truthy(_t1 := J.seq(state1, (-1))) else _t1)
    bothRed = G_for_every(haState1, haState2, _f4)
    def _f5(state1=J.undefined, state2=J.undefined, *_args):
        return (not ((J.seq(state1, 1) and J.seq(state2, 1)) or (J.seq(state1, (-1)) and J.seq(state2, (-1)))))
    mixed = G_for_every(haState1, haState2, _f5)
    G_register_signal(bothGreen, "Both HA Green")
    G_register_signal(bothRed, "Both HA Red")
    G_register_signal(mixed, "HA Mixed")


register_store_indicator(
    script,
    name='2_timeframe_heikin_ashi_consensus_TS',
    title='2-Timeframe Heikin Ashi Consensus',
    developer='James',
    url='https://trendspider.com/trading-tools-store/indicators/6a918f-2-timeframe-heikin-ashi-consensus/',
    position='price',
    inputs=[{'id': 'timeframe_1', 'title': 'Timeframe 1', 'type': 'select_wide', 'default': '15', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'timeframe_2', 'title': 'Timeframe 2', 'type': 'select_wide', 'default': '60', 'options': ['1', '2', '3', '4', '5', '6', '10', '12', '15', '30', '45', '60', '65', '90', '120', '240', '1440', 'D', 'W', 'M', 'Q', 'Y']}, {'id': 'repainting_mode', 'title': 'Repainting Mode', 'type': 'select_wide', 'default': 'OFF - Confirmed Candles Only', 'options': ['OFF - Confirmed Candles Only', 'ON - Live (Repaints)']}],
    outputs=['cdl', 'both_ha_green', 'both_ha_red', 'ha_mixed'],
    signals=['both_ha_green', 'both_ha_red', 'ha_mixed'],
    requires=['history'],
    parity='exact',
)
