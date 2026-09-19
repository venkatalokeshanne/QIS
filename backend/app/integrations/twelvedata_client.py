"""
Twelve Data historical bars client (https://twelvedata.com/docs).

Thin wrapper around Twelve Data's `/time_series` REST endpoint -- the
one bar source for the whole app, injectable as `fetch_bars` into
app.services.levels_service / app.services.signal_service /
app.services.backtest_data. This does NOT stream live data or place
orders.

Requires at least one of TWELVEDATA_API_KEY_1..TWELVEDATA_API_KEY_5 set
(backend/.env) -- see backend/.env.example. When more than one is set,
requests are round-robinned across all of them via _KeyPool below to
spread load and stay under each key's own per-minute rate limit.
"""

import threading
import time
from collections import deque
from datetime import time as time_cls

import pandas as pd
import requests

from app.config.settings import settings
from app.core.exceptions import TwelveDataError

_TIMEOUT_SECONDS = 10
_RATE_LIMIT_WINDOW_SECONDS = 60.0

# Twelve Data's /time_series hard cap -- asking for even 5001 gets a
# flat HTTP 400, not a truncated response (verified against the live
# API). Clamped here rather than trusted to every caller because it's a
# property of the data source itself: the pre-TwelveData DXLink feed
# streamed with no such cap, so callers written against it (and the
# constants sized for it) legitimately asked for far more.
#
# Callers wanting a wider window than 5000 bars covers must either use
# a coarser interval or page across multiple requests -- silently
# clamping means the FRESHEST 5000 bars come back, so a request for a
# longer span quietly covers less calendar time than asked for. Every
# caller that can be affected reports the actual span it received
# (e.g. historical_period_start/end, walk-forward's fold_date_ranges)
# rather than echoing back the requested one.
MAX_OUTPUTSIZE = 5000

# Regular US equity session, America/New_York (naive, since every bar
# timestamp in this app is already tz-localized to NY and stripped).
_SESSION_REGULAR_START = time_cls(9, 30)
_SESSION_REGULAR_END = time_cls(16, 0)
# Pre-/after-market, same calendar day as the regular session either side of it.
_SESSION_EXTENDED_START = time_cls(4, 0)
_SESSION_EXTENDED_END = time_cls(20, 0)
# Overnight is everything NOT regular or extended, i.e. 20:00-04:00.

# A daily/weekly/monthly bar's single timestamp represents the whole
# period (Twelve Data returns it at midnight), not a specific time of
# day -- there's no regular/extended/overnight session for it to
# belong to, so filter_by_session must never run on these or every bar
# gets silently dropped whenever include_overnight is left at its
# default False.
_DAILY_OR_COARSER_INTERVALS = frozenset({"1day", "1week", "1month"})


def filter_by_session(df: pd.DataFrame, include_extended_hours: bool, include_overnight: bool) -> pd.DataFrame:
    """Twelve Data's `/time_series` endpoint has no native trading-hours
    toggle (unlike DXLink's `tho` flag) -- whatever bars it returns for
    an intraday interval are filtered down to the requested session(s)
    here instead. Regular-session bars are always kept. No-op (returns
    df unchanged) when both flags are True.

    Note: if Twelve Data's plan/endpoint doesn't return pre-/after-
    market or overnight bars in the first place, setting these flags
    won't conjure bars that were never in the response.
    """
    if include_extended_hours and include_overnight:
        return df
    times = df["date"].dt.time if "date" in df.columns else pd.Series(df.index, index=df.index).dt.time
    is_regular = (times >= _SESSION_REGULAR_START) & (times < _SESSION_REGULAR_END)
    is_extended = ((times >= _SESSION_EXTENDED_START) & (times < _SESSION_REGULAR_START)) | (
        (times >= _SESSION_REGULAR_END) & (times < _SESSION_EXTENDED_END)
    )
    keep = is_regular.copy()
    if include_extended_hours:
        keep |= is_extended
    if include_overnight:
        keep |= ~(is_regular | is_extended)
    return df[keep] if "date" not in df.columns else df[keep].reset_index(drop=True)


class _KeyPool:
    """Round-robins across every configured Twelve Data API key.

    Tracks each key's own requests-in-the-last-60s (a sliding window of
    monotonic timestamps) so concurrent fetches (backtest_routes' own
    thread pool, or a Scanner/Day Prep batch) spread evenly across all
    keys instead of hammering whichever one happens to be first, and
    BLOCK (sleeping, never dropping the request) once every key is at
    its per-minute cap rather than firing anyway and eating a 429.

    Does NOT track each key's daily credit cap (e.g. 800/day on Twelve
    Data's Basic tier) -- a big multi-symbol multi-year backtest could
    still exhaust that across a day even with per-minute pacing
    respected.

    Thread-safe (a single `threading.Lock` guards the round-robin
    cursor and every key's window) -- built for this process's own
    ThreadPoolExecutor-based concurrent fetches, not for coordinating
    rate limits across multiple separate server processes.
    """

    def __init__(self, keys: list[str], requests_per_minute: int):
        if not keys:
            raise TwelveDataError(
                "No Twelve Data API keys configured. Set at least one of TWELVEDATA_API_KEY_1 through "
                "TWELVEDATA_API_KEY_5 in backend/.env (see backend/.env.example)."
            )
        self.keys = keys
        self._limit = requests_per_minute
        self._lock = threading.Lock()
        self._next_index = 0
        self._recent_calls: dict[str, deque] = {key: deque() for key in keys}

    def __len__(self) -> int:
        return len(self.keys)

    def _prune(self, key: str, now: float) -> None:
        window = self._recent_calls[key]
        cutoff = now - _RATE_LIMIT_WINDOW_SECONDS
        while window and window[0] < cutoff:
            window.popleft()

    def acquire(self) -> str:
        """Block until a key has a free slot under its per-minute limit,
        reserve that slot, and return the key to use."""
        while True:
            with self._lock:
                now = time.monotonic()
                # Start from the round-robin cursor so load stays spread
                # evenly across keys instead of favoring keys[0].
                for offset in range(len(self.keys)):
                    idx = (self._next_index + offset) % len(self.keys)
                    key = self.keys[idx]
                    self._prune(key, now)
                    if len(self._recent_calls[key]) < self._limit:
                        self._recent_calls[key].append(now)
                        self._next_index = (idx + 1) % len(self.keys)
                        return key
                # Every key is at its per-minute cap -- sleep until the
                # earliest reserved slot ages out of the window, then
                # retry from the top rather than picking blind.
                soonest_free = min(window[0] for window in self._recent_calls.values())
                sleep_for = max(0.05, soonest_free + _RATE_LIMIT_WINDOW_SECONDS - now)
            time.sleep(sleep_for)

    def penalize(self, key: str) -> None:
        """Called after Twelve Data itself 429s a request made with
        `key` -- treat it as fully saturated for the next window
        regardless of our own local count, since the server's own
        limiter is the ground truth, not our estimate (a fresh process
        restart, a second app instance sharing the same key, etc. can
        all make our local count under-estimate real usage)."""
        with self._lock:
            now = time.monotonic()
            window = self._recent_calls[key]
            window.clear()
            window.extend([now] * self._limit)


# Cached per distinct key tuple (not a bare module-level singleton) so
# tests that monkeypatch settings.twelvedata_api_keys to a fake list get
# their own isolated pool/rate-state instead of sharing production's.
_pools: dict[tuple[str, ...], _KeyPool] = {}
_pools_lock = threading.Lock()


def _get_pool() -> _KeyPool:
    keys = tuple(settings.twelvedata_api_keys)
    pool = _pools.get(keys)
    if pool is None:
        with _pools_lock:
            pool = _pools.get(keys)
            if pool is None:
                pool = _KeyPool(list(keys), settings.twelvedata_requests_per_minute_per_key)
                _pools[keys] = pool
    return pool


def _is_rate_limited(status_code: int, body: dict) -> bool:
    # Twelve Data signals a rate limit either via a real HTTP 429, or
    # (observed in practice) HTTP 200 with a JSON error body carrying
    # its own "code": 429 -- check both rather than trusting either alone.
    return status_code == 429 or (body.get("status") == "error" and body.get("code") == 429)


def fetch_historical_bars(
    symbol: str,
    interval: str = "1min",
    outputsize: int = 5000,
    start_date: str | None = None,
    end_date: str | None = None,
    include_extended_hours: bool = False,
    include_overnight: bool = False,
) -> pd.DataFrame:
    """
    Fetch historical bars for `symbol` from Twelve Data and return a raw
    (not-yet-normalized) DataFrame with a "date" column plus lowercase
    open/high/low/close/volume, chronologically sorted -- ready for the
    same detect_columns -> normalize_ohlcv -> validate_ohlcv pipeline
    every bar consumer in this app runs it through.

    `interval` is one of Twelve Data's own strings, e.g. "1min", "5min",
    "15min", "1h", "1day". `outputsize` is the number of most-recent
    bars to return (max 5000 per request, 1 API credit per call).

    `include_extended_hours`/`include_overnight` default to False (the
    original, regular-hours-only behavior); see filter_by_session for
    the caveat on what Twelve Data actually returns.

    Picks an API key from the configured pool (see _KeyPool) for each
    attempt; a 429 from one key penalizes just that key and retries
    with another, up to once per configured key, before giving up.
    """
    pool = _get_pool()

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": min(outputsize, MAX_OUTPUTSIZE),  # see MAX_OUTPUTSIZE
        "format": "JSON",
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    last_rate_limit_error: TwelveDataError | None = None

    for _ in range(len(pool)):
        api_key = pool.acquire()
        try:
            resp = requests.get(
                f"{settings.twelvedata_base_url}/time_series",
                params={**params, "apikey": api_key},
                timeout=_TIMEOUT_SECONDS,
            )
            body = resp.json()
        except requests.RequestException as exc:
            # Not f"...{exc}" -- requests' HTTPError message embeds the full
            # request URL, including the apikey query param, which would
            # otherwise leak the credential into an API error response.
            status = exc.response.status_code if exc.response is not None else "unknown"
            raise TwelveDataError(f"Could not reach Twelve Data for '{symbol}' (HTTP {status}).") from exc

        if _is_rate_limited(resp.status_code, body):
            pool.penalize(api_key)
            last_rate_limit_error = TwelveDataError(
                f"Twelve Data rate-limited the key ending '...{api_key[-4:]}' fetching '{symbol}'."
            )
            continue

        if resp.status_code >= 400:
            raise TwelveDataError(f"Could not reach Twelve Data for '{symbol}' (HTTP {resp.status_code}).")

        if body.get("status") == "error":
            raise TwelveDataError(
                f"Twelve Data returned an error for '{symbol}': {body.get('message', 'unknown error')}"
            )

        values = body.get("values")
        if not values:
            raise TwelveDataError(
                f"Twelve Data returned no historical bars for '{symbol}'. Check the symbol and interval."
            )

        df = pd.DataFrame(values)
        df = df.rename(columns={"datetime": "date"})
        df["date"] = pd.to_datetime(df["date"])
        for col in ("open", "high", "low", "close", "volume"):
            df[col] = pd.to_numeric(df[col])

        # Twelve Data returns newest-first; the rest of the pipeline expects
        # chronological order.
        df = df.sort_values("date").reset_index(drop=True)

        if interval not in _DAILY_OR_COARSER_INTERVALS:
            df = filter_by_session(df, include_extended_hours, include_overnight)
        return df

    # Every configured key came back rate-limited on this attempt.
    raise last_rate_limit_error or TwelveDataError(
        f"Twelve Data rate-limited every configured key while fetching '{symbol}'."
    )
