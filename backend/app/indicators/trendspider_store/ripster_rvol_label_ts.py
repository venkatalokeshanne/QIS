"""
Ripster RVol Label -- TrendSpider store indicator by Ripster G.

Registered as "ripster_rvol_label_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/6923c8-ripster-rvol-label/)
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
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_div = G["div"]
    G_for_every = G["for_every"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_mult = G["mult"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    G_shift = G["shift"]
    G_sma = G["sma"]
    G_volume = G["volume"]
    G_describe_indicator("Ripster RVol Label")
    volumeLength = J.get(G_input, "number")("Average Volume Length", 20, J.obj(("min", 1)))
    isIntradayTimeframe = (not J.truthy(G_isNaN(G_parseInt(J.get(G_current, "resolution")))))
    myAvgVolume = J.undefined
    myRvol = J.undefined
    myLabelString = J.undefined
    myBackgroundColor = J.undefined
    if J.truthy(isIntradayTimeframe):
        dailyData = J.get(G_request, "history")(J.get(G_current, "ticker"), "D")
        G_assert((not J.truthy(J.get(dailyData, "error"))), J.template("Error fetching daily data: ", J.get(dailyData, "error")))
        dailyAvgVolume = G_sma(G_shift(J.get(dailyData, "volume"), 1), volumeLength)
        dailyRvol = G_div(G_mult(J.get(dailyData, "volume"), 100), dailyAvgVolume)
        latestDailyVolume = J.get(J.get(dailyData, "volume"), J.sub(J.get(J.get(dailyData, "volume"), "length"), 1))
        latestDailyAvgVolume = J.get(dailyAvgVolume, J.sub(J.get(dailyAvgVolume, "length"), 1))
        latestDailyRvol = J.get(dailyRvol, J.sub(J.get(dailyRvol, "length"), 1))
        def formatVolume(vol=J.undefined, *_args):
            if J.ge(vol, 1000000):
                return J.add(J.get(J.div(vol, 1000000), "toFixed")(2), " M")
            elif J.ge(vol, 1000):
                return J.add(J.get(J.div(vol, 1000), "toFixed")(2), "k")
            else:
                return J.get(vol, "toFixed")(2)
        formattedVol = formatVolume(latestDailyVolume)
        formattedAvg = formatVolume(latestDailyAvgVolume)
        roundedRvol = J.get(J.get(J.get(G_Math, "round")(latestDailyRvol), "toString")(), "padStart")(3)
        labelText = J.template("Vol: ", formattedVol, "    |    Avg Vol: ", formattedAvg, "    |    RVol: ", roundedRvol, "%")
        backgroundColor = ("#FF9999" if J.le(latestDailyRvol, 20) else "#99FF99")
        G_paint_overlay("RVol Table", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", labelText), ("background", backgroundColor), ("padding", 5), ("fontFamily", "Arial, sans-serif"), ("color", "black"), ("borderRadius", "5px"), ("whiteSpace", "pre"), ("fontWeight", "bold"), ("fontSize", "14px"))])))]))))
    else:
        isApplicableTimeframe = J.get(J.JSArray(["D", "W", "M"]), "includes")(J.get(G_current, "resolution"))
        if J.truthy(isApplicableTimeframe):
            myAvgVolume = G_sma(G_shift(G_volume, 1), volumeLength)
            myRvol = G_div(G_mult(G_volume, 100), myAvgVolume)
            def formatVolume_2(vol=J.undefined, *_args):
                if J.ge(vol, 1000000):
                    return J.add(J.get(J.div(vol, 1000000), "toFixed")(2), " M")
                elif J.ge(vol, 1000):
                    return J.add(J.get(J.div(vol, 1000), "toFixed")(2), "k")
                else:
                    return J.get(vol, "toFixed")(2)
            def _f1(_v=J.undefined, _a=J.undefined, _r=J.undefined, *_args):
                formattedVol_2 = formatVolume_2(_v)
                formattedAvg_2 = formatVolume_2(_a)
                roundedRvol_2 = J.get(J.get(J.get(G_Math, "round")(_r), "toString")(), "padStart")(3)
                return J.template("Vol: ", formattedVol_2, "    |    Avg Vol: ", formattedAvg_2, "    |    RVol: ", roundedRvol_2, "%")
            myLabelString = G_for_every(G_volume, myAvgVolume, myRvol, _f1)
            def _f2(_r=J.undefined, *_args):
                return ("#FF9999" if J.le(_r, 20) else "#99FF99")
            myBackgroundColor = G_for_every(myRvol, _f2)
            G_paint_overlay("RVol Table", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.get(myLabelString, J.sub(J.get(myLabelString, "length"), 1))), ("background", J.get(myBackgroundColor, J.sub(J.get(myBackgroundColor, "length"), 1))), ("padding", 5), ("fontFamily", "Arial, sans-serif"), ("color", "black"), ("borderRadius", "5px"), ("whiteSpace", "pre"), ("fontWeight", "bold"), ("fontSize", "14px"))])))]))))
        else:
            G_paint_overlay("RVol Table", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("rows", J.JSArray([]))))


register_store_indicator(
    script,
    name='ripster_rvol_label_TS',
    title='Ripster RVol Label',
    developer='Ripster G',
    url='https://trendspider.com/trading-tools-store/indicators/6923c8-ripster-rvol-label/',
    position='price',
    inputs=[{'id': 'average_volume_length', 'title': 'Average Volume Length', 'type': 'number', 'default': 20}],
    outputs=[],
    signals=[],
    requires=['history'],
    parity='exact',
)
