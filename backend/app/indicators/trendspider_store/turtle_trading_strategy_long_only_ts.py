"""
Turtle Trading Strategy (Long-Only) -- TrendSpider store indicator by TrendSpider.

Registered as "turtle_trading_strategy_long_only_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/689209-turtle-trading-strategy-long-only/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_assert = G["assert"]
    G_atr = G["atr"]
    G_close = G["close"]
    G_color_candles = G["color_candles"]
    G_describe_indicator = G["describe_indicator"]
    G_high = G["high"]
    G_highest = G["highest"]
    G_input = G["input"]
    G_low = G["low"]
    G_lowest = G["lowest"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_register_signal = G["register_signal"]
    G_series_of = G["series_of"]
    G_describe_indicator("Turtle Trading Strategy (Long-Only)", "price", J.obj(("mainColorInheritFrom", "system_2_exit___20_day_low_")))
    showSystem1 = J.get(G_input, "boolean")("Show System 1", True)
    showSystem2 = J.get(G_input, "boolean")("Show System 2", True)
    showAtrStop = J.get(G_input, "boolean")("Show ATR Stop", True)
    showPyramids = J.get(G_input, "boolean")("Show Pyramids", True)
    atrMult = J.get(G_input, "number")("ATR Stop Multiplier", 2, J.obj(("min", 0.1), ("max", 10)))
    sys1EntryColor = J.get(G_input, "color")("System 1 Entry Color", "#00FFFF")
    sys2EntryColor = J.get(G_input, "color")("System 2 Entry Color", "#0066CC")
    sys1ExitColor = J.get(G_input, "color")("System 1 Exit Color", "#FF6B6B")
    sys2ExitColor = J.get(G_input, "color")("System 2 Exit Color", "#9370DB")
    atrStopColor = J.get(G_input, "color")("ATR Stop Color", "#FF00FF")
    entryLen1 = 20
    entryLen2 = 55
    exitLen1 = 10
    exitLen2 = 20
    atrLen = 20
    pyramidStep = 0.5
    maxUnits = 4
    G_assert(J.ge(J.get(G_close, "length"), entryLen2), J.template("Need at least ", entryLen2, " bars for System 2 calculations"))
    state = J.obj(("inTrade", False), ("system", 0), ("entry", 0), ("stop", 0), ("units", 0), ("nextAdd", 0), ("lastTradeWinner", False))
    chan20Hi = G_highest(G_high, entryLen1)
    chan55Hi = G_highest(G_high, entryLen2)
    chan10Lo = G_lowest(G_low, exitLen1)
    chan20Lo = G_lowest(G_low, exitLen2)
    atrN = G_atr(atrLen)
    stopLine = G_series_of(None)
    candleColors = G_series_of(None)
    entryMarkers = G_series_of(None)
    exitMarkers = G_series_of(None)
    longBreakoutSignal = G_series_of(False)
    pyramidAddSignal = G_series_of(False)
    stopHitSignal = G_series_of(False)
    channelExitSignal = G_series_of(False)
    system1EntrySignal = G_series_of(False)
    system2EntrySignal = G_series_of(False)
    system1ExitSignal = G_series_of(False)
    system2ExitSignal = G_series_of(False)
    atrStopExitSignal = G_series_of(False)
    i = J.get(G_Math, "max")(entryLen2, atrLen)
    while J.lt(i, J.get(G_close, "length")):
        currentHigh = J.get(G_high, i)
        currentLow = J.get(G_low, i)
        currentClose = J.get(G_close, i)
        currentAtr = J.get(atrN, i)
        prevChan20Hi = J.get(chan20Hi, J.sub(i, 1))
        prevChan55Hi = J.get(chan55Hi, J.sub(i, 1))
        prevChan10Lo = J.get(chan10Lo, J.sub(i, 1))
        prevChan20Lo = J.get(chan20Lo, J.sub(i, 1))
        exitTriggered = False
        pyramidTriggered = False
        entryTriggered = False
        stopTriggered = False
        if J.truthy(J.get(state, "inTrade")):
            if J.le(currentLow, J.get(state, "stop")):
                exitTriggered = True
                stopTriggered = True
                J.set(exitMarkers, i, "ATR")
                J.set(candleColors, i, atrStopColor)
                J.set(stopHitSignal, i, True)
                J.set(atrStopExitSignal, i, True)
                J.set(state, "lastTradeWinner", J.gt(currentClose, J.get(state, "entry")))
            elif (J.seq(J.get(state, "system"), 1) and J.le(currentLow, prevChan10Lo)):
                exitTriggered = True
                J.set(exitMarkers, i, "S1X")
                J.set(candleColors, i, sys1ExitColor)
                J.set(channelExitSignal, i, True)
                J.set(system1ExitSignal, i, True)
                J.set(state, "lastTradeWinner", J.gt(currentClose, J.get(state, "entry")))
            elif (J.seq(J.get(state, "system"), 2) and J.le(currentLow, prevChan20Lo)):
                exitTriggered = True
                J.set(exitMarkers, i, "S2X")
                J.set(candleColors, i, sys2ExitColor)
                J.set(channelExitSignal, i, True)
                J.set(system2ExitSignal, i, True)
                J.set(state, "lastTradeWinner", J.gt(currentClose, J.get(state, "entry")))
            elif ((J.truthy(showPyramids) and J.lt(J.get(state, "units"), maxUnits)) and J.ge(currentHigh, J.get(state, "nextAdd"))):
                pyramidTriggered = True
                J.set(state, "units", J.add(J.get(state, "units"), 1))
                fillPrice = (J.get(G_open, J.add(i, 1)) if J.lt(J.add(i, 1), J.get(G_open, "length")) else J.get(state, "nextAdd"))
                J.set(state, "stop", J.sub(fillPrice, J.mul(atrMult, currentAtr)))
                J.set(state, "nextAdd", J.add(fillPrice, J.mul(pyramidStep, currentAtr)))
                J.set(entryMarkers, i, J.template("+", J.get(state, "units")))
                J.set(candleColors, i, (sys1EntryColor if J.seq(J.get(state, "system"), 1) else sys2EntryColor))
                J.set(pyramidAddSignal, i, True)
            if (not J.truthy(exitTriggered)):
                J.set(stopLine, i, J.get(state, "stop"))
            if J.truthy(exitTriggered):
                J.set(state, "inTrade", False)
                J.set(state, "system", 0)
                J.set(state, "entry", 0)
                J.set(state, "stop", 0)
                J.set(state, "units", 0)
                J.set(state, "nextAdd", 0)
        if ((not J.truthy(J.get(state, "inTrade"))) and (not J.truthy(exitTriggered))):
            if J.gt(currentHigh, prevChan55Hi):
                fillPrice_2 = (J.get(G_open, J.add(i, 1)) if J.lt(J.add(i, 1), J.get(G_open, "length")) else currentHigh)
                entryTriggered = True
                J.set(state, "inTrade", True)
                J.set(state, "system", 2)
                J.set(state, "entry", fillPrice_2)
                J.set(state, "stop", J.sub(fillPrice_2, J.mul(atrMult, currentAtr)))
                J.set(state, "units", 1)
                J.set(state, "nextAdd", J.add(fillPrice_2, J.mul(pyramidStep, currentAtr)))
                J.set(entryMarkers, i, "S2")
                J.set(candleColors, i, sys2EntryColor)
                J.set(longBreakoutSignal, i, True)
                J.set(system2EntrySignal, i, True)
            elif J.gt(currentHigh, prevChan20Hi):
                if (not J.truthy(J.get(state, "lastTradeWinner"))):
                    fillPrice_3 = (J.get(G_open, J.add(i, 1)) if J.lt(J.add(i, 1), J.get(G_open, "length")) else currentHigh)
                    entryTriggered = True
                    J.set(state, "inTrade", True)
                    J.set(state, "system", 1)
                    J.set(state, "entry", fillPrice_3)
                    J.set(state, "stop", J.sub(fillPrice_3, J.mul(atrMult, currentAtr)))
                    J.set(state, "units", 1)
                    J.set(state, "nextAdd", J.add(fillPrice_3, J.mul(pyramidStep, currentAtr)))
                    J.set(entryMarkers, i, "S1")
                    J.set(candleColors, i, sys1EntryColor)
                    J.set(longBreakoutSignal, i, True)
                    J.set(system1EntrySignal, i, True)
                else:
                    J.set(state, "lastTradeWinner", False)
            if J.truthy(entryTriggered):
                J.set(stopLine, i, J.get(state, "stop"))
        i = J.inc(i)
    G_paint((chan20Hi if J.truthy(showSystem1) else G_series_of(None)), J.obj(("name", "System 1 Entry (20‑day high)"), ("color", sys1EntryColor), ("style", "ladder")))
    G_paint((chan10Lo if J.truthy(showSystem1) else G_series_of(None)), J.obj(("name", "System 1 Exit  (10‑day low)"), ("color", sys1ExitColor), ("style", "ladder")))
    G_paint((chan55Hi if J.truthy(showSystem2) else G_series_of(None)), J.obj(("name", "System 2 Entry (55‑day high)"), ("color", sys2EntryColor), ("style", "ladder")))
    G_paint((chan20Lo if J.truthy(showSystem2) else G_series_of(None)), J.obj(("name", "System 2 Exit  (20‑day low)"), ("color", sys2ExitColor), ("style", "ladder")))
    G_paint((stopLine if J.truthy(showAtrStop) else G_series_of(None)), J.obj(("name", "ATR Stop Line"), ("color", atrStopColor), ("style", "ladder")))
    G_color_candles(candleColors)
    G_paint(entryMarkers, J.obj(("style", "labels_below"), ("color", "white"), ("backgroundColor", "transparent"), ("name", "Entry Markers")))
    G_paint(exitMarkers, J.obj(("style", "labels_above"), ("color", "white"), ("backgroundColor", "transparent"), ("name", "Exit Markers")))
    G_register_signal(pyramidAddSignal, "Turtle Pyramid Add")
    G_register_signal(system1EntrySignal, "System 1 Entry")
    G_register_signal(system2EntrySignal, "System 2 Entry")
    G_register_signal(system1ExitSignal, "System 1 Exit")
    G_register_signal(system2ExitSignal, "System 2 Exit")
    G_register_signal(atrStopExitSignal, "ATR Stop Exit")


register_store_indicator(
    script,
    name='turtle_trading_strategy_long_only_TS',
    title='Turtle Trading Strategy (Long-Only)',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/689209-turtle-trading-strategy-long-only/',
    position='price',
    inputs=[{'id': 'show_system_1', 'title': 'Show System 1', 'type': 'boolean', 'default': True}, {'id': 'show_system_2', 'title': 'Show System 2', 'type': 'boolean', 'default': True}, {'id': 'show_atr_stop', 'title': 'Show ATR Stop', 'type': 'boolean', 'default': True}, {'id': 'show_pyramids', 'title': 'Show Pyramids', 'type': 'boolean', 'default': True}, {'id': 'atr_stop_multiplier', 'title': 'ATR Stop Multiplier', 'type': 'number', 'default': 2}, {'id': 'system_1_entry_color', 'title': 'System 1 Entry Color', 'type': 'color', 'default': '#00FFFF'}, {'id': 'system_2_entry_color', 'title': 'System 2 Entry Color', 'type': 'color', 'default': '#0066CC'}, {'id': 'system_1_exit_color', 'title': 'System 1 Exit Color', 'type': 'color', 'default': '#FF6B6B'}, {'id': 'system_2_exit_color', 'title': 'System 2 Exit Color', 'type': 'color', 'default': '#9370DB'}, {'id': 'atr_stop_color', 'title': 'ATR Stop Color', 'type': 'color', 'default': '#FF00FF'}],
    outputs=['system_1_entry__20_day_high_', 'system_1_exit___10_day_low_', 'system_2_entry__55_day_high_', 'system_2_exit___20_day_low_', 'atr_stop_line', 'cdl', 'entry_markers', 'exit_markers', 'turtle_pyramid_add', 'system_1_entry', 'system_2_entry', 'system_1_exit', 'system_2_exit', 'atr_stop_exit'],
    signals=['turtle_pyramid_add', 'system_1_entry', 'system_2_entry', 'system_1_exit', 'system_2_exit', 'atr_stop_exit'],
    requires=[],
    parity='exact',
)
