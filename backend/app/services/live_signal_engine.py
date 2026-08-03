"""
Live Signal Engine.

Detects strategy buy/sell signals the moment dxfeed reports a
qualifying live bar, instead of re-polling on a timer the way
app.services.poller's old signal-watch loop did. One shared, long-lived
DXLink WebSocket subscribes to a live (never-closed) Candle feed per
distinct (symbol, interval) pair any active watch needs -- the exact
same event type and compound-symbol format
(app.integrations.tastytrade_client.build_candle_symbol) the one-shot
historical backfill already uses, so live bars and the cached
historical warm-up window share identical timestamp semantics with no
risk of the live-to-historical handoff looking like a different bar.

Connection lifecycle (one shared multiplexed socket, reconnect with
backoff, keepalive loop, start()/stop() via asyncio.create_task/
cancel()+await) mirrors app.services.poller.Poller and the earlier
(deleted) tastytrade_stream.py -- recovered from git history as the
known-working pattern for this app's DXLink usage.

Each (symbol, interval) pair keeps an in-memory cached DataFrame of
closed historical bars (fetched via tastytrade_client.fetch_historical_bars,
off the event loop via asyncio.to_thread since that function calls
asyncio.run() internally and cannot run on an already-running loop) --
every live Candle event swaps that DataFrame's last row for the
freshest live bar before re-running the strategy, throttled per pair so
a fast-updating candle doesn't trigger the full prepare->entries->exits
->simulate_trades pipeline on every single tick. "Is this a new signal"
uses the exact same app.services.signal_service.event_for_bar logic
the on-demand Live Signal tab check uses, and the same
last_notified_bar_time dedup field on WatchRecord -- just keyed off the
live candle's own timestamp instead of a poll-fetched one.

Level watches (Daily Levels S/R) are untouched -- see app.services.poller,
which still polls those on its own fixed cadence; they have no
per-timeframe live-bar concept the way signal watches do.
"""

import asyncio
import json
import logging
import time
from dataclasses import replace
from datetime import datetime, timezone

import pandas as pd
import websockets

from app.integrations import dxlink, tastytrade_client
from app.repositories.watch_repository import WatchRecord, WatchRepository
from app.services import notification_service, poller, signal_service
from app.strategies.execution import ExecutionConfig
from app.strategies.registry import get_strategy

logger = logging.getLogger("quant_platform")

_CHANNEL_CONTROL = 0
_CHANNEL_FEED = 1
_KEEPALIVE_INTERVAL_SECONDS = 30
_RECONNECT_DELAY_SECONDS = 5

# Minimum time between full strategy recomputes for the same
# (symbol, interval) pair -- bounds CPU cost if dxfeed streams rapid
# candle updates for a liquid symbol, while staying far more responsive
# than the old fixed per-interval poll.
_EVAL_THROTTLE_SECONDS = 2.0

# Keep the cached historical window from growing unbounded as live bars
# get appended over a long-running process.
_MAX_CACHED_BARS = signal_service.OUTPUTSIZE


class _PairState:
    __slots__ = ("historical_df", "last_eval_monotonic")

    def __init__(self, historical_df: pd.DataFrame):
        self.historical_df = historical_df
        self.last_eval_monotonic = 0.0


def parse_live_candle(event: dict) -> tuple[pd.Timestamp, dict]:
    """Same time/field parsing fetch_historical_bars uses, for one live
    Candle event instead of a whole backfill batch."""
    bar_time = (
        pd.to_datetime(int(event["time"]), unit="ms", utc=True)
        .tz_convert("America/New_York")
        .tz_localize(None)
    )
    ohlcv = {
        "open": float(event["open"]),
        "high": float(event["high"]),
        "low": float(event["low"]),
        "close": float(event["close"]),
        "volume": float(event["volume"]),
    }
    return bar_time, ohlcv


def merge_live_candle(historical_df: pd.DataFrame, bar_time: pd.Timestamp, ohlcv: dict) -> pd.DataFrame:
    """Returns a NEW dataframe (never mutates historical_df) with the
    live candle's OHLCV written to `bar_time` -- updates that row in
    place if it's the same still-forming bar as last time, or appends
    a new row if the bar has rolled over. Trimmed to _MAX_CACHED_BARS
    so the cache doesn't grow unbounded over a long-running process."""
    df = historical_df.copy()
    for col, value in ohlcv.items():
        df.loc[bar_time, col] = value
    df = df.sort_index()
    if len(df) > _MAX_CACHED_BARS:
        df = df.iloc[-_MAX_CACHED_BARS:]
    return df


class LiveSignalEngine:
    def __init__(self, repository: WatchRepository | None = None):
        self._repository = repository or WatchRepository()
        self._task: asyncio.Task | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._ws = None
        # (symbol, interval) -> _PairState
        self._pairs: dict[tuple[str, str], _PairState] = {}
        # dxfeed compound symbol -> (symbol, interval), so an incoming
        # event (keyed by its own eventSymbol) can be routed back.
        self._symbol_to_pair: dict[str, tuple[str, str]] = {}
        self._eval_tasks: set[asyncio.Task] = set()

    # --- lifecycle ------------------------------------------------------

    def start(self) -> None:
        if self._task is None:
            self._loop = asyncio.get_running_loop()
            self._task = asyncio.create_task(self._run_loop())
            asyncio.create_task(self._bootstrap_existing_watches())

    async def _bootstrap_existing_watches(self) -> None:
        """Resume watching whatever watches already existed before this
        process (re)started -- watch_routes.py's on_watch_created only
        fires for NEW watches created while the engine is already up."""
        try:
            watches = await asyncio.to_thread(self._repository.list_all)
        except Exception:
            logger.exception("Could not list existing watches on startup")
            return
        for watch in watches:
            await self._ensure_subscribed(watch.symbol, watch.interval)

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        for eval_task in list(self._eval_tasks):
            eval_task.cancel()
        self._loop = None

    async def _run_loop(self) -> None:
        while True:
            try:
                await self._connect_and_listen()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Live signal engine connection failed; reconnecting")
            self._ws = None
            await asyncio.sleep(_RECONNECT_DELAY_SECONDS)

    async def _connect_and_listen(self) -> None:
        quote_token = await asyncio.to_thread(tastytrade_client.get_quote_token)
        url = quote_token["dxlink-url"]

        async with websockets.connect(url) as ws:
            self._ws = ws
            await dxlink.handshake(ws, quote_token["token"], {"Candle": tastytrade_client.CANDLE_FIELDS})
            logger.info("Live signal engine connected to DXLink")
            # (Re)connect resync: refresh every pair's historical warm-up
            # window (covers whatever was missed while disconnected) and
            # resubscribe to all of them on the new socket.
            await self._resync_all_pairs()
            if self._symbol_to_pair:
                await self._send_subscription(ws, list(self._symbol_to_pair), add=True)
                logger.info("Live signal engine resubscribed to %s", sorted(self._symbol_to_pair))

            keepalive_task = asyncio.create_task(self._keepalive_loop(ws))
            try:
                async for raw in ws:
                    message = json.loads(raw)
                    if message.get("type") != "FEED_DATA":
                        continue
                    for event in message.get("data", []):
                        if event.get("eventType") == "Candle":
                            self._handle_candle_event(event)
            finally:
                keepalive_task.cancel()

    async def _keepalive_loop(self, ws) -> None:
        while True:
            await asyncio.sleep(_KEEPALIVE_INTERVAL_SECONDS)
            await ws.send(json.dumps({"type": "KEEPALIVE", "channel": _CHANNEL_CONTROL}))

    async def _send_subscription(self, ws, compound_symbols: list[str], *, add: bool) -> None:
        key = "add" if add else "remove"
        await ws.send(json.dumps({
            "type": "FEED_SUBSCRIPTION",
            "channel": _CHANNEL_FEED,
            key: [{"type": "Candle", "symbol": s} for s in compound_symbols],
        }))

    # --- watch lifecycle (called from sync FastAPI routes) ---------------

    def on_watch_created(self, watch: WatchRecord) -> None:
        """Schedules the subscribe work onto the engine's own event loop
        rather than blocking the calling (threadpool-executed) route on
        the historical backfill. No-op if the engine isn't running
        (e.g. under test)."""
        if self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(self._ensure_subscribed(watch.symbol, watch.interval), self._loop)

    def on_watch_deleted(self, watch: WatchRecord) -> None:
        if self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(self._maybe_unsubscribe(watch.symbol, watch.interval), self._loop)

    async def _ensure_subscribed(self, symbol: str, interval: str) -> None:
        pair = (symbol, interval)
        if pair in self._pairs:
            return
        try:
            historical_df = await asyncio.to_thread(signal_service.fetch_symbol_bars, symbol, interval)
        except Exception:
            logger.exception("Could not fetch initial historical bars for %s %s", symbol, interval)
            return

        self._pairs[pair] = _PairState(historical_df)
        periodicity = tastytrade_client.periodicity_for_interval(interval)
        compound_symbol = tastytrade_client.build_candle_symbol(symbol, periodicity)
        self._symbol_to_pair[compound_symbol] = pair

        if self._ws is not None:
            await self._send_subscription(self._ws, [compound_symbol], add=True)
            logger.info("Live signal engine subscribed to %s (%d warm-up bars)", compound_symbol, len(historical_df))
        else:
            logger.info(
                "Live signal engine cached %s (%d warm-up bars); will subscribe once connected",
                compound_symbol,
                len(historical_df),
            )

    async def _maybe_unsubscribe(self, symbol: str, interval: str) -> None:
        pair = (symbol, interval)
        if pair not in self._pairs:
            return
        watches = await asyncio.to_thread(self._repository.list_all)
        still_needed = any(w.symbol == symbol and w.interval == interval for w in watches)
        if still_needed:
            return

        del self._pairs[pair]
        compound_symbol = next((s for s, p in self._symbol_to_pair.items() if p == pair), None)
        if compound_symbol is not None:
            del self._symbol_to_pair[compound_symbol]
            if self._ws is not None:
                await self._send_subscription(self._ws, [compound_symbol], add=False)

    async def _resync_all_pairs(self) -> None:
        for symbol, interval in list(self._pairs):
            try:
                historical_df = await asyncio.to_thread(signal_service.fetch_symbol_bars, symbol, interval)
            except Exception:
                logger.exception("Resync failed for %s %s -- keeping previously cached bars", symbol, interval)
                continue
            state = self._pairs.get((symbol, interval))
            if state is not None:
                state.historical_df = historical_df

    # --- live candle handling --------------------------------------------

    def _handle_candle_event(self, event: dict) -> None:
        if not tastytrade_client.is_real_candle(event):
            return
        pair = self._symbol_to_pair.get(event.get("eventSymbol"))
        if pair is None:
            return
        state = self._pairs.get(pair)
        if state is None:
            return

        now = time.monotonic()
        if now - state.last_eval_monotonic < _EVAL_THROTTLE_SECONDS:
            return
        state.last_eval_monotonic = now

        eval_task = asyncio.create_task(self._evaluate_pair(pair, event))
        self._eval_tasks.add(eval_task)
        eval_task.add_done_callback(self._eval_tasks.discard)

    async def _evaluate_pair(self, pair: tuple[str, str], event: dict) -> None:
        if not poller.is_market_hours(datetime.now(timezone.utc)):
            return
        state = self._pairs.get(pair)
        if state is None:
            return

        symbol, interval = pair
        bar_time, ohlcv = parse_live_candle(event)
        df = merge_live_candle(state.historical_df, bar_time, ohlcv)
        state.historical_df = df

        watches = await asyncio.to_thread(self._repository.list_all)
        matching = [w for w in watches if w.symbol == symbol and w.interval == interval]
        for watch in matching:
            await self._evaluate_watch(watch, df, bar_time)

    async def _evaluate_watch(self, watch: WatchRecord, df: pd.DataFrame, bar_time: pd.Timestamp) -> None:
        try:
            event, direction, exit_reason = await asyncio.to_thread(self._run_strategy, watch, df, bar_time)
        except Exception:
            logger.exception("Live signal check failed for watch %s (%s)", watch.id, watch.symbol)
            return

        now_iso = datetime.now(timezone.utc).isoformat()
        bar_time_iso = bar_time.isoformat()
        already_notified = watch.last_notified_bar_time == bar_time_iso

        if event is not None and not already_notified:
            check = signal_service.SignalCheck(
                symbol=watch.symbol,
                interval=watch.interval,
                strategy_name=watch.strategy_name,
                as_of=bar_time,
                price=float(df["close"].iloc[-1]),
                event=event,
                direction=direction,
                exit_reason=exit_reason,
            )
            title, body = poller.format_notification(check)
            notification_service.send_telegram_message(f"*{title}*\n{body}")
            await asyncio.to_thread(self._repository.mark_checked, watch.id, now_iso, notified_bar_time=bar_time_iso)
        else:
            await asyncio.to_thread(self._repository.mark_checked, watch.id, now_iso)

    @staticmethod
    def _run_strategy(watch: WatchRecord, df: pd.DataFrame, bar_time: pd.Timestamp):
        strategy = get_strategy(watch.strategy_name)
        params = strategy.validate_params(watch.strategy_params)
        # The execution config snapshotted at watch-creation time (see
        # WatchRepository's docstring) -- falls back to bare defaults
        # for watches created before that snapshot existed.
        base_config = ExecutionConfig(**watch.execution_settings) if watch.execution_settings else ExecutionConfig()
        execution_config = replace(base_config, force_close_at_session_end=False)
        trades = strategy.run(df, params, execution_config)
        return signal_service.event_for_bar(trades, bar_time)


# Module-level singleton, same pattern as app.services.poller's own
# Poller instance in app.main -- lifespan starts/stops this exact
# instance, and watch_routes.py notifies it on watch create/delete.
engine = LiveSignalEngine()
