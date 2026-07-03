"""
Session-timing utilities.

Several indicators and strategies need to know "when did today's
session start" (VWAP reset, Opening Range, ORB entry timing). This is
written once here so that logic isn't duplicated across modules.
"""

import pandas as pd


def session_start_series(index: pd.DatetimeIndex) -> pd.Series:
    """For each timestamp, return the timestamp of the first bar of its session (day)."""
    if not isinstance(index, pd.DatetimeIndex):
        raise ValueError("session_start_series requires a DatetimeIndex.")
    ts = pd.Series(index, index=index)
    return ts.groupby(index.date).transform("min")


def minutes_since_session_start(index: pd.DatetimeIndex) -> pd.Series:
    """Float Series: minutes elapsed since the start of each bar's session."""
    starts = session_start_series(index)
    ts = pd.Series(index, index=index)
    return (ts - starts).dt.total_seconds() / 60.0


def is_last_bar_of_session(index: pd.DatetimeIndex) -> pd.Series:
    """Boolean Series: True on the final bar of each session (day)."""
    if not isinstance(index, pd.DatetimeIndex):
        raise ValueError("is_last_bar_of_session requires a DatetimeIndex.")
    ts = pd.Series(index, index=index)
    session_max = ts.groupby(index.date).transform("max")
    return ts == session_max


def is_first_bar_of_session(index: pd.DatetimeIndex) -> pd.Series:
    """Boolean Series: True on the first bar of each session (day)."""
    if not isinstance(index, pd.DatetimeIndex):
        raise ValueError("is_first_bar_of_session requires a DatetimeIndex.")
    ts = pd.Series(index, index=index)
    session_min = ts.groupby(index.date).transform("min")
    return ts == session_min
