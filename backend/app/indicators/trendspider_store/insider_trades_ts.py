"""
Insider Trades -- TrendSpider store indicator by Rock Regan.

Registered as "insider_trades_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/697812-insider-trades/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Intl = G["Intl"]
    G_String = G["String"]
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_isNaN = G["isNaN"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_parseInt = G["parseInt"]
    G_request = G["request"]
    G_time = G["time"]
    def pickTheme(_name=J.undefined, *_args):
        if J.seq(_name, "Steel + Cyan"):
            return J.obj(("panelBg", "rgba(29, 41, 61, 0.85)"), ("text", "#E5E7EB"), ("mutedText", "#CBD5E1"), ("headerBg", "#1D293D"), ("headerText", "#E5E7EB"), ("buy", "#00CBD6"), ("sell", "#FB7185"), ("award", "#D6C100"), ("other", "#A3A3A3"), ("border", "#22D3EE"), ("divider", "rgba(148, 163, 184, 0.35)"), ("buyHeaderBg", "#0B1220"), ("sellHeaderBg", "#0B1220"), ("awardHeaderBg", "#0B1220"), ("otherHeaderBg", "#0B1220"), ("sectionHeaderText", "#E5E7EB"))
        if J.seq(_name, "Monochrome + Accent"):
            return J.obj(("panelBg", "rgba(0, 0, 0, 0.92)"), ("text", "#E5E5E5"), ("mutedText", "#A3A3A3"), ("headerBg", "#0A0A0A"), ("headerText", "#FFB000"), ("buy", "#E5E5E5"), ("sell", "#E5E5E5"), ("award", "#E5E5E5"), ("other", "#A3A3A3"), ("border", "rgba(255, 176, 0, 0.75)"), ("divider", "rgba(255, 255, 255, 0.10)"), ("buyHeaderBg", "#111111"), ("sellHeaderBg", "#111111"), ("awardHeaderBg", "#111111"), ("otherHeaderBg", "#111111"), ("sectionHeaderText", "#FFB000"))
        return J.obj(("panelBg", "rgba(10, 12, 18, 0.88)"), ("text", "#E5E7EB"), ("mutedText", "#CBD5E1"), ("headerBg", "#100099"), ("headerText", "#FFFFFF"), ("buy", "#22C55E"), ("sell", "#EF4444"), ("award", "#F59E0B"), ("other", "#94A3B8"), ("border", "rgba(255, 255, 255, 0.750)"), ("divider", "rgba(148, 163, 184, 0.30)"), ("buyHeaderBg", "#111827"), ("sellHeaderBg", "#111827"), ("awardHeaderBg", "#111827"), ("otherHeaderBg", "#111827"), ("sectionHeaderText", "#FFFFFF"))
    def myFormatDateFromTimestamp(_timestamp=J.undefined, *_args):
        tsNum = G_parseInt(_timestamp)
        ms = (J.mul(tsNum, 1000) if J.le(J.get(G_String(tsNum), "length"), 10) else tsNum)
        moment = G_library("moment-timezone")
        return J.get(moment(ms), "format")("MM/DD/YYYY")
    def myNormalizeAction(_transaction=J.undefined, _action=J.undefined, *_args):
        t = J.get((_t1 if J.truthy(_t1 := _transaction) else ""), "toLowerCase")()
        a = J.get((_t2 if J.truthy(_t2 := _action) else ""), "toLowerCase")()
        if J.seq(t, "buy"):
            return "BUY"
        if J.seq(t, "sell"):
            return "SELL"
        if (J.seq(t, "award") or J.seq(a, "award")):
            return "AWARD"
        return "OTHER"
    def myDisplayActionText(t=J.undefined, *_args):
        if J.sne(J.get(t, "actionType"), "OTHER"):
            return J.get(t, "actionType")
        raw = J.get((_t1 if J.truthy(_t1 := (_t2 if J.truthy(_t2 := J.get(t, "transaction")) else J.get(t, "action"))) else "unknown"), "toUpperCase")()
        return raw
    def myGetDaysAgoTimestamp(_days=J.undefined, *_args):
        secsInDay = J.mul(J.mul(24, 60), 60)
        nowTs = J.get(G_time, J.sub(J.get(G_time, "length"), 1))
        return J.sub(nowTs, J.mul(_days, secsInDay))
    def padNum(_txt=J.undefined, _len=J.undefined, *_args):
        s_2 = G_String(("" if J.nullish(_t1 := _txt) else _t1))
        return J.get(s_2, "padStart")(_len, " ")
    def myActionCellByType(_actionType=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = None
        _textOverride = _t2
        txt = (_actionType if J.nullish(_t3 := _textOverride) else _t3)
        _t4 = _actionType
        if J.seq(_t4, "BUY"):
            _t5 = 0
        elif J.seq(_t4, "SELL"):
            _t5 = 1
        elif J.seq(_t4, "AWARD"):
            _t5 = 2
        else:
            _t5 = 3
        _c6 = False
        for _once in (0,):
            if _t5 <= 0:
                return myActionBuyCell(txt)
            if _t5 <= 1:
                return myActionSellCell(txt)
            if _t5 <= 2:
                return myActionAwardCell(txt)
            if _t5 <= 3:
                return myActionOtherCell(txt)
            pass
    def myMakeSectionRows(_actionType=J.undefined, *_args):
        rows = J.JSArray([])
        J.get(rows, "push")(J.obj(("cells", J.JSArray([myHeadCell("Date", "left"), myHeadCell("Name", "left"), myHeadCell("Position", "left"), myHeadCell("Action", "left"), myHeadCell("Shares", "right"), myHeadCell("Value", "right")]))))
        J.get(rows, "push")(J.obj(("cells", J.JSArray([MY_SEPARATOR]))))
        count = 0
        for t_2 in J.iter_of(myTransactions):
            if J.sne(J.get(t_2, "actionType"), _actionType):
                continue
            dateStr = myFormatDateFromTimestamp(J.get(t_2, "timestamp"))
            actionLabel = myDisplayActionText(t_2)
            volStr = padNum(myFormatLargeNumber(J.get(t_2, "volume")), maxSharesLen)
            valStr = padNum(J.add("$", myFormatLargeNumber(J.get(t_2, "netValue"))), maxValueLen)
            volCell = (myBuyNumCell(volStr) if J.seq(_actionType, "BUY") else (mySellNumCell(volStr) if J.seq(_actionType, "SELL") else (myAwardNumCell(volStr) if J.seq(_actionType, "AWARD") else myOtherNumCell(volStr))))
            valCell = (myBuyNumCell(valStr) if J.seq(_actionType, "BUY") else (mySellNumCell(valStr) if J.seq(_actionType, "SELL") else (myAwardNumCell(valStr) if J.seq(_actionType, "AWARD") else myOtherNumCell(valStr))))
            J.get(rows, "push")(J.obj(("cells", J.JSArray([myDateCell(dateStr), myValueCell(J.get(t_2, "owner_name"), "left"), myValueCell(J.get(t_2, "owner_title"), "left"), myActionCellByType(_actionType, actionLabel), volCell, valCell]))))
            count = J.inc(count)
        if (not J.truthy(count)):
            J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", J.template("No ", _actionType, " actions in the last ", myLookbackDays, " days")), ("colspan", 6), ("color", J.get(THEME, "mutedText")), ("padding", PAD_ROW), ("textAlign", "center"))]))))
        return rows
    def mySectionHeader(_label=J.undefined, _bg=J.undefined, _fg=J.undefined, *_args):
        return J.obj(("cells", J.JSArray([J.obj(("colspan", 6), ("text", J.template(_label)), ("color", _fg), ("background", _bg), ("padding", PAD_SEC), ("fontWeight", "bold"), ("textAlign", "center"))])))
    G_describe_indicator("Insider Trades", J.obj(("shortName", "\ud83d\udc33 Insiders")))
    myLookbackDays = J.get(G_input, "number")("Lookback Period (Days)", 14, J.obj(("min", 1)))
    myFontSize = J.get(G_input, "number")("Font Size", 12, J.obj(("min", 8), ("max", 30)))
    showAwards = J.get(G_input, "boolean")("Show AWARD section", True)
    showOther = J.get(G_input, "boolean")("Show OTHER section", True)
    themeName = J.get(G_input, "select")("Theme", "Steel + Cyan", J.JSArray(["Midnight Neon", "Steel + Cyan", "Monochrome + Accent"]))
    THEME = pickTheme(themeName)
    myInsiderData = J.get(G_request, "insider_trading")(J.get(G_current, "ticker"))
    G_assert((not J.truthy(J.get(myInsiderData, "error"))), J.template("Error fetching insider trading data: ", J.get(myInsiderData, "error")))
    def myFormatLargeNumber(_value=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = 0
        _decimals = _t2
        return ("—" if J.truthy(G_isNaN(_value)) else J.get(J.get(G_Intl, "NumberFormat")("en-US", J.obj(("notation", "compact"), ("maximumFractionDigits", _decimals))), "format")(_value))
    myLookbackTimestamp = myGetDaysAgoTimestamp(myLookbackDays)
    def _f2(t=J.undefined, *_args):
        return J.ge(J.get(t, "timestamp"), myLookbackTimestamp)
    def _f3(t=J.undefined, *_args):
        info = (_t1 if J.truthy(_t1 := J.chain_end(J.oget(J.get(myInsiderData, "insidersByCIK"), J.get(t, "insider")))) else J.obj())
        own = (_t2 if J.truthy(_t2 := J.chain_end(J.oget(J.get(myInsiderData, "ownershipByCIK"), J.get(t, "insider")))) else 0)
        return J.obj(("timestamp", J.get(t, "timestamp")), ("transaction", J.get(t, "transaction")), ("action", J.get(t, "action")), ("volume", J.get(t, "volume")), ("netValue", J.get(t, "netValue")), ("isGift", (_t3 if J.truthy(_t3 := J.get(t, "isGift")) else False)), ("owner_name", (_t4 if J.truthy(_t4 := J.get(info, "name")) else "Unknown")), ("owner_title", (_t5 if J.truthy(_t5 := J.chain_end(J.oget(J.get(info, "role"), "title"))) else "Unknown")), ("total_owned", own), ("actionType", myNormalizeAction(J.get(t, "transaction"), J.get(t, "action"))))
    def _f4(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(b, "timestamp"), J.get(a, "timestamp"))
    myTransactions = J.get(J.get(J.get((_t1 if J.truthy(_t1 := J.get(myInsiderData, "transactions")) else J.JSArray([])), "filter")(_f2), "map")(_f3), "sort")(_f4)
    hasAnyTransactions = J.gt(J.get(myTransactions, "length"), 0)
    maxSharesLen = 1
    maxValueLen = 1
    for t in J.iter_of(myTransactions):
        s = myFormatLargeNumber(J.get(t, "volume"))
        v = J.add("$", myFormatLargeNumber(J.get(t, "netValue")))
        if (J.truthy(s) and J.gt(J.get(s, "length"), maxSharesLen)):
            maxSharesLen = J.get(s, "length")
        if (J.truthy(v) and J.gt(J.get(v, "length"), maxValueLen)):
            maxValueLen = J.get(v, "length")
    PAD_HEAD = "1px 6px"
    PAD_ROW = "2px 6px"
    PAD_SEC = "2px 6px"
    def myHeadCell(_text=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = "left"
        _align = _t2
        return J.obj(("text", J.template(_text)), ("fontWeight", "bold"), ("color", J.get(THEME, "headerText")), ("padding", PAD_HEAD), ("textAlign", _align))
    def myValueCell(_text=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = "left"
        _align = _t2
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "text")), ("padding", PAD_ROW), ("textAlign", _align))
    def myDateCell(_text=J.undefined, *_args):
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "text")), ("padding", PAD_ROW), ("textAlign", "left"))
    def myBuyNumCell(_text=J.undefined, *_args):
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "buy")), ("padding", PAD_ROW), ("textAlign", "right"))
    def mySellNumCell(_text=J.undefined, *_args):
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "sell")), ("padding", PAD_ROW), ("textAlign", "right"))
    def myAwardNumCell(_text=J.undefined, *_args):
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "award")), ("padding", PAD_ROW), ("textAlign", "right"))
    def myOtherNumCell(_text=J.undefined, *_args):
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "other")), ("padding", PAD_ROW), ("textAlign", "right"))
    def myActionBuyCell(_text=J.undefined, *_args):
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "buy")), ("padding", PAD_ROW), ("fontWeight", "bold"), ("textAlign", "left"))
    def myActionSellCell(_text=J.undefined, *_args):
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "sell")), ("padding", PAD_ROW), ("fontWeight", "bold"), ("textAlign", "left"))
    def myActionAwardCell(_text=J.undefined, *_args):
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "award")), ("padding", PAD_ROW), ("fontWeight", "bold"), ("textAlign", "left"))
    def myActionOtherCell(_text=J.undefined, *_args):
        return J.obj(("text", J.template(_text)), ("color", J.get(THEME, "other")), ("padding", PAD_ROW), ("fontWeight", "bold"), ("textAlign", "left"))
    MY_SEPARATOR = J.obj(("text", ""), ("colspan", 6), ("borderBottom", J.template("1px solid ", J.get(THEME, "divider"))))
    overlayRows = J.JSArray([])
    J.get(overlayRows, "push")(J.obj(("cells", J.JSArray([J.obj(("colspan", 6), ("text", J.template(J.get(G_current, "ticker"), ": Insider Transactions (Last ", myLookbackDays, " Days)")), ("color", J.get(THEME, "headerText")), ("background", J.get(THEME, "headerBg")), ("padding", PAD_SEC), ("fontWeight", "bold"), ("textAlign", "center"), ("fontSize", J.add(myFontSize, 2)))]))))
    J.get(overlayRows, "push")(J.obj(("cells", J.JSArray([MY_SEPARATOR]))))
    if (not J.truthy(hasAnyTransactions)):
        J.get(overlayRows, "push")(J.obj(("cells", J.JSArray([J.obj(("colspan", 6), ("text", "NO INSIDER ACTIVITY DETECTED"), ("color", J.get(THEME, "mutedText")), ("padding", "6px 6px"), ("textAlign", "center"), ("fontWeight", "bold"))]))))
        G_paint_overlay("Insider Trades", J.obj(("position", "bottom_left"), ("order", "above_all")), J.obj(("fontSize", myFontSize), ("fontFamily", "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace"), ("background", J.get(THEME, "panelBg")), ("border", J.template("2px solid ", J.get(THEME, "border"))), ("rows", overlayRows)))
        return J.undefined
    myBuyRows = myMakeSectionRows("BUY")
    mySellRows = myMakeSectionRows("SELL")
    myAwardRows = myMakeSectionRows("AWARD")
    myOtherRows = myMakeSectionRows("OTHER")
    BUY_BG = (_t5 if J.truthy(_t5 := J.get(THEME, "buyHeaderBg")) else J.get(THEME, "buy"))
    SELL_BG = (_t6 if J.truthy(_t6 := J.get(THEME, "sellHeaderBg")) else J.get(THEME, "sell"))
    AWARD_BG = (_t7 if J.truthy(_t7 := J.get(THEME, "awardHeaderBg")) else J.get(THEME, "award"))
    OTHER_BG = (_t8 if J.truthy(_t8 := J.get(THEME, "otherHeaderBg")) else "#111111")
    SECTION_FG = (_t9 if J.truthy(_t9 := (_t10 if J.truthy(_t10 := J.get(THEME, "sectionHeaderText")) else J.get(THEME, "headerText"))) else J.get(THEME, "text"))
    J.get(overlayRows, "push")(mySectionHeader("BUY", BUY_BG, SECTION_FG))
    J.get(overlayRows, "push")(J.obj(("cells", J.JSArray([MY_SEPARATOR]))))
    J.get(overlayRows, "push")(*J.spread(myBuyRows))
    J.get(overlayRows, "push")(mySectionHeader("SELL", SELL_BG, SECTION_FG))
    J.get(overlayRows, "push")(J.obj(("cells", J.JSArray([MY_SEPARATOR]))))
    J.get(overlayRows, "push")(*J.spread(mySellRows))
    if J.truthy(showAwards):
        J.get(overlayRows, "push")(mySectionHeader("AWARD", AWARD_BG, SECTION_FG))
        J.get(overlayRows, "push")(J.obj(("cells", J.JSArray([MY_SEPARATOR]))))
        J.get(overlayRows, "push")(*J.spread(myAwardRows))
    if J.truthy(showOther):
        J.get(overlayRows, "push")(mySectionHeader("OTHER", OTHER_BG, SECTION_FG))
        J.get(overlayRows, "push")(J.obj(("cells", J.JSArray([MY_SEPARATOR]))))
        J.get(overlayRows, "push")(*J.spread(myOtherRows))
    G_paint_overlay("Insider Trades", J.obj(("position", "bottom_left"), ("order", "above_all")), J.obj(("fontSize", myFontSize), ("fontFamily", "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace"), ("background", J.get(THEME, "panelBg")), ("border", J.template("2px solid ", J.get(THEME, "border"))), ("rows", overlayRows)))


register_store_indicator(
    script,
    name='insider_trades_TS',
    title='Insider Trades',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/697812-insider-trades/',
    position='price',
    inputs=[{'id': 'lookback_period__days_', 'title': 'Lookback Period (Days)', 'type': 'number', 'default': 14}, {'id': 'font_size', 'title': 'Font Size', 'type': 'number', 'default': 12}, {'id': 'show_award_section', 'title': 'Show AWARD section', 'type': 'boolean', 'default': True}, {'id': 'show_other_section', 'title': 'Show OTHER section', 'type': 'boolean', 'default': True}, {'id': 'theme', 'title': 'Theme', 'type': 'select_wide', 'default': 'Steel + Cyan', 'options': ['Midnight Neon', 'Steel + Cyan', 'Monochrome + Accent']}],
    outputs=[],
    signals=[],
    requires=['insider_trading'],
    parity='exact',
)
