"""
Every tunable number of the Strategy Selection Engine, in one place.

These are INITIAL values, not statistically optimal truths. Change them
here (or pass overrides to the engine); `config_version()` hashes the
effective configuration and is logged with every selection decision so
a result can be reproduced with exactly the configuration that made it.
"""

from __future__ import annotations

import copy
import hashlib
import json

SESSION_CONFIG = {
    "timezone": "America/New_York",
    "premarket_start": "04:00",
    "rth_open": "09:30",
    "rth_close": "16:00",
    "early_close": "13:00",
    "after_hours_end": "20:00",
    "early_after_hours_end": "17:00",
}

DATA_QUALITY_CONFIG = {
    # RTH candles a trading day should have, as a fraction of the expected
    # count, before the day counts as having missing candles.
    "min_rth_completeness": 0.90,
    # Share of trading days allowed to be incomplete before the dataset is
    # DATA_INSUFFICIENT.
    "max_incomplete_day_fraction": 0.05,
    # RTH bars with zero volume beyond this share -> suspicious feed.
    "max_zero_volume_fraction": 0.02,
    # Close-to-close jumps larger than this (and not a normal gap) are
    # flagged as possible unadjusted corporate actions (splits).
    "corporate_action_jump": 0.45,
    # Minimum history (bars) required per purpose.
    "min_daily_bars": 260,      # ~1 year: SMA200 + percentile history
    "min_intraday_days": 20,    # time-of-day RVOL needs this many prior sessions
}

MARKET_REGIME_CONFIG = {
    "reference_symbols": ["SPY", "QQQ", "IWM"],
    "direction_symbols": ["SPY", "QQQ"],
    "volatility_symbol": "VIX",          # optional secondary input
    "ema_fast": 20,
    "ema_slow": 50,
    "sma_mid": 50,
    "sma_long": 200,
    "adx_period": 14,
    "trend_adx_threshold": 20,
    "strong_adx_threshold": 30,
    "swing_lookback": 5,                 # bars on each side for swing highs/lows
    "structure_swings": 2,               # compare the last N swing highs/lows
    "atr_period": 14,
    "hv_period": 20,
    "volatility_percentiles": [0.20, 0.70, 0.90],   # LOW | NORMAL | HIGH | EXTREME
    "volatility_history_bars": 252,
    "minimum_confirmation_period": 3,    # regime persistence
}

TICKER_REGIME_CONFIG = {
    "ema_periods": [9, 20, 50],
    "sma_long": 200,
    "slope_lookback": 5,
    "strong_trend_slope": 0.01,          # EMA20 change over slope_lookback, as a fraction
    "roc_period": 10,
    "rsi_period": 14,
    "macd": [12, 26, 9],
    "relative_strength_windows": [1, 5, 20],
    "relative_strength_benchmarks": ["SPY", "QQQ"],
    "strong_rs_threshold": 0.03,         # outperformance over the 20-day window
    "weak_rs_threshold": -0.03,
    "atr_period": 14,
    "hv_period": 20,
    "volatility_percentiles": [0.20, 0.70, 0.90],
    "volatility_history_bars": 252,
    "rvol_lookback_days": 20,
    "rvol_levels": [0.7, 1.5, 3.0],      # LOW | NORMAL | HIGH | EXTREME
    "gap_levels": [0.005, 0.02, 0.05, 0.10],  # NO | SMALL | MODERATE | LARGE | EXTREME (abs gap)
    "liquidity_dollar_volume": [5_000_000, 50_000_000],  # LOW | MEDIUM | HIGH (avg daily $ volume)
    "liquidity_lookback_days": 20,
    "earnings_soon_days": 5,
    "minimum_confirmation_period": 3,
    # Young listings (e.g. INFQ) can be classified from ~6 months: the labels
    # need EMA50 slopes (~55 bars) and volatility percentiles (~80 bars);
    # SMA200 is reported but not used by any label. Below `full_history_bars`
    # the result carries a SHORT_HISTORY warning.
    "min_daily_bars": 120,
    "full_history_bars": 260,
}

PREMARKET_CONFIG = {
    "session_start": "04:00",
    "session_end": "09:30",
    "timezone": "America/New_York",
    "min_non_empty_bar_ratio": 0.30,
    "min_premarket_dollar_volume": 1_000_000,
    "gap_percentile_thresholds": [0.20, 0.70, 0.90],
    "rvol_percentile_thresholds": [0.20, 0.70, 0.90],
    "rvol_lookback_days": 20,
    "market_gap_confirm_pct": 0.003,
    "strong_gap_pct": 0.03,              # fallback when too little history for percentiles
    "gap_pct": 0.01,
    "holding_highs_position": 0.70,      # position in premarket range
    "holding_lows_position": 0.30,
}

FAMILY_RULES_CONFIG = {
    # Initial, configurable mapping from regimes to strategy families (spec 26).
    # A rule fires when every field in `when` matches (lists = any of). Families
    # a firing rule lists as "eligible" are applicable; "lower_priority" ones stay
    # applicable but are flagged -- no family is prohibited just by these rules.
    # Families no firing rule mentions are NOT applicable in that regime.
    # Fields: market.direction / market.volatility / market.trend_strength /
    #         ticker.trend / ticker.momentum / ticker.volatility / ticker.volume /
    #         premarket.premarket_regime / premarket.structure
    "rules": [
        {"name": "bullish_high_volatility_strong_momentum",
         "when": {"market.direction": ["BULLISH"], "market.volatility": ["HIGH", "EXTREME"],
                  "ticker.momentum": ["STRONG", "POSITIVE"]},
         "eligible": ["BREAKOUT_MOMENTUM", "VWAP_INTRADAY", "TREND_FOLLOWING"],
         "lower_priority": ["MEAN_REVERSION"]},
        {"name": "neutral_calm_market",
         "when": {"market.direction": ["NEUTRAL"], "market.volatility": ["LOW", "NORMAL"]},
         "eligible": ["MEAN_REVERSION", "REVERSAL"],
         "lower_priority": ["OSCILLATOR_MOMENTUM"]},
        {"name": "strong_ticker_trend",
         "when": {"ticker.trend": ["STRONG_UPTREND", "STRONG_DOWNTREND"]},
         "eligible": ["TREND_FOLLOWING", "BREAKOUT_MOMENTUM", "VWAP_INTRADAY", "LONG_TERM_BREAKOUT"],
         "lower_priority": ["OSCILLATOR_MOMENTUM"]},
        {"name": "ticker_uptrend",
         "when": {"ticker.trend": ["UPTREND"]},
         "eligible": ["TREND_FOLLOWING", "OSCILLATOR_MOMENTUM"],
         "lower_priority": ["BREAKOUT_MOMENTUM", "LONG_TERM_BREAKOUT"]},
        {"name": "ticker_downtrend",
         "when": {"ticker.trend": ["DOWNTREND"]},
         "eligible": ["REVERSAL"],
         "lower_priority": ["MEAN_REVERSION", "OSCILLATOR_MOMENTUM"]},
        {"name": "bullish_market",
         "when": {"market.direction": ["BULLISH"]},
         "eligible": ["TREND_FOLLOWING", "LONG_TERM_BREAKOUT", "OSCILLATOR_MOMENTUM"],
         "lower_priority": []},
        {"name": "bearish_market",
         "when": {"market.direction": ["BEARISH"]},
         "eligible": ["REVERSAL"],
         "lower_priority": ["MEAN_REVERSION", "BREAKOUT_MOMENTUM"]},
        {"name": "extreme_volatility",
         "when": {"market.volatility": ["EXTREME"]},
         "eligible": ["BREAKOUT_MOMENTUM"],
         "lower_priority": [],
         "note": "extreme volatility: stricter risk controls required"},
        {"name": "premarket_strong_gap_up_holding",
         "when": {"premarket.premarket_regime": ["STRONG_GAP_UP_HIGH_PARTICIPATION", "GAP_UP_HIGH_PARTICIPATION"],
                  "premarket.structure": ["HOLDING_HIGHS"]},
         "eligible": ["BREAKOUT_MOMENTUM", "VWAP_INTRADAY"],
         "lower_priority": ["MEAN_REVERSION"]},
        {"name": "premarket_gap_fading_or_low_participation",
         "when": {"premarket.premarket_regime": ["GAP_UP_LOW_PARTICIPATION", "STRONG_GAP_UP_LOW_PARTICIPATION",
                                                 "GAP_DOWN_LOW_PARTICIPATION", "STRONG_GAP_DOWN_LOW_PARTICIPATION"]},
         "eligible": ["MEAN_REVERSION", "REVERSAL"],
         "lower_priority": ["BREAKOUT_MOMENTUM"]},
        {"name": "premarket_fading",
         "when": {"premarket.structure": ["FADING"]},
         "eligible": ["MEAN_REVERSION", "REVERSAL"],
         "lower_priority": ["BREAKOUT_MOMENTUM"]},
        {"name": "premarket_flat_quiet",
         "when": {"premarket.premarket_regime": ["FLAT_QUIET"]},
         "eligible": ["MEAN_REVERSION"],
         "lower_priority": ["BREAKOUT_MOMENTUM"]},
    ],
    # Premarket regimes that must not add or remove families (spec 26).
    "premarket_ignored_when": ["PREMARKET_UNRELIABLE", "PREMARKET_DATA_UNAVAILABLE", "NOT_EVALUATED"],
    # When no rule fires at all, these families are applicable (nothing is
    # prohibited without evidence).
    "default_eligible": ["TREND_FOLLOWING", "BREAKOUT_MOMENTUM", "MEAN_REVERSION", "REVERSAL",
                         "VWAP_INTRADAY", "OSCILLATOR_MOMENTUM", "LONG_TERM_BREAKOUT"],
}

QUALIFICATION_CONFIG = {
    "min_trades": 100,
    "min_profit_factor": 1.20,
    "min_oos_profit_factor": 1.10,
    "min_sharpe": 0.50,
    "max_drawdown": 0.30,
    "require_walk_forward": True,
    "min_walk_forward_pass_rate": 0.60,
    "require_parameter_stability": True,
    "min_parameter_stability": 0.60,
    "slippage_multipliers": [0, 1, 2, 3],
    "min_pf_at_2x_slippage": 1.05,
    "min_regime_matched_trades": 30,
    "oos_fraction": 0.30,
    "walk_forward_periods": 8,
}

EXECUTION_COST_CONFIG = {
    # Estimated one-way slippage as a fraction of price ("1x").
    "rth_slippage": 0.0005,
    "premarket_slippage": 0.0020,
    "commission_per_trade": 0.0,
}


def all_config() -> dict:
    return copy.deepcopy({
        "SESSION_CONFIG": SESSION_CONFIG,
        "DATA_QUALITY_CONFIG": DATA_QUALITY_CONFIG,
        "MARKET_REGIME_CONFIG": MARKET_REGIME_CONFIG,
        "TICKER_REGIME_CONFIG": TICKER_REGIME_CONFIG,
        "PREMARKET_CONFIG": PREMARKET_CONFIG,
        "FAMILY_RULES_CONFIG": FAMILY_RULES_CONFIG,
        "QUALIFICATION_CONFIG": QUALIFICATION_CONFIG,
        "EXECUTION_COST_CONFIG": EXECUTION_COST_CONFIG,
    })


def config_version(config: dict | None = None) -> str:
    blob = json.dumps(config if config is not None else all_config(), sort_keys=True, default=str)
    return hashlib.sha1(blob.encode()).hexdigest()[:12]
