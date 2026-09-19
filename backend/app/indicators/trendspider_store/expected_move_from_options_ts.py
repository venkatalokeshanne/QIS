"""
Expected Move from Options -- TrendSpider store indicator by TrendSpider.

Registered as "expected_move_from_options_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69b826-expected-move-from-options/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: both-error, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Math = G["Math"]
    G_Number = G["Number"]
    G_Object = G["Object"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_fill = G["fill"]
    G_input = G["input"]
    G_interpolate_sparse_series = G["interpolate_sparse_series"]
    G_library = G["library"]
    G_paint = G["paint"]
    G_paint_projection = G["paint_projection"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_describe_indicator("Expected Move from Options")
    if J.ne(J.get(G_current, "resolution"), "D"):
        raise J.js_throw("This indicator is only applicable to Daily time frame")
    myNumberOfExpirations = J.get(G_input, "number")("Number of Expirations", 10, J.obj(("min", 1), ("max", 30)))
    mySchedule = J.get(G_request, "options_schedule")(J.get(G_current, "ticker"))
    G_assert((J.gt(J.get(mySchedule, "length"), 0) if J.truthy(_t1 := (not J.truthy(J.get(mySchedule, "error")))) else _t1), "No options data available for this ticker")
    def _f2(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(J.get(a, "expiration"), "dte"), J.get(J.get(b, "expiration"), "dte"))
    mySortedExpirations = J.get(mySchedule, "sort")(_f2)
    myTargetExpirations = J.JSArray([])
    for myExp in J.iter_of(mySortedExpirations):
        if J.lt(J.get(myTargetExpirations, "length"), myNumberOfExpirations):
            J.get(myTargetExpirations, "push")(myExp)
    G_assert(J.gt(J.get(myTargetExpirations, "length"), 0), "Could not find suitable expirations")
    myAllOptionsData = J.get(G_request, "options_data_for_all_expirations")(J.get(G_current, "ticker"), 6, J.JSArray(["l", "a", "b"]), "all")
    G_assert((not J.truthy(J.get(myAllOptionsData, "error"))), J.add("Error fetching options data: ", J.get(myAllOptionsData, "error")))
    myCurrentPrice = J.get(J.get(myAllOptionsData, "underlyingSymbolQuote"), "lastPrice")
    binarySearch = G_library("binary-search-bounds")
    myExpectedMoves = J.JSArray([])
    for myExpiration in J.iter_of(myTargetExpirations):
        myExpirationCode = J.get(J.get(myExpiration, "expiration"), "code")
        myExpirationData = J.get(J.get(myAllOptionsData, "resultByExpiration"), myExpirationCode)
        if (not J.truthy(myExpirationData)):
            continue
        def _f3(a=J.undefined, b=J.undefined, *_args):
            return J.sub(a, b)
        myStrikes = J.get(J.get(J.get(G_Object, "keys")(myExpirationData), "map")(G_Number), "sort")(_f3)
        myAtmIndex = J.get(binarySearch, "gt")(myStrikes, myCurrentPrice)
        myAtmStrike = (J.get(myStrikes, J.sub(J.get(myStrikes, "length"), 1)) if J.ge(myAtmIndex, J.get(myStrikes, "length")) else J.get(myStrikes, myAtmIndex))
        myAtmData = J.get(myExpirationData, myAtmStrike)
        myCallPrice = (_t4 if J.truthy(_t4 := (_t5 if J.truthy(_t5 := (_t6 if J.truthy(_t6 := J.chain_end(J.oget(J.oget(myAtmData, "C"), "l"))) else J.chain_end(J.oget(J.oget(myAtmData, "C"), "a")))) else J.chain_end(J.oget(J.oget(myAtmData, "C"), "b")))) else 0)
        myPutPrice = (_t7 if J.truthy(_t7 := (_t8 if J.truthy(_t8 := (_t9 if J.truthy(_t9 := J.chain_end(J.oget(J.oget(myAtmData, "P"), "l"))) else J.chain_end(J.oget(J.oget(myAtmData, "P"), "a")))) else J.chain_end(J.oget(J.oget(myAtmData, "P"), "b")))) else 0)
        if (J.gt(myCallPrice, 0) and J.gt(myPutPrice, 0)):
            myExpectedMove = J.add(myCallPrice, myPutPrice)
            J.get(myExpectedMoves, "push")(J.obj(("dte", J.get(J.get(myExpiration, "expiration"), "dte")), ("move", myExpectedMove)))
    G_assert(J.gt(J.get(myExpectedMoves, "length"), 0), "Could not calculate expected moves from available options")
    myCurrentClose = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    myCurrentPriceLine = G_paint(G_series_of(myCurrentClose), J.obj(("style", "dotted"), ("color", "gray"), ("name", "Current Price")))
    def _f10(m=J.undefined, *_args):
        return J.get(m, "dte")
    myMaxDte = J.get(G_Math, "max")(*J.spread(J.get(myExpectedMoves, "map")(_f10)))
    myExpectedMoveHigh = G_series_of(None)
    myExpectedMoveLow = G_series_of(None)
    J.set(myExpectedMoveHigh, 0, myCurrentClose)
    J.set(myExpectedMoveLow, 0, myCurrentClose)
    for myMoveData in J.iter_of(myExpectedMoves):
        myDteIndex = J.get(myMoveData, "dte")
        if (J.ge(myDteIndex, 0) and J.le(myDteIndex, myMaxDte)):
            J.set(myExpectedMoveHigh, myDteIndex, J.add(myCurrentClose, J.get(myMoveData, "move")))
            J.set(myExpectedMoveLow, myDteIndex, J.sub(myCurrentClose, J.get(myMoveData, "move")))
    myExpectedMoveLow = G_interpolate_sparse_series(myExpectedMoveLow)
    myExpectedMoveHigh = G_interpolate_sparse_series(myExpectedMoveHigh)
    myCurrentPriceProjection = G_series_of(myCurrentClose)
    myUpperLine = G_paint_projection(myExpectedMoveHigh, J.obj(("color", "#81ce6f"), ("name", "Upper Expected Move")))
    myLowerLine = G_paint_projection(myExpectedMoveLow, J.obj(("color", "#d13232"), ("name", "Lower Expected Move")))
    myMiddleLine = G_paint_projection(myCurrentPriceProjection, J.obj(("color", "gray"), ("style", "dotted"), ("hidden", True)))
    G_fill(myUpperLine, myMiddleLine, "#81ce6f", 0.15)
    G_fill(myMiddleLine, myLowerLine, "#d13232", 0.15)


register_store_indicator(
    script,
    name='expected_move_from_options_TS',
    title='Expected Move from Options',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69b826-expected-move-from-options/',
    position='price',
    inputs=[{'id': 'number_of_expirations', 'title': 'Number of Expirations', 'type': 'number', 'default': 10}],
    outputs=[],
    signals=[],
    requires=['options_data_for_all_expirations', 'options_schedule'],
    parity='aapl_d: both-error, syn_5m: both-error',
)
