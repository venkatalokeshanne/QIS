"""
Sector, Industry, Market Cap & Change Metrics -- TrendSpider store indicator by James Chambers.

Registered as "sector_industry_market_cap_change_metrics_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/sector-industry-market-cap-change-metrics/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
exact.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Boolean = G["Boolean"]
    G_Intl = G["Intl"]
    G_Promise = G["Promise"]
    G_assert = G["assert"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_input = G["input"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    def calculateChange(currentClose=J.undefined, periodOpen=J.undefined, *_args):
        return (J.get(J.mul(J.div(J.sub(currentClose, periodOpen), periodOpen), 100), "toFixed")(2) if J.truthy(periodOpen) else "N/A")
    G_describe_indicator("Sector, Industry, Market Cap, & Change Metrics (Horizontal Layout)")
    showMarketCap = J.get(G_input, "boolean")("Show Market Cap", True)
    showDailyChange = J.get(G_input, "boolean")("Show Daily Change%", True)
    showWTDChange = J.get(G_input, "boolean")("Show WTD Change%", True)
    showMTDChange = J.get(G_input, "boolean")("Show MTD Change%", True)
    showYTDChange = J.get(G_input, "boolean")("Show YTD Change%", True)
    _t1 = J.iter_of(J.get(G_Promise, "all")(J.JSArray([J.get(G_request, "fundamental")(J.get(G_current, "ticker"), J.JSArray(["market_cap"])), J.get(G_request, "history")(J.get(G_current, "ticker"), "D"), J.get(G_request, "history")(J.get(G_current, "ticker"), "W"), J.get(G_request, "history")(J.get(G_current, "ticker"), "M"), J.get(G_request, "history")(J.get(G_current, "ticker"), "Y")])))
    fundamentals = (_t1[0] if 0 < len(_t1) else J.undefined)
    dailyHistory = (_t1[1] if 1 < len(_t1) else J.undefined)
    weeklyHistory = (_t1[2] if 2 < len(_t1) else J.undefined)
    monthlyHistory = (_t1[3] if 3 < len(_t1) else J.undefined)
    yearlyHistory = (_t1[4] if 4 < len(_t1) else J.undefined)
    def _f2(_p1=J.undefined, *_args):
        _t2 = J.require_object(_p1)
        data = J.get(_t2, "data")
        name = J.get(_t2, "name")
        G_assert((not J.truthy(J.get(data, "error"))), J.template("Error fetching ", name, ": ", J.get(data, "error")))
    J.get(J.JSArray([J.obj(("data", fundamentals), ("name", "fundamentals")), J.obj(("data", dailyHistory), ("name", "dailyHistory")), J.obj(("data", weeklyHistory), ("name", "weeklyHistory")), J.obj(("data", monthlyHistory), ("name", "monthlyHistory")), J.obj(("data", yearlyHistory), ("name", "yearlyHistory"))]), "forEach")(_f2)
    marketCap = (J.template("$", J.get(J.get(G_Intl, "NumberFormat")("en-US", J.obj(("notation", "compact"), ("maximumFractionDigits", 1))), "format")(J.get(J.get(J.get(fundamentals, "market_cap"), 0), "value"))) if J.truthy(J.chain_end(J.oget(J.get(J.get(fundamentals, "market_cap"), 0), "value"))) else "N/A")
    dailyOpen = J.get(J.get(dailyHistory, "open"), J.sub(J.get(J.get(dailyHistory, "open"), "length"), 1))
    weeklyOpen = J.get(J.get(weeklyHistory, "open"), J.sub(J.get(J.get(weeklyHistory, "open"), "length"), 1))
    monthlyOpen = J.get(J.get(monthlyHistory, "open"), J.sub(J.get(J.get(monthlyHistory, "open"), "length"), 1))
    yearlyOpen = J.get(J.get(yearlyHistory, "open"), J.sub(J.get(J.get(yearlyHistory, "open"), "length"), 1))
    latestClose = J.get(J.get(dailyHistory, "close"), J.sub(J.get(J.get(dailyHistory, "close"), "length"), 1))
    dailyChange = calculateChange(latestClose, dailyOpen)
    wtdChange = calculateChange(latestClose, weeklyOpen)
    mtdChange = calculateChange(latestClose, monthlyOpen)
    ytdChange = calculateChange(latestClose, yearlyOpen)
    def titleCell(text=J.undefined, *_args):
        return J.obj(("text", text), ("fontWeight", "bold"), ("color", "white"), ("background", "var(--background-color-highlight)"), ("padding", "5px 10px"))
    def valueCell(text=J.undefined, color=J.undefined, *_args):
        return J.obj(("text", text), ("color", color), ("padding", "5px 10px"))
    rows = J.JSArray([J.obj(("cells", J.get(J.JSArray([titleCell("Sector / Industry"), valueCell(J.template(J.get(G_current, "sector"), " / ", J.get(G_current, "industry")), "var(--text-color)"), (titleCell("Market Cap") if J.truthy(showMarketCap) else None), (valueCell(marketCap, "var(--text-color)") if J.truthy(showMarketCap) else None), (titleCell("Day%") if J.truthy(showDailyChange) else None), (valueCell(J.template(dailyChange, "%"), ("green" if J.gt(dailyChange, 0) else ("red" if J.lt(dailyChange, 0) else "var(--text-color)"))) if J.truthy(showDailyChange) else None), (titleCell("WTD%") if J.truthy(showWTDChange) else None), (valueCell(J.template(wtdChange, "%"), ("green" if J.gt(wtdChange, 0) else ("red" if J.lt(wtdChange, 0) else "var(--text-color)"))) if J.truthy(showWTDChange) else None), (titleCell("MTD%") if J.truthy(showMTDChange) else None), (valueCell(J.template(mtdChange, "%"), ("green" if J.gt(mtdChange, 0) else ("red" if J.lt(mtdChange, 0) else "var(--text-color)"))) if J.truthy(showMTDChange) else None), (titleCell("YTD%") if J.truthy(showYTDChange) else None), (valueCell(J.template(ytdChange, "%"), ("green" if J.gt(ytdChange, 0) else ("red" if J.lt(ytdChange, 0) else "var(--text-color)"))) if J.truthy(showYTDChange) else None)]), "filter")(G_Boolean)))])
    G_paint_overlay("Table", J.obj(("position", "top_right"), ("order", "above_all")), J.obj(("fontSize", 12), ("border", "1px solid var(--border-color)"), ("background", "var(--background-color)"), ("rows", rows)))


register_store_indicator(
    script,
    name='sector_industry_market_cap_change_metrics_TS',
    title='Sector, Industry, Market Cap & Change Metrics',
    developer='James Chambers',
    url='https://trendspider.com/trading-tools-store/indicators/sector-industry-market-cap-change-metrics/',
    position='price',
    inputs=[{'id': 'show_market_cap', 'title': 'Show Market Cap', 'type': 'boolean', 'default': True}, {'id': 'show_daily_change_', 'title': 'Show Daily Change%', 'type': 'boolean', 'default': True}, {'id': 'show_wtd_change_', 'title': 'Show WTD Change%', 'type': 'boolean', 'default': True}, {'id': 'show_mtd_change_', 'title': 'Show MTD Change%', 'type': 'boolean', 'default': True}, {'id': 'show_ytd_change_', 'title': 'Show YTD Change%', 'type': 'boolean', 'default': True}],
    outputs=[],
    signals=[],
    requires=['fundamental', 'history'],
    parity='exact',
)
