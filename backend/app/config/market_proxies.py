"""
Market-proxy tickers for the Daily Strategy Selector's market-wide
regime read (see app.services.regime_classifier).

Static config, not environment/settings -- these are app data (which
proxy represents "the market" for a given ticker), same spirit as
frontend/src/data/watchlists.js, not something that varies per deploy.
"""

# Every ticker gets at least these two -- broad market (SPY) plus a
# tech-heavy read (QQQ), since the platform's watchlist skews AI/tech.
DEFAULT_MARKET_PROXIES = ["SPY", "QQQ"]

# Semiconductor-heavy names get SMH added -- SPY/QQQ alone dilute a
# name whose actual day-to-day mover is semis-specific sentiment, not
# the broad tape. Covers the starter tickers plus the wider AI Core
# watchlist's obvious semis names, so calibrating additional tickers
# later doesn't require touching this file first.
_SEMIS_TICKERS = ["NVDA", "AMD", "AVGO", "TSM", "MU", "QCOM", "ASML", "INTC"]
SECTOR_PROXY_OVERRIDES: dict[str, list[str]] = {
    ticker: [*DEFAULT_MARKET_PROXIES, "SMH"] for ticker in _SEMIS_TICKERS
}


def market_proxies_for(symbol: str) -> list[str]:
    """The market-proxy tickers to use for `symbol`'s market-regime
    read -- SECTOR_PROXY_OVERRIDES if it has one, else DEFAULT_MARKET_PROXIES."""
    return SECTOR_PROXY_OVERRIDES.get(symbol.upper(), DEFAULT_MARKET_PROXIES)


# Starter calibration set (see the Daily Strategy Selector plan) --
# spans the watchlist's volatility/liquidity range: IONQ (small,
# regime-dependent per prior analysis), NVDA (mega-cap, liquid), TSLA
# (liquid but historically regime-volatile), PLTR (mid-cap, choppier),
# RKLB (small-cap, higher-vol).
STARTER_TICKERS = ["IONQ", "NVDA", "TSLA", "PLTR", "RKLB"]
