"""
Deterministic stand-ins for TrendSpider's alternative data (request.*),
shaped like the examples in TrendSpider's API reference. They exist only
so the parity harness can drive the scripts that consume such data: the
Python side and TrendSpider's engine are handed the identical responses
(in call order), so the translation of those scripts is verified even
though the data itself is synthetic.
"""

from __future__ import annotations

import hashlib
import random


def _rnd(*key):
    return random.Random(int(hashlib.md5("|".join(map(str, key)).encode()).hexdigest()[:8], 16))


def fixture(kind, args, bars):
    t0, t1 = bars["time"][0], bars["time"][-1]
    span = max(1, t1 - t0)
    ticker = args[0] if args and isinstance(args[0], str) else "AAPL"
    r = _rnd(kind, ticker, len(bars["time"]))
    last = bars["close"][-1]
    if kind == "earnings":
        out = []
        t = t0 + 86400 * 20
        q = 1
        while t < t1 + 86400 * 60:
            eps_est = round(r.uniform(0.5, 2.5), 2)
            eps = round(eps_est * r.uniform(0.85, 1.2), 2)
            rev_est = r.randint(50, 100) * 1_000_000_000
            rev = int(rev_est * r.uniform(0.9, 1.1))
            out.append({"timestamp": int(t), "isFuture": t > t1, "when": r.choice(["premarket", "postmarket"]),
                        "change": round(r.uniform(-10, 15), 2), "revenue_change": round(r.uniform(-5, 10), 2),
                        "eps": eps, "eps_est": eps_est, "eps_surprise_percent": round((eps - eps_est) / eps_est * 100, 2),
                        "revenue": rev, "revenue_est": rev_est, "revenue_surprise_percent": round((rev - rev_est) / rev_est * 100, 2),
                        "period": f"Q{q}", "period_year": 2024 + (q > 4), "accounting_method": "gaap",
                        "id": f"e{len(out)}", "ticker": ticker})
            q = q % 4 + 1
            t += 86400 * 91
        return list(reversed(out))
    if kind == "analyst_ratings":
        return [{"action": r.choice(["initial", "downgrade", "confirm", "upgrade"]),
                 "analystCompany": r.choice(["Bernstein", "Goldman", "Barclays", "UBS"]), "analystPerson": "A. Analyst",
                 "ratingCurrent": r.choice(["buy", "hold", "sell"]), "ratingPrior": r.choice(["buy", "hold", "sell"]),
                 "pTarget": round(last * r.uniform(0.8, 1.4), 2), "pTargetPrior": round(last * r.uniform(0.8, 1.3), 2),
                 "timestamp": int(t1 - r.randint(0, span))} for _ in range(40)]
    if kind == "unusual_options":
        out = []
        for _ in range(60):
            strike = round(last * r.uniform(0.8, 1.2))
            typ = r.choice(["CALL", "PUT"])
            dte = r.randint(1, 60)
            ts = int(t1 - r.randint(0, min(span, 86400 * 20)))
            out.append({"timestamp": ts, "costBasis": r.randint(20_000, 2_000_000), "dealType": r.choice(["TRADE", "SWEEP", "BLOCK"]),
                        "assetPrice": last, "strike": strike, "type": typ, "oi": r.randint(100, 20000),
                        "moneyStatus": r.choice(["OTM", "ITM"]), "expDate": (ts + dte * 86400) * 1000,
                        "expDateFormatted": "20 Jun'26", "daysToExp": dte, "size": r.randint(10, 3000),
                        "oiPercent": round(r.uniform(0.1, 50), 2),
                        "tags": [r.choice(["trade", "sweep"]), r.choice(["bullish", "bearish"]), "stock", typ.lower()]})
        return sorted(out, key=lambda x: -x["timestamp"])
    if kind == "options_schedule":
        out = []
        for k in range(8):
            ts = t1 + 86400 * (7 * k + 3)
            import datetime as dt

            d = dt.datetime.utcfromtimestamp(ts)
            out.append({"expiration": {"day": d.day, "month": d.strftime("%b"), "year": d.year,
                                       "code": int(d.strftime("%y%m%d")), "dte": 7 * k + 3, "timestamp": ts * 1000,
                                       "schedule": "W"},
                        "ticker": f"{ticker}.{d.strftime('%y%m%d')}.{{DIRECTION}}.{{STRIKE}}",
                        "strikes": [round(last * (0.8 + 0.02 * i)) for i in range(21)]})
        return out
    if kind in ("options_data_for_expiration", "options_data_for_all_expirations"):
        def chain(n):
            res = {}
            for i in range(n):
                strike = round(last * (0.85 + 0.015 * i))
                res[str(strike)] = {side: {"l": round(r.uniform(0.1, 20), 2), "oi": r.randint(0, 30000),
                                           "iv": round(r.uniform(0.15, 0.9), 4), "gd": round(r.uniform(-1, 1), 3),
                                           "gg": round(r.uniform(0, 0.1), 4), "b": 1.0, "a": 1.1, "dvol": r.randint(0, 5000)}
                                    for side in ("C", "P")}
            return res

        if kind == "options_data_for_expiration":
            return {"underlyingSymbolQuote": {"lastPrice": last}, "resultByStrike": chain(21)}
        return {"underlyingSymbolQuote": {"lastPrice": last},
                "resultByExpiration": {str(260600 + 7 * k): chain(11) for k in range(4)}}
    if kind == "relative_performance":
        return [[t, round(r.uniform(-30, 60), 2)] for t in bars["time"][:: max(1, len(bars["time"]) // 200)]]
    if kind == "fundamental":
        metrics = args[1] if len(args) > 1 and isinstance(args[1], list) else ["revenue"]
        n = int(args[2]) if len(args) > 2 and isinstance(args[2], (int, float)) else 4
        out = {}
        for m in metrics:
            rows, base = [], r.uniform(1e6, 1e11)
            for k in range(n):
                ts = t1 - k * 91 * 86400
                rows.append({"reportdate": ts, "reportDateShort": 20260331 - k * 300, "year": 2026 - k // 4,
                             "quarter": 4 - k % 4, "value": round(base * r.uniform(0.8, 1.2), 2)})
            out[m] = rows
        return out
    if kind == "seasonality":
        cats = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return {"dataByCategory": {c: [{"timestamp": 1325455200 + y * 31536000 + i * 2592000, "value": round(r.uniform(-8, 8), 2)}
                                       for y in range(10)] for i, c in enumerate(cats)}}
    if kind == "insider_trading":
        ciks = [f"000{1000000 + i}" for i in range(4)]
        return {"insidersByCIK": {c: {"name": f"Insider {i}", "role": {"type": "director", "title": "Director"}} for i, c in enumerate(ciks)},
                "ownershipByCIK": {c: r.randint(1000, 1_000_000) for c in ciks},
                "transactions": [{"insider": r.choice(ciks), "timestamp": (t1 - r.randint(0, span)) * 1000, "security": "stock",
                                  "derivative": False, "volume": r.randint(100, 50000), "netValue": r.randint(10_000, 5_000_000),
                                  "action": r.choice(["dispose", "acquire"]), "transaction": r.choice(["sell", "buy"])} for _ in range(30)]}
    if kind == "congress_trading":
        return [{"representative": f"Rep {i}", "ticker": ticker, "transaction": r.choice(["sale", "purchase"]),
                 "house": r.choice(["house", "senate"]), "party": r.choice(["D", "R"]),
                 "report_date": t1 - r.randint(0, span), "timestamp": t1 - r.randint(0, span),
                 "range_from": 1001, "range_to": 15000} for i in range(20)]
    if kind == "dividends":
        out = []
        t = t0 + 86400 * 30
        while t < t1:
            amt = round(r.uniform(0.2, 1.0), 3)
            out += [{"amount": amt, "type": "declaration", "timestamp": t, "dividend_yield": 0.5},
                    {"amount": amt, "type": "ex-date", "timestamp": t + 86400 * 14, "dividend_yield": 0.5}]
            t += 86400 * 91
        return list(reversed(out))
    if kind == "news":
        return [{"timestamp": t1 - r.randint(0, span), "daysAgo": r.randint(0, 300), "author": "Reporter",
                 "title": f"Headline {i}", "teaser": "Teaser text", "url": "https://example.com/n"} for i in range(50)]
    if kind == "http" and isinstance(args[0], str) and "api.worldbank.org" in args[0] and "/topic/" in args[0]:
        ids = _world_bank_ids()
        return [{"page": 1, "pages": 1, "per_page": 1000, "total": len(ids)},
                [{"id": i, "name": f"Indicator {i}", "unit": "", "source": {"id": "2", "value": "WDI"},
                  "sourceNote": f"Synthetic note for {i}", "sourceOrganization": "Synthetic",
                  "topics": [{"id": "8", "value": "Health"}]} for i in ids]]
    if kind == "http":
        # A JSON document shaped like the World Bank API (what most store
        # scripts that use request.http() query): [meta, [rows]].
        return [{"page": 1, "pages": 1, "per_page": 100, "total": 30},
                [{"date": str(2025 - i), "value": round(r.uniform(-3, 8), 3),
                  "country": {"id": "US", "value": "United States"}, "indicator": {"id": "X", "value": "X"}} for i in range(30)]]
    return {"error": f"no fixture for {kind}"}


_WB_IDS = None


def _world_bank_ids():
    global _WB_IDS
    if _WB_IDS is None:
        import re
        from pathlib import Path

        ids = []
        for f in sorted((Path(__file__).resolve().parents[1] / "clean").glob("*world-bank*.js")):
            for i in re.findall(r'"([A-Z]{2,3}\.[A-Z0-9.]+)"', f.read_text(encoding="utf-8")):
                if i not in ids:
                    ids.append(i)
        _WB_IDS = ids
    return _WB_IDS
