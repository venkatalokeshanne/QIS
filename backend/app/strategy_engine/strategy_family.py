"""
Strategy-family eligibility (spec sections 25-27).

Maps the current market / ticker / premarket regimes to the strategy
families that are applicable, using the declarative rules in
thresholds.FAMILY_RULES_CONFIG. This is NOT historical qualification: a
family being applicable only means its strategies are worth checking
against history (the qualification engine decides the rest).

Every result lists the rules that fired, so the choice is explainable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from app.strategy_engine.models import Family, StrategyMeta
from app.strategy_engine.thresholds import FAMILY_RULES_CONFIG

ELIGIBLE = "ELIGIBLE"
LOWER_PRIORITY = "LOWER_PRIORITY"
NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class FamilyDecision:
    eligible: list[str] = field(default_factory=list)
    lower_priority: list[str] = field(default_factory=list)
    not_applicable: list[str] = field(default_factory=list)
    fired_rules: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def applicable(self) -> list[str]:
        return self.eligible + self.lower_priority

    def status_of(self, family: Family | str) -> str:
        f = str(family)
        return ELIGIBLE if f in self.eligible else LOWER_PRIORITY if f in self.lower_priority else NOT_APPLICABLE

    def to_dict(self) -> dict:
        return asdict(self)


def _field(regimes: dict, path: str):
    scope, key = path.split(".", 1)
    obj = regimes.get(scope)
    if obj is None:
        return None
    return obj.get(key) if isinstance(obj, dict) else getattr(obj, key, None)


class StrategyFamilyEngine:
    def __init__(self, config: dict | None = None):
        self.cfg = {**FAMILY_RULES_CONFIG, **(config or {})}

    def decide(self, market, ticker, premarket=None) -> FamilyDecision:
        """`market`, `ticker`, `premarket` are the regime objects (or dicts)."""
        regimes = {"market": market, "ticker": ticker, "premarket": premarket}
        cfg = self.cfg
        pm_label = _field(regimes, "premarket.premarket_regime") if premarket is not None else "NOT_EVALUATED"
        pm_ignored = pm_label in cfg["premarket_ignored_when"]
        d = FamilyDecision()
        if pm_ignored:
            d.notes.append(f"premarket regime {pm_label}: premarket does not add or remove families; "
                           f"using market + ticker regimes only")
        eligible, lower = [], []
        for rule in cfg["rules"]:
            when = rule["when"]
            if pm_ignored and any(k.startswith("premarket.") for k in when):
                continue
            if all(_field(regimes, k) in v for k, v in when.items()):
                d.fired_rules.append({"name": rule["name"], "when": when, "eligible": rule["eligible"],
                                      "lower_priority": rule.get("lower_priority", [])})
                eligible += rule["eligible"]
                lower += rule.get("lower_priority", [])
                if rule.get("note"):
                    d.notes.append(rule["note"])
        if not d.fired_rules:
            eligible = list(cfg["default_eligible"])
            d.notes.append("no family rule matched the current regimes; all families stay applicable "
                           "(none is prohibited without evidence)")
        order = [f.value for f in Family]
        d.eligible = [f for f in order if f in eligible]
        d.lower_priority = [f for f in order if f in lower and f not in d.eligible]
        d.not_applicable = [f for f in order if f not in d.eligible and f not in d.lower_priority
                            and f != Family.SPECIAL_ASSET_SPECIFIC.value]
        return d

    @staticmethod
    def strategy_status(strategy: StrategyMeta, decision: FamilyDecision) -> tuple[str, str]:
        """A strategy is as applicable as the best of its (primary or secondary)
        technique families. SPECIAL_ASSET_SPECIFIC is a scope marker, not a technique."""
        best, via = NOT_APPLICABLE, None
        rank = {ELIGIBLE: 2, LOWER_PRIORITY: 1, NOT_APPLICABLE: 0}
        for fam in strategy.all_families:
            if fam is Family.SPECIAL_ASSET_SPECIFIC:
                continue
            st = decision.status_of(fam)
            if rank[st] > rank[best]:
                best, via = st, fam
        if best == NOT_APPLICABLE:
            fams = ", ".join(str(f) for f in strategy.all_families if f is not Family.SPECIAL_ASSET_SPECIFIC)
            return best, f"family {fams} is not applicable in the current regime"
        primary = " (primary)" if via is strategy.family else " (secondary)"
        return best, f"family {via}{primary} is {best.lower().replace('_', ' ')} in the current regime"
