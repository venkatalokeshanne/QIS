"""
Daily Levels Signal.

Turns the same "known right now" levels the Daily Levels snapshot
already shows (see app.services.levels_service) into a single,
explainable buy/sell/neutral read for the CURRENT moment -- not a
backtestable strategy (no entry/exit/trade simulation, no historical
win rate), just a transparent scoring of where price sits relative to
its own level structure. Every point added or subtracted comes with a
plain-language reason, so nothing about the verdict is a black box.

Deliberately conservative about what counts as a real signal: this
session's own backtesting found raw "does a level hold" accuracy sits
close to a coin flip (see conversation history), so this only fires a
directional verdict when MULTIPLE independent signals line up
(confluence), not from any single indicator alone.
"""

from dataclasses import dataclass, field

from app.services.levels_service import DailyLevels

_CONFLUENCE_TOLERANCE_PCT = 0.5  # levels within this % of each other count as "the same zone"
_ACTIONABLE_DISTANCE_PCT = 1.0  # price must be within this % of a level for it to matter right now
_BUY_THRESHOLD = 2
_SELL_THRESHOLD = -2


@dataclass(frozen=True)
class SignalResult:
    verdict: str  # "buy" | "sell" | "neutral"
    score: int
    reasons: list[str] = field(default_factory=list)


def _all_levels(levels: DailyLevels) -> list[float]:
    """Every numeric level across every family, flattened -- used only
    to measure proximity/confluence, agnostic of which family a level
    came from."""
    values: list[float | None] = [
        levels.prior_high,
        levels.prior_low,
        levels.opening_range_high,
        levels.opening_range_low,
        levels.adr_expected_high,
        levels.adr_expected_low,
        *levels.pivot_points.values(),
        *levels.camarilla_pivots.values(),
        *levels.demark_pivots.values(),
        *levels.auto_support_resistance,
        *levels.fibonacci_retracement.values(),
    ]
    return [v for v in values if v is not None]


def _confluence_count(target_level: float, all_levels: list[float]) -> int:
    """How many OTHER levels land within tolerance of `target_level` --
    a level several families agree on is a stronger zone than one
    lone reading."""
    return sum(
        1 for lv in all_levels if lv != target_level and abs(lv - target_level) / target_level * 100 <= _CONFLUENCE_TOLERANCE_PCT
    )


def _vwap_bias(levels: DailyLevels) -> tuple[int, str | None]:
    if levels.vwap is None:
        return 0, None
    if levels.current_price > levels.vwap:
        return 1, f"Trading above VWAP (${levels.vwap:.2f}) -- intraday bias is bullish."
    if levels.current_price < levels.vwap:
        return -1, f"Trading below VWAP (${levels.vwap:.2f}) -- intraday bias is bearish."
    return 0, None


def _adr_exhaustion(levels: DailyLevels) -> tuple[int, str | None]:
    if levels.adr_expected_low is not None and levels.current_price <= levels.adr_expected_low:
        return 1, (
            f"At or below the ADR-projected low (${levels.adr_expected_low:.2f}) -- "
            "today's typical range is already exhausted to the downside, raising bounce odds."
        )
    if levels.adr_expected_high is not None and levels.current_price >= levels.adr_expected_high:
        return -1, (
            f"At or above the ADR-projected high (${levels.adr_expected_high:.2f}) -- "
            "today's typical range is already exhausted to the upside, raising pullback odds."
        )
    return 0, None


def _confluence_proximity(levels: DailyLevels) -> tuple[int, str | None]:
    all_levels = _all_levels(levels)
    price = levels.current_price

    below = [lv for lv in all_levels if lv < price]
    above = [lv for lv in all_levels if lv > price]
    nearest_support = max(below) if below else None
    nearest_resistance = min(above) if above else None

    support_distance_pct = (price - nearest_support) / price * 100 if nearest_support is not None else None
    resistance_distance_pct = (nearest_resistance - price) / price * 100 if nearest_resistance is not None else None

    closer_to_support = support_distance_pct is not None and (
        resistance_distance_pct is None or support_distance_pct <= resistance_distance_pct
    )

    if closer_to_support and support_distance_pct <= _ACTIONABLE_DISTANCE_PCT:
        confluence = _confluence_count(nearest_support, all_levels)
        if confluence >= 1:
            return 2, (
                f"Within {support_distance_pct:.2f}% of a support zone at ${nearest_support:.2f} "
                f"confirmed by {confluence + 1} independent level readings."
            )
        return 0, f"Near a support level at ${nearest_support:.2f}, but no other level family confirms it."

    if not closer_to_support and resistance_distance_pct is not None and resistance_distance_pct <= _ACTIONABLE_DISTANCE_PCT:
        confluence = _confluence_count(nearest_resistance, all_levels)
        if confluence >= 1:
            return -2, (
                f"Within {resistance_distance_pct:.2f}% of a resistance zone at ${nearest_resistance:.2f} "
                f"confirmed by {confluence + 1} independent level readings."
            )
        return 0, f"Near a resistance level at ${nearest_resistance:.2f}, but no other level family confirms it."

    return 0, "Sitting mid-range between the nearest support and resistance -- no confluence edge either way."


def _gap_fill_tendency(levels: DailyLevels) -> tuple[int, str | None]:
    if levels.gap_pct > 0 and levels.current_price < levels.session_open:
        return -1, "Gapped up but has already given back part of the move -- gap-fill tendency favors further downside."
    if levels.gap_pct < 0 and levels.current_price > levels.session_open:
        return 1, "Gapped down but has already recovered part of the move -- gap-fill tendency favors further upside."
    return 0, None


def compute_signal(levels: DailyLevels) -> SignalResult:
    score = 0
    reasons: list[str] = []

    for rule in (_vwap_bias, _adr_exhaustion, _confluence_proximity, _gap_fill_tendency):
        points, reason = rule(levels)
        score += points
        if reason:
            reasons.append(reason)

    if score >= _BUY_THRESHOLD:
        verdict = "buy"
    elif score <= _SELL_THRESHOLD:
        verdict = "sell"
    else:
        verdict = "neutral"

    return SignalResult(verdict=verdict, score=score, reasons=reasons)
