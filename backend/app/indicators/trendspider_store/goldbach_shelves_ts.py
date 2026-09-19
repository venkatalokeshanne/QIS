"""
Goldbach Shelves -- TrendSpider store indicator by M4RK4R4.

Registered as "goldbach_shelves_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a0fd-goldbach-shelves/)
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
    G_input = G["input"]
    G_open = G["open"]
    G_paint = G["paint"]
    G_paint_label_at_line = G["paint_label_at_line"]
    G_series_of = G["series_of"]
    G_describe_indicator("Goldbach Shelves", "price")
    expOptions = J.JSArray([3, 9, 27, 81, 243, 729, 2187, 6561, 19683, 59049, 177147])
    multiOptions = J.JSArray([0.01, 0.1, 1, 10, 100, 1000, 10000, 100000, 1000000])
    exp = J.get(G_input, "select")("PO3 Exponent", 243, expOptions)
    multi = J.get(G_input, "select")("Decimal Multiplier", 1, multiOptions)
    myPrevRl = None
    myPrevRh = None
    def calculatePO3Levels(_openPrice=J.undefined, *_args):
        nonlocal myPrevRl, myPrevRh
        myIp = J.mul(_openPrice, multi)
        myPo3 = exp
        myPo3R = J.mul(J.get(G_Math, "floor")(J.div(myIp, myPo3)), myPo3)
        myRl = J.div(myPo3R, multi)
        myRh = J.div(J.add(myPo3R, myPo3), multi)
        if ((myPrevRl is not None) and (myPrevRh is not None)):
            myMaxRef = J.get(G_Math, "max")(J.add(myPrevRh, J.mul(J.sub(myPrevRl, myPrevRh), (-0.111))), J.add(myPrevRh, J.mul(J.sub(myPrevRl, myPrevRh), 1.111)))
            myMinRef = J.get(G_Math, "min")(J.add(myPrevRh, J.mul(J.sub(myPrevRl, myPrevRh), (-0.111))), J.add(myPrevRh, J.mul(J.sub(myPrevRl, myPrevRh), 1.111)))
            if (J.gt(_openPrice, myMaxRef) or J.lt(_openPrice, myMinRef)):
                myRl = J.div(myPo3R, multi)
                myRh = J.div(J.add(myPo3R, myPo3), multi)
            else:
                myRl = myPrevRl
                myRh = myPrevRh
        myPrevRl = myRl
        myPrevRh = myRh
        return J.obj(("myRl", myRl), ("myRh", myRh))
    myColorGray = "gray"
    myColorDarkGreen = "darkgreen"
    myColorDarkRed = "darkred"
    myColorCrimson = "crimson"
    myLevels = J.JSArray([1.111, 1, 0.95, 0.71, 0.66, 0.61, 0.38, 0.33, 0.28, 0.05, 0, (-0.111)])
    myCurrentOpen = J.get(G_open, J.sub(J.get(G_open, "length"), 1))
    _t1 = J.require_object(calculatePO3Levels(myCurrentOpen))
    myCurrentRl = J.get(_t1, "myRl")
    myCurrentRh = J.get(_t1, "myRh")
    def calculatePrice(myRel=J.undefined, *_args):
        return J.add(myCurrentRh, J.mul(J.sub(myCurrentRl, myCurrentRh), J.sub(1, myRel)))
    def getCurrentShelf(myCurrentPrice_2=J.undefined, *_args):
        myTopShelfLow = calculatePrice(0.66)
        myMidShelfLow = calculatePrice(0.33)
        myBottomShelfLow = calculatePrice((-0.111))
        if J.ge(myCurrentPrice_2, myTopShelfLow):
            return "Top Shelf"
        elif J.ge(myCurrentPrice_2, myMidShelfLow):
            return "Mid Shelf"
        elif J.ge(myCurrentPrice_2, myBottomShelfLow):
            return "Bottom Shelf"
        else:
            return "Below Range"
    i = 0
    while J.lt(i, J.get(myLevels, "length")):
        myRel = J.get(myLevels, i)
        myPrice = calculatePrice(myRel)
        myLineThickness = (4 if (((J.seq(myRel, 0) or J.seq(myRel, 0.35)) or J.seq(myRel, 0.65)) or J.seq(myRel, 1)) else 1)
        myLineColor = J.undefined
        if (J.seq(myRel, 1.111) or J.seq(myRel, (-0.111))):
            myLineColor = myColorCrimson
        elif ((J.seq(myRel, 0.95) or J.seq(myRel, 0.61)) or J.seq(myRel, 0.28)):
            myLineColor = myColorDarkRed
        elif ((J.seq(myRel, 0.71) or J.seq(myRel, 0.38)) or J.seq(myRel, 0.05)):
            myLineColor = myColorDarkGreen
        else:
            myLineColor = myColorGray
        myPaintedLine = G_paint(G_series_of(myPrice), J.obj(("color", myLineColor), ("linewidth", myLineThickness), ("style", "ladder"), ("title", J.template("Level ", myRel))))
        myLabelText = J.undefined
        if J.seq(myRel, 0.95):
            myLabelText = "top shelf 0.95"
        elif J.seq(myRel, 0.71):
            myLabelText = "top shelf 0.71"
        elif J.seq(myRel, 0.61):
            myLabelText = "mid shelf 0.61"
        elif J.seq(myRel, 0.38):
            myLabelText = "mid shelf 0.38"
        elif J.seq(myRel, 0.28):
            myLabelText = "bottom shelf 0.28"
        elif J.seq(myRel, 0.05):
            myLabelText = "bottom shelf 0.05"
        elif J.seq(myRel, (-0.111)):
            myLabelText = "-0.111"
        elif J.seq(myRel, 1.111):
            myLabelText = "1.111"
        else:
            myLabelText = J.get(myRel, "toFixed")(2)
        G_paint_label_at_line(myPaintedLine, J.sub(J.get(G_close, "length"), 1), myLabelText, J.obj(("color", myLineColor), ("vertical_align", "middle")))
        i = J.inc(i)
    myBottomPrice = calculatePrice((-0.111))
    myPo3Label = G_paint(G_series_of(myBottomPrice), J.obj(("color", myColorGray), ("linewidth", 1), ("style", "ladder"), ("title", "PO3 Label")))
    G_paint_label_at_line(myPo3Label, J.sub(J.get(G_close, "length"), 1), J.template("PO3: ", exp), J.obj(("color", myColorGray), ("vertical_align", "bottom")))
    myTopPrice = calculatePrice(1.111)
    myCurrentPrice = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    myCurrentShelf = getCurrentShelf(myCurrentPrice)
    myShelfLabel = G_paint(G_series_of(myTopPrice), J.obj(("color", myColorGray), ("linewidth", 1), ("style", "ladder"), ("title", "Current Shelf Label")))
    G_paint_label_at_line(myShelfLabel, J.sub(J.get(G_close, "length"), 1), J.template("Current: ", myCurrentShelf), J.obj(("color", myColorGray), ("vertical_align", "top")))


register_store_indicator(
    script,
    name='goldbach_shelves_TS',
    title='Goldbach Shelves',
    developer='M4RK4R4',
    url='https://trendspider.com/trading-tools-store/indicators/68a0fd-goldbach-shelves/',
    position='price',
    inputs=[{'id': 'po3_exponent', 'title': 'PO3 Exponent', 'type': 'select_wide', 'default': 243, 'options': [3, 9, 27, 81, 243, 729, 2187, 6561, 19683, 59049, 177147]}, {'id': 'decimal_multiplier', 'title': 'Decimal Multiplier', 'type': 'select_wide', 'default': 1, 'options': [0.01, 0.1, 1, 10, 100, 1000, 10000, 100000, 1000000]}],
    outputs=['line_1', 'line_2', 'line_3', 'line_4', 'line_5', 'line_6', 'line_7', 'line_8', 'line_9', 'line_10', 'line_11', 'line_12', 'line_13', 'line_14'],
    signals=[],
    requires=[],
    parity='exact',
)
