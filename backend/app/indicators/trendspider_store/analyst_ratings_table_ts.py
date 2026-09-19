"""
Analyst Ratings Table -- TrendSpider store indicator by Rock Regan.

Registered as "analyst_ratings_table_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/68a9db-analyst-ratings-table/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Array = G["Array"]
    G_Date = G["Date"]
    G_Number = G["Number"]
    G_String = G["String"]
    G_assert = G["assert"]
    G_constants = G["constants"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    def getActionColor(actionRaw=J.undefined, *_args):
        a = J.get(G_String((_t1 if J.truthy(_t1 := actionRaw) else "")), "toLowerCase")()
        if J.truthy(J.get(a, "includes")("upgrade")):
            return "limegreen"
        if J.truthy(J.get(a, "includes")("downgrade")):
            return "crimson"
        if J.truthy(J.get(a, "includes")("confirm")):
            return NEUTRAL
        return "dodgerblue"
    def getTargetColorFromAction(actionRaw=J.undefined, *_args):
        base = getActionColor(actionRaw)
        _t1 = base
        if J.seq(_t1, "limegreen"):
            _t2 = 0
        elif J.seq(_t1, "crimson"):
            _t2 = 1
        elif J.seq(_t1, NEUTRAL):
            _t2 = 2
        elif J.seq(_t1, "dodgerblue"):
            _t2 = 3
        else:
            _t2 = 4
        _c3 = False
        for _once in (0,):
            if _t2 <= 0:
                return "#98fb98"
            if _t2 <= 1:
                return "#FC92A3"
            if _t2 <= 2:
                return "#ffd966"
            if _t2 <= 4:
                return "#87cefa"
            pass
    def formatDate(tsMs=J.undefined, *_args):
        return J.get(J.get(moment, "tz")(tsMs, TZ), "format")("MM/DD HH:mm")
    def getRankColor(rankRaw=J.undefined, *_args):
        rank = J.get(G_String((_t1 if J.truthy(_t1 := rankRaw) else "")), "toLowerCase")()
        if J.seq(rank, "buy"):
            return "limegreen"
        if J.seq(rank, "hold"):
            return NEUTRAL
        if J.seq(rank, "sell"):
            return "crimson"
        return "white"
    G_describe_indicator(" Analyst Ratings Table ")
    myFontSize = J.get(G_input, "number")("Font Size", 12, J.obj(("min", 8), ("max", 30)))
    lookbackDays = J.get(G_input, "number")("Lookback Days", 5, J.obj(("min", 1), ("max", 60)))
    useStriping = J.get(G_input, "boolean")("Enable Striping", False)
    moment = G_library("moment-timezone")
    TZ = "America/New_York"
    ratings = J.get(G_request, "analyst_ratings")(G_String(J.get(G_constants, "ticker")))
    G_assert(J.get(G_Array, "isArray")(ratings), J.template("Failed to load ratings: ", (_t1 if J.truthy(_t1 := J.chain_end(J.oget(ratings, "error"))) else "unknown error")))
    nowMs = J.get(G_Date, "now")()
    lookbackStart = J.get(J.get(J.get(moment, "tz")(nowMs, TZ), "startOf")("day"), "subtract")(J.sub(lookbackDays, 1), "days")
    def _f2(r=J.undefined, *_args):
        return J.obj(*J.obj_spread(r), ("tsMs", J.mul((_t1 if J.truthy(_t1 := G_Number(J.get(r, "timestamp"))) else 0), 1000)))
    def _f3(r=J.undefined, *_args):
        return (J.get(J.get(moment, "tz")(J.get(r, "tsMs"), TZ), "isSameOrAfter")(lookbackStart) if J.truthy(_t1 := J.gt(J.get(r, "tsMs"), 0)) else _t1)
    def _f4(a=J.undefined, b=J.undefined, *_args):
        return J.sub(J.get(b, "tsMs"), J.get(a, "tsMs"))
    recentRatings = J.get(J.get(J.get(ratings, "map")(_f2), "filter")(_f3), "sort")(_f4)
    NEUTRAL = "#ffd966"
    BG = "#251f2b"
    STRIPE1 = "#595959"
    STRIPE2 = "#363636"
    if J.seq(J.get(recentRatings, "length"), 0):
        G_paint_overlay("Analyst Ratings", J.obj(("position", "bottom_right"), ("order", "above_all")), J.obj(("fontSize", myFontSize), ("background", BG), ("border", J.template("1px solid #ffd966")), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("text", J.template("\ud83d\udd34 No analyst ratings in the last ", lookbackDays, " days for ", J.get(G_constants, "ticker"))), ("color", "white"), ("background", STRIPE2), ("padding", "6px 10px"))])))]))))
        return J.undefined
    rows = J.JSArray([J.obj(("cells", J.JSArray([J.obj(("colspan", 4), ("text", J.template("\ud83c\udff7️ ", J.get(G_constants, "ticker"), " Analyst Ratings (Last ", lookbackDays, " Days)")), ("fontWeight", "bold"), ("color", "orange"), ("textAlign", "center"), ("padding", "8px 12px"), ("fontSize", J.add(myFontSize, 1)), ("background", BG))]))), J.obj(("cells", J.JSArray([J.obj(("text", "Time"), ("fontWeight", "bold"), ("padding", "4px 8px"), ("color", "lightgray"), ("background", STRIPE2)), J.obj(("text", "Firm"), ("fontWeight", "bold"), ("padding", "4px 8px"), ("color", "lightgray"), ("background", STRIPE2)), J.obj(("text", "Action / Target"), ("fontWeight", "bold"), ("padding", "4px 8px"), ("color", "lightgray"), ("background", STRIPE2)), J.obj(("text", "Rank"), ("fontWeight", "bold"), ("padding", "4px 8px"), ("color", "lightgray"), ("background", STRIPE2))])))])
    i = 0
    while J.lt(i, J.get(recentRatings, "length")):
        r = J.get(recentRatings, i)
        stripe = ((STRIPE1 if J.seq(J.mod(i, 2), 0) else STRIPE2) if J.truthy(useStriping) else STRIPE2)
        tsStr = formatDate(J.get(r, "tsMs"))
        firm = (_t5 if J.truthy(_t5 := J.get(r, "analystCompany")) else "Unknown")
        action = J.get(G_String((_t6 if J.truthy(_t6 := J.get(r, "action")) else "")), "toUpperCase")()
        rankRaw = (_t7 if J.truthy(_t7 := J.get(r, "ratingCurrent")) else "N/A")
        actionColor = getActionColor(action)
        targetColor = getTargetColorFromAction(action)
        pt = (J.template("→ $", J.get(r, "pTarget")) if J.truthy(J.get(r, "pTarget")) else "")
        actionCellText = (J.template(action, " ", pt) if J.truthy(pt) else action)
        J.get(rows, "push")(J.obj(("cells", J.JSArray([J.obj(("text", tsStr), ("padding", "4px 8px"), ("color", "#E0E0E0"), ("background", stripe)), J.obj(("text", firm), ("padding", "4px 8px"), ("color", "white"), ("background", stripe)), J.obj(("text", actionCellText), ("padding", "4px 8px"), ("color", (targetColor if J.truthy(pt) else actionColor)), ("fontWeight", "bold"), ("background", stripe)), J.obj(("text", J.get(G_String(rankRaw), "toUpperCase")()), ("padding", "4px 8px"), ("color", getRankColor(rankRaw)), ("fontWeight", "bold"), ("background", stripe))]))))
        i = J.inc(i)
    G_paint_overlay("Analyst Ratings", J.obj(("position", "bottom_right"), ("order", "above_all")), J.obj(("fontSize", myFontSize), ("background", BG), ("border", J.template("1px solid #ffd966")), ("rows", rows)))


register_store_indicator(
    script,
    name='analyst_ratings_table_TS',
    title='Analyst Ratings Table',
    developer='Rock Regan',
    url='https://trendspider.com/trading-tools-store/indicators/68a9db-analyst-ratings-table/',
    position='price',
    inputs=[{'id': 'font_size', 'title': 'Font Size', 'type': 'number', 'default': 12}, {'id': 'lookback_days', 'title': 'Lookback Days', 'type': 'number', 'default': 5}, {'id': 'enable_striping', 'title': 'Enable Striping', 'type': 'boolean', 'default': False}],
    outputs=[],
    signals=[],
    requires=['analyst_ratings'],
    parity='exact',
)
