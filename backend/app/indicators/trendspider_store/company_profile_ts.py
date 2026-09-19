"""
Company Profile -- TrendSpider store indicator by TrendSpider.

Registered as "company_profile_TS". Translated line-for-line from the script's
published JavaScript (https://trendspider.com/trading-tools-store/indicators/company-profile/)
by tools/ts_store/transpile.js; parity with TrendSpider's own engine:
aapl_d: OK, syn_5m: both-error.

Generated file -- regenerate with tools/ts_store/build_modules.py
rather than editing by hand.
"""

from app.indicators.trendspider_store._runtime import js as J
from app.indicators.trendspider_store._runtime.indicator import register_store_indicator

def script(G):
    G_Intl = G["Intl"]
    G_Math = G["Math"]
    G_Object = G["Object"]
    G_Promise = G["Promise"]
    G_assert = G["assert"]
    G_close = G["close"]
    G_current = G["current"]
    G_describe_indicator = G["describe_indicator"]
    G_isNaN = G["isNaN"]
    G_library = G["library"]
    G_paint_overlay = G["paint_overlay"]
    G_request = G["request"]
    G_series_of = G["series_of"]
    G_time = G["time"]
    G_time_of = G["time_of"]
    G_describe_indicator("Company profile")
    moment = G_library("moment-timezone")
    _t1 = J.iter_of(J.get(G_Promise, "all")(J.JSArray([J.get(G_request, "history")(J.get(G_current, "ticker"), "W"), J.get(G_request, "fundamental")(J.get(G_current, "ticker"), J.JSArray(["dividends_per_share", "pe_ratio_ttm", "revenue", "eps_basic", "market_cap", "shares_diluted_is", "pe_ratio_ttm"]), 20), J.get(G_request, "relative_performance")(J.get(G_current, "ticker"), "quarterly", "same_sector"), J.get(G_request, "relative_performance")(J.get(G_current, "ticker"), "quarterly", "same_mktcap"), J.get(G_request, "analyst_ratings")(J.get(G_current, "ticker")), J.get(G_request, "earnings")(J.get(G_current, "ticker"), J.obj(("filters", J.JSArray([J.obj(("field", "timestamp"), ("filter", "greater"), ("value", 0))])))), J.get(G_request, "insider_trading")(J.get(G_current, "ticker"))])))
    weeklyHistory = (_t1[0] if 0 < len(_t1) else J.undefined)
    fundamentals = (_t1[1] if 1 < len(_t1) else J.undefined)
    rpSector = (_t1[2] if 2 < len(_t1) else J.undefined)
    rpMktcap = (_t1[3] if 3 < len(_t1) else J.undefined)
    analysts = (_t1[4] if 4 < len(_t1) else J.undefined)
    earnings = (_t1[5] if 5 < len(_t1) else J.undefined)
    insider = (_t1[6] if 6 < len(_t1) else J.undefined)
    G_assert((not J.truthy(J.get(weeklyHistory, "error"))), J.template("Error fetching W data: ", J.get(weeklyHistory, "error")))
    G_assert((not J.truthy(J.get(fundamentals, "error"))), J.template("Error fetching fundamentals: ", J.get(fundamentals, "error")))
    G_assert((not J.truthy(J.get(rpSector, "error"))), J.template("Error fetching rpSector: ", J.get(rpSector, "error")))
    G_assert((not J.truthy(J.get(rpMktcap, "error"))), J.template("Error fetching rpMktcap: ", J.get(rpMktcap, "error")))
    G_assert((not J.truthy(J.get(analysts, "error"))), J.template("Error fetching analysts: ", J.get(analysts, "error")))
    G_assert((not J.truthy(J.get(earnings, "error"))), J.template("Error fetching earnings: ", J.get(earnings, "error")))
    G_assert((not J.truthy(J.get(insider, "error"))), J.template("Error fetching insider_trading: ", J.get(insider, "error")))
    range52Wk = J.obj(("high", J.get(G_Math, "max")(*J.spread(J.get(J.get(weeklyHistory, "high"), "slice")((-52))))), ("low", J.get(G_Math, "min")(*J.spread(J.get(J.get(weeklyHistory, "low"), "slice")((-52))))))
    lastPrice = J.get(G_close, J.sub(J.get(G_close, "length"), 1))
    def _f2(result=J.undefined, dataPoint=J.undefined, *_args):
        return J.add(result, J.get(dataPoint, "value"))
    divYield = J.div(J.get(J.get(J.get(fundamentals, "dividends_per_share"), "slice")(0, 4), "reduce")(_f2, 0), lastPrice)
    def currentFundamental(metricId=J.undefined, *_args):
        return (J.get(J.get(J.get(fundamentals, metricId), 0), "value") if J.truthy(J.get(J.get(fundamentals, metricId), 0)) else J.undefined)
    def lastOf(series=J.undefined, *_args):
        return J.get(J.get(series, J.sub(J.get(series, "length"), 1)), 1)
    def headCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("fontWeight", "bold"), ("color", "var(--text-color)"), ("padding", "1px 7px"))
    def valueCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("color", "var(--text-color)"), ("padding", "3px 7px"))
    def rsCell(rank=J.undefined, *_args):
        return J.obj(("text", J.template(rank)), ("color", ("green" if J.gt(rank, 85) else ("red" if J.lt(rank, 50) else "var(--text-color)"))), ("padding", "3px 7px"))
    def leftTitleCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("fontWeight", "bold"), ("color", "var(--text-color)"), ("padding", "1px 7px"), ("width", "65%"))
    def rightValueCell(text=J.undefined, *_args):
        return J.obj(("text", J.template(text)), ("color", "var(--text-color)"), ("textAlign", "right"), ("padding", "1px 7px"))
    def titleValueRow(title=J.undefined, value=J.undefined, *_args):
        return J.obj(("cells", J.JSArray([leftTitleCell(title), rightValueCell(value)])))
    epsDataPoints = J.get(J.get(J.get(fundamentals, "eps_basic"), "reverse")(), "slice")((-12))
    pastEPSDataPoints = J.get(J.JSArray([*J.spread(G_series_of(J.obj(("value", None)))), *J.spread(J.get(fundamentals, "eps_basic"))]), "slice")((-16), (-4))
    def _f3(record=J.undefined, *_args):
        return J.template("Q", J.get(record, "quarter"), "'", J.mod(J.get(record, "year"), 100))
    epsLabels = J.get(epsDataPoints, "map")(_f3)
    def _f4(record=J.undefined, *_args):
        return J.get(record, "value")
    def _f5(record=J.undefined, *_args):
        return J.get(record, "value")
    def _f6(record=J.undefined, *_args):
        return J.get(record, "value")
    def _f7(record=J.undefined, *_args):
        return J.get(record, "value")
    epsRange = J.sub(J.get(G_Math, "max")(*J.spread(J.get(epsDataPoints, "map")(_f4)), *J.spread(J.get(pastEPSDataPoints, "map")(_f5))), J.get(G_Math, "min")(*J.spread(J.get(epsDataPoints, "map")(_f6)), *J.spread(J.get(pastEPSDataPoints, "map")(_f7))))
    revDataPoints = J.get(J.get(J.get(fundamentals, "revenue"), "reverse")(), "slice")((-12))
    pastRevDataPoints = J.get(J.JSArray([*J.spread(G_series_of(J.obj(("value", None)))), *J.spread(J.get(fundamentals, "revenue"))]), "slice")((-16), (-4))
    def _f8(record=J.undefined, *_args):
        return J.template("Q", J.get(record, "quarter"), "'", J.mod(J.get(record, "year"), 100))
    revLabels = J.get(revDataPoints, "map")(_f8)
    def _f9(record=J.undefined, *_args):
        return J.get(record, "value")
    def _f10(record=J.undefined, *_args):
        return J.get(record, "value")
    def _f11(record=J.undefined, *_args):
        return J.get(record, "value")
    def _f12(record=J.undefined, *_args):
        return J.get(record, "value")
    revRange = J.sub(J.get(G_Math, "max")(*J.spread(J.get(revDataPoints, "map")(_f9)), *J.spread(J.get(pastRevDataPoints, "map")(_f10))), J.get(G_Math, "min")(*J.spread(J.get(revDataPoints, "map")(_f11)), *J.spread(J.get(pastRevDataPoints, "map")(_f12))))
    def _f13(record=J.undefined, *_args):
        return J.JSArray([J.get(record, "analystPerson"), J.get(record, "ratingCurrent")])
    currentRatingPerPerson = J.get(G_Object, "fromEntries")(J.get(analysts, "map")(_f13))
    def _f14(result=J.undefined, person=J.undefined, *_args):
        rating = J.get(currentRatingPerPerson, person)
        J.set(result, rating, J.add(J.get(result, rating), 1))
        return result
    currentRatingsCount = J.get(J.get(G_Object, "keys")(currentRatingPerPerson), "reduce")(_f14, J.obj(("buy", 0), ("sell", 0), ("hold", 0)))
    def formatLargeNumber(value=J.undefined, _p1=J.undefined, *_args):
        _t2 = _p1
        if _t2 is J.undefined:
            _t2 = 0
        decimals = _t2
        return ("—" if J.truthy(G_isNaN(value)) else J.get(J.get(G_Intl, "NumberFormat")("en-US", J.obj(("notation", "compact"), ("maximumFractionDigits", decimals))), "format")(value))
    marketCap = J.template("$", formatLargeNumber(currentFundamental("market_cap")))
    sharesOutstanding = formatLargeNumber(currentFundamental("shares_diluted_is"))
    def _f15(record=J.undefined, *_args):
        return J.get(record, "isFuture")
    futureEarnings = J.get(earnings, "filter")(_f15)
    def _f16(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(cur, "eps_est"))
    nextFourQuartersEpsEst = J.get(J.get(futureEarnings, "slice")(0, 4), "reduce")(_f16, 0)
    forwardPe = (J.get(J.div(J.get(G_close, J.sub(J.get(G_close, "length"), 1)), nextFourQuartersEpsEst), "toFixed")(2) if J.truthy(nextFourQuartersEpsEst) else "—")
    def _f17(record=J.undefined, *_args):
        return J.get(record, "value")
    peRatioValues = J.get(J.get(J.get(fundamentals, "pe_ratio_ttm"), "slice")(0, 20), "map")(_f17)
    peRatioMax = J.get(J.get(G_Math, "max")(*J.spread(peRatioValues)), "toFixed")(1)
    peRatioMin = J.get(J.get(G_Math, "min")(*J.spread(peRatioValues)), "toFixed")(1)
    def _f18(record=J.undefined, *_args):
        return (not J.truthy(J.get(record, "isFuture")))
    def _f19(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(cur, "eps"))
    thisYearEarnings = J.get(J.get(J.get(earnings, "filter")(_f18), "slice")((-4)), "reduce")(_f19, 0)
    def _f20(record=J.undefined, *_args):
        return (not J.truthy(J.get(record, "isFuture")))
    def _f21(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(cur, "eps"))
    previousYearEarnings = J.get(J.get(J.get(earnings, "filter")(_f20), "slice")((-8), (-4)), "reduce")(_f21, 0)
    epsGrowth = J.get(J.div(J.mul(100, J.sub(thisYearEarnings, previousYearEarnings)), previousYearEarnings), "toFixed")(2)
    def _f23(id=J.undefined, *_args):
        return J.ne(J.get(J.get(J.get(J.get(insider, "insidersByCIK"), id), "role"), "type"), "10_p_owner")
    ownerIds = J.get(J.get(G_Object, "keys")((_t22 if J.truthy(_t22 := J.get(insider, "insidersByCIK")) else J.obj())), "filter")(_f23)
    def _f24(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(J.get(insider, "ownershipByCIK"), cur))
    sharesInsidersOwn = J.get(ownerIds, "reduce")(_f24, 0)
    mgmtOwnership = J.template(J.get(J.div(J.mul(100, sharesInsidersOwn), currentFundamental("shares_diluted_is")), "toFixed")(2), "%")
    currentYear = J.get(G_time_of(J.get(G_time, J.sub(J.get(G_time, "length"), 1))), "year")
    def _f25(quarter=J.undefined, *_args):
        return J.eq(J.get(quarter, "period_year"), J.sub(currentYear, 1))
    previousYearEarningsQuarters = J.get(earnings, "filter")(_f25)
    def _f26(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(cur, "eps"))
    previousYearEps = formatLargeNumber(J.get(previousYearEarningsQuarters, "reduce")(_f26, 0), 2)
    def _f27(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(cur, "revenue"))
    previousYearRevenue = formatLargeNumber(J.get(previousYearEarningsQuarters, "reduce")(_f27, 0), 1)
    def _f28(quarter=J.undefined, *_args):
        return ((not J.truthy(J.get(quarter, "isFuture"))) if J.truthy(_t1 := J.eq(J.get(quarter, "period_year"), currentYear)) else _t1)
    currentYearPastQuarters = J.get(earnings, "filter")(_f28)
    def _f29(quarter=J.undefined, *_args):
        return (J.get(quarter, "isFuture") if J.truthy(_t1 := J.eq(J.get(quarter, "period_year"), currentYear)) else _t1)
    currentYearFutureQuarters = J.get(earnings, "filter")(_f29)
    def _f30(quarter=J.undefined, *_args):
        return (J.nullish(J.get(quarter, "eps_est")))
    numberOfFutureQuartersWithoutEpsEstimate = J.get(J.get(currentYearFutureQuarters, "filter")(_f30), "length")
    def _f31(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(cur, "eps"))
    currentYearPastQuartersTotalEps = J.get(currentYearPastQuarters, "reduce")(_f31, 0)
    def _f32(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(cur, "eps_est"))
    currentYearFutureQuartersTotalEpsEst = J.get(currentYearFutureQuarters, "reduce")(_f32, 0)
    currentYearEpsEst = ("—" if J.gt(numberOfFutureQuartersWithoutEpsEstimate, 0) else formatLargeNumber(J.add(currentYearPastQuartersTotalEps, currentYearFutureQuartersTotalEpsEst), 2))
    def _f33(quarter=J.undefined, *_args):
        return (J.nullish(J.get(quarter, "revenue_est")))
    numberOfFutureQuartersWithoutRevenueEstimate = J.get(J.get(currentYearFutureQuarters, "filter")(_f33), "length")
    def _f34(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(cur, "revenue"))
    currentYearPastQuartersTotalRevenue = J.get(currentYearPastQuarters, "reduce")(_f34, 0)
    def _f35(acc=J.undefined, cur=J.undefined, *_args):
        return J.add(acc, J.get(cur, "revenue_est"))
    currentYearFutureQuartersTotalRevenueEst = J.get(currentYearFutureQuarters, "reduce")(_f35, 0)
    currentYearRevenueEst = ("—" if J.gt(numberOfFutureQuartersWithoutRevenueEstimate, 0) else formatLargeNumber(J.add(currentYearPastQuartersTotalRevenue, currentYearFutureQuartersTotalRevenueEst), 2))
    def _f36(record=J.undefined, *_args):
        return J.get(record, "isFuture")
    nextEarnings = J.get(earnings, "find")(_f36)
    DAYS_IN_SECONDS = J.mul(J.mul(24, 60), 60)
    daysUntilNextEarnings = J.get(G_Math, "floor")(J.div(J.sub(J.get(nextEarnings, "timestamp"), J.get(G_time, J.sub(J.get(G_time, "length"), 1))), DAYS_IN_SECONDS))
    def _f37(record=J.undefined, index=J.undefined, *_args):
        return ("green" if J.gt(J.get(record, "value"), J.get(J.get(pastRevDataPoints, index), "value")) else "red")
    def _f38(record=J.undefined, *_args):
        return J.get(record, "value")
    def _f39(record=J.undefined, *_args):
        return J.get(record, "value")
    revenueChartDefinition = J.obj(("width", "250px"), ("height", "80px"), ("type", "line"), ("options", J.obj(("scales", J.obj(("y", J.obj(("ticks", J.obj(("format", "0a"), ("stepSize", J.div(revRange, 3)), ("autoSkip", False))), ("position", "right"))), ("x", J.obj(("ticks", J.obj(("display", False))))))), ("plugins", J.obj(("legend", J.obj(("display", False))))))), ("data", J.obj(("labels", revLabels), ("datasets", J.JSArray([J.obj(("label", "Rev"), ("borderColor", "var(--text-color)"), ("pointBorderWidth", 0), ("borderWidth", 1), ("backgroundColor", J.get(revDataPoints, "map")(_f37)), ("data", J.get(revDataPoints, "map")(_f38))), J.obj(("label", "Prev.Rev"), ("backgroundColor", "silver"), ("borderColor", "var(--border-color)"), ("pointBorderWidth", 0), ("borderWidth", 0.3), ("data", J.get(pastRevDataPoints, "map")(_f39)))])))))
    def _f40(record=J.undefined, index=J.undefined, *_args):
        return ("green" if J.gt(J.get(record, "value"), J.get(J.get(pastEPSDataPoints, index), "value")) else "red")
    def _f41(record=J.undefined, *_args):
        return J.get(record, "value")
    def _f42(record=J.undefined, *_args):
        return J.get(record, "value")
    epsChartDefinition = J.obj(("width", "250px"), ("height", "80px"), ("type", "line"), ("options", J.obj(("scales", J.obj(("y", J.obj(("position", "right"), ("ticks", J.obj(("stepSize", J.div(epsRange, 3)), ("autoSkip", False))))), ("x", J.obj(("ticks", J.obj(("display", False))))))), ("plugins", J.obj(("legend", J.obj(("display", False))))))), ("data", J.obj(("labels", epsLabels), ("datasets", J.JSArray([J.obj(("label", "Current EPS"), ("borderColor", "var(--text-color)"), ("pointBorderWidth", 0), ("borderWidth", 1), ("backgroundColor", J.get(epsDataPoints, "map")(_f40)), ("data", J.get(epsDataPoints, "map")(_f41))), J.obj(("label", "Previous year EPS"), ("backgroundColor", "silver"), ("borderColor", "var(--border-color)"), ("pointBorderWidth", 0), ("borderWidth", 0.3), ("data", J.get(pastEPSDataPoints, "map")(_f42)))])))))
    SEPARATOR = J.obj(("text", ""), ("colspan", 2), ("borderBottom", "1px solid var(--border-color)"))
    G_paint_overlay("Table", J.obj(("position", "bottom_left"), ("order", "above_all")), J.obj(("fontSize", 12), ("border", "1px solid var(--border-color)"), ("background", "var(--background-color)"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("text", J.template(J.get(G_current, "ticker"), ": ", J.get(G_current, "sector"), " / ", J.get(G_current, "industry"))), ("color", "var(--text-color)"), ("padding", "3px 7px"))]))), J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(valueCell(J.template("Next earnings: ", J.get(moment(J.mul(J.get(nextEarnings, "timestamp"), 1000)), "format")("DD-MM-YYYY"), " (in ", daysUntilNextEarnings, " days)"))), ("colspan", 2))]))), J.obj(("cells", J.JSArray([SEPARATOR]))), J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(headCell("EPS over time")), ("colspan", 2))]))), J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("chart", epsChartDefinition))]))), J.obj(("cells", J.JSArray([SEPARATOR]))), J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(headCell("Revenue over time")), ("colspan", 2))]))), J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("chart", revenueChartDefinition))]))), J.obj(("cells", J.JSArray([SEPARATOR]))), J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("table", J.obj(("width", "100%"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([headCell("52Wk Low"), headCell("Last"), headCell("52Wk High")]))), J.obj(("cells", J.JSArray([valueCell(J.get(J.get(range52Wk, "low"), "toFixed")(J.get(G_current, "decimals"))), valueCell(J.get(lastPrice, "toFixed")(J.get(G_current, "decimals"))), valueCell(J.get(J.get(range52Wk, "high"), "toFixed")(J.get(G_current, "decimals")))]))), J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(SEPARATOR), ("colspan", 3))])))])))))]))), J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("table", J.obj(("width", "100%"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([headCell("RP sector"), rsCell(J.get(lastOf(rpSector), "toFixed")(1)), headCell("RP mkt.cap"), rsCell(J.get(lastOf(rpMktcap), "toFixed")(1))]))), J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(SEPARATOR), ("colspan", 4))])))])))))]))), J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("table", J.obj(("width", "100%"), ("rows", J.JSArray([J.obj(("cells", J.JSArray([J.obj(*J.obj_spread(headCell("Analysts")), ("borderRight", "1px solid var(--border-color)")), J.obj(("table", J.obj(("rows", J.JSArray([J.obj(("cells", J.JSArray([leftTitleCell("Sell"), J.obj(*J.obj_spread(rightValueCell(J.get(currentRatingsCount, "sell"))), ("color", "red")), leftTitleCell("Hold"), rightValueCell(J.get(currentRatingsCount, "hold")), leftTitleCell("Buy"), J.obj(*J.obj_spread(rightValueCell(J.get(currentRatingsCount, "buy"))), ("color", "green"))])))])))))]))), J.obj(("cells", J.JSArray([SEPARATOR])))])))))]))), J.obj(("cells", J.JSArray([J.obj(("colspan", 2), ("table", J.obj(("width", "100%"), ("rows", J.JSArray([titleValueRow("Mkt Cap", marketCap), titleValueRow("Shares Outstanding", sharesOutstanding), J.obj(("cells", J.JSArray([SEPARATOR]))), titleValueRow("P/E Ratio", currentFundamental("pe_ratio_ttm")), titleValueRow("Forward P/E", forwardPe), titleValueRow("5-Year P/E Range", J.template(peRatioMin, " - ", peRatioMax)), titleValueRow("EPS Growth", J.template(epsGrowth, "%")), J.obj(("cells", J.JSArray([SEPARATOR]))), titleValueRow("Yield", J.template(J.get(J.mul(100, divYield), "toFixed")(2), "%")), titleValueRow("Mgmt Ownership", mgmtOwnership), J.obj(("cells", J.JSArray([SEPARATOR]))), titleValueRow(J.template("Year ", J.sub(currentYear, 1), " EPS"), J.template("$", previousYearEps)), titleValueRow(J.template("Year ", currentYear, " EPS est"), J.template("$", currentYearEpsEst)), J.obj(("cells", J.JSArray([SEPARATOR]))), titleValueRow(J.template("Year ", J.sub(currentYear, 1), " Rev"), J.template("$", previousYearRevenue)), titleValueRow(J.template("Year ", currentYear, " Rev est"), J.template("$", currentYearRevenueEst)), J.obj(("cells", J.JSArray([SEPARATOR])))])))))])))]))))


register_store_indicator(
    script,
    name='company_profile_TS',
    title='Company Profile',
    developer='TrendSpider',
    url='https://trendspider.com/trading-tools-store/indicators/company-profile/',
    position='price',
    inputs=[],
    outputs=[],
    signals=[],
    requires=['analyst_ratings', 'earnings', 'fundamental', 'history', 'insider_trading', 'relative_performance'],
    parity='aapl_d: OK, syn_5m: both-error',
)
