"""
Put/Call Ratio -- TrendSpider store indicator by TrendSpider.

Registered as "put_call_ratio_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/69b825-put-call-ratio/)
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
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_describe_indicator("Put/Call Ratio")
    optionsData = J.get(G_request, "options_data_for_all_expirations")(J.get(G_current, "ticker"), 30, J.JSArray(["oi"]), "all")
    G_assert((not J.truthy(J.get(optionsData, "error"))), J.template("Error fetching options data: ", J.get(optionsData, "error")))
    myTotalCallsOI = 0
    myTotalPutsOI = 0
    for myExpiration in J.iter_in(J.get(optionsData, "resultByExpiration")):
        myStrikesData = J.get(J.get(optionsData, "resultByExpiration"), myExpiration)
        for myStrike in J.iter_in(myStrikesData):
            myStrikeData = J.get(myStrikesData, myStrike)
            if (J.truthy(J.get(myStrikeData, "C")) and J.truthy(J.get(J.get(myStrikeData, "C"), "oi"))):
                myTotalCallsOI = J.add(myTotalCallsOI, J.get(J.get(myStrikeData, "C"), "oi"))
            if (J.truthy(J.get(myStrikeData, "P")) and J.truthy(J.get(J.get(myStrikeData, "P"), "oi"))):
                myTotalPutsOI = J.add(myTotalPutsOI, J.get(J.get(myStrikeData, "P"), "oi"))
    myTotal = J.add(myTotalCallsOI, myTotalPutsOI)
    myCallsPercent = (J.get(J.mul(J.div(myTotalCallsOI, myTotal), 100), "toFixed")(1) if J.gt(myTotal, 0) else 0)
    myPutsPercent = (J.get(J.mul(J.div(myTotalPutsOI, myTotal), 100), "toFixed")(1) if J.gt(myTotal, 0) else 0)
    myPutCallRatio = (J.get(J.div(myTotalPutsOI, myTotalCallsOI), "toFixed")(2) if J.gt(myTotalCallsOI, 0) else 0)
    G_paint_overlay("Chart", J.obj(("position", "bottom_left"), ("offset_x", 10), ("offset_y", 0)), J.obj(("rows", J.JSArray([J.undefined, J.obj(("cells", J.JSArray([J.obj(("textAlign", "center"), ("text", "Put/Call Ratio"), ("paddingBottom", 7), ("color", "var(--text-color)"))]))), J.obj(("cells", J.JSArray([J.obj(("chart", J.obj(("width", "80px"), ("height", "80px"), ("type", "doughnut"), ("options", J.obj(("plugins", J.obj(("legend", J.obj(("display", False), ("position", "inset"))), ("datalabels", J.obj(("display", True))))), ("cutout", "70%"))), ("data", J.obj(("labels", J.JSArray([J.template("Calls ", myCallsPercent, "%"), J.template("Puts ", myPutsPercent, "%")])), ("datasets", J.JSArray([J.obj(("data", J.JSArray([myTotalCallsOI, myTotalPutsOI])), ("backgroundColor", J.JSArray(["#12d962", "#ff4444"])), ("borderColor", J.JSArray(["#0fa84d", "#cc0000"])), ("borderWidth", 2), ("datalabels", J.obj(("display", False))))])))))))]))), J.obj(("cells", J.JSArray([J.obj(("position", "relative"), ("textAlign", "center"), ("top", (-55)), ("fontSize", 20), ("fontWeight", "bold"), ("text", myPutCallRatio), ("color", "var(--text-color)"))])))]))))


register_store_indicator(
    script,
    name='put_call_ratio_TS',
    title='Put/Call Ratio',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/69b825-put-call-ratio/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=['options_data_for_all_expirations'],
    parity='exact',
)
