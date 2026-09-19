"""NYSE calendar vs. published holiday and early-close schedules."""

import datetime as dt

from app.strategy_engine.data.calendar import holidays, is_early_close, is_trading_day, session_bounds

D = dt.date

NYSE_2024 = {D(2024, 1, 1), D(2024, 1, 15), D(2024, 2, 19), D(2024, 3, 29), D(2024, 5, 27), D(2024, 6, 19),
             D(2024, 7, 4), D(2024, 9, 2), D(2024, 11, 28), D(2024, 12, 25)}
NYSE_2025 = {D(2025, 1, 1), D(2025, 1, 9), D(2025, 1, 20), D(2025, 2, 17), D(2025, 4, 18), D(2025, 5, 26),
             D(2025, 6, 19), D(2025, 7, 4), D(2025, 9, 1), D(2025, 11, 27), D(2025, 12, 25)}
NYSE_2026 = {D(2026, 1, 1), D(2026, 1, 19), D(2026, 2, 16), D(2026, 4, 3), D(2026, 5, 25), D(2026, 6, 19),
             D(2026, 7, 3), D(2026, 9, 7), D(2026, 11, 26), D(2026, 12, 25)}
NYSE_2022 = {D(2022, 1, 17), D(2022, 2, 21), D(2022, 4, 15), D(2022, 5, 30), D(2022, 6, 20), D(2022, 7, 4),
             D(2022, 9, 5), D(2022, 11, 24), D(2022, 12, 26)}  # New Year 2022 fell on a Saturday: not observed


def test_published_holidays():
    assert holidays(2024) == NYSE_2024
    assert holidays(2025) == NYSE_2025
    assert holidays(2026) == NYSE_2026
    assert holidays(2022) == NYSE_2022


def test_early_closes():
    assert is_early_close(D(2024, 7, 3)) and is_early_close(D(2024, 11, 29)) and is_early_close(D(2024, 12, 24))
    assert is_early_close(D(2025, 7, 3)) and is_early_close(D(2025, 12, 24))
    assert not is_early_close(D(2026, 7, 3))   # a holiday that year (July 4 is a Saturday)
    assert not is_early_close(D(2024, 7, 5))


def test_session_bounds_follow_new_york_time_across_dst():
    winter = session_bounds(D(2026, 1, 5))
    summer = session_bounds(D(2026, 7, 6))
    # 09:30 New York is 14:30 UTC in winter, 13:30 UTC in summer
    assert winter.open.astimezone(dt.timezone.utc).hour == 14
    assert summer.open.astimezone(dt.timezone.utc).hour == 13
    early = session_bounds(D(2025, 11, 28))
    assert early.close.hour == 13 and early.after_hours_end.hour == 17


def test_weekends_and_holidays_are_closed():
    assert session_bounds(D(2026, 9, 19)) is None       # Saturday
    assert session_bounds(D(2026, 12, 25)) is None
    assert is_trading_day(D(2026, 9, 18))
