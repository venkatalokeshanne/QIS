"""
Shared win/loss streak calculation.

Not a registered Metric -- a helper so the two streak metrics don't
duplicate the same loop.
"""

import pandas as pd


def longest_streak(pnl: pd.Series, *, winning: bool) -> int:
    """Longest run of consecutive winning (or losing) trades."""
    if pnl.empty:
        return 0
    condition = (pnl > 0) if winning else (pnl < 0)
    longest = current = 0
    for is_match in condition:
        current = current + 1 if is_match else 0
        longest = max(longest, current)
    return longest
