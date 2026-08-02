"""
Tastytrade DXLink live-quote streaming client.

Maintains one persistent WebSocket connection to Tastytrade's DXLink
feed for the app's lifetime (started/stopped from app.main's lifespan,
the same pattern app.services.poller.Poller uses for its background
asyncio task), subscribing to Quote/Trade events for whatever symbols
callers have asked about and caching the latest snapshot per symbol in
memory so a request never has to wait on the socket.

Message parsing (_parse_feed_data) is a pure function, deliberately
kept separate from the connect/reconnect loop, so it's testable without
a live socket or credentials.

DXLink handshake (SETUP -> AUTH -> CHANNEL_REQUEST -> FEED_SETUP ->
FEED_SUBSCRIPTION) is validated against a live connection: the server
rejects CHANNEL_REQUEST/FEED_SETUP sent before AUTH_STATE reaches
AUTHORIZED, so _handshake blocks on that before proceeding (see its
docstring/comments). Uses "FULL" data format (keyed dicts) rather than
"COMPACT" (positional arrays) -- slightly more bandwidth, but avoids
hardcoding field order.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import websockets

from app.integrations import tastytrade_client

logger = logging.getLogger("quant_platform")

_CHANNEL_CONTROL = 0
_CHANNEL_FEED = 1
_KEEPALIVE_INTERVAL_SECONDS = 30
_RECONNECT_DELAY_SECONDS = 5
_EVENT_TYPES = ("Quote", "Trade")


@dataclass
class QuoteSnapshot:
    symbol: str
    bid: float | None = None
    ask: float | None = None
    last: float | None = None
    updated_at: datetime | None = None


def _parse_feed_data(message: dict) -> dict[str, QuoteSnapshot]:
    """
    Extract per-symbol Quote/Trade fields from one FEED_DATA message.

    Returns PARTIAL snapshots -- only the fields that message actually
    carried are set; a Quote event never carries `last`, a Trade event
    never carries `bid`/`ask`. The caller merges these into its
    persistent cache rather than overwriting unrelated fields.
    """
    updates: dict[str, QuoteSnapshot] = {}
    if message.get("type") != "FEED_DATA":
        return updates

    for event in message.get("data", []):
        symbol = event.get("eventSymbol")
        event_type = event.get("eventType")
        if not symbol or event_type not in _EVENT_TYPES:
            continue

        snapshot = updates.setdefault(symbol, QuoteSnapshot(symbol=symbol))
        if event_type == "Quote":
            snapshot.bid = event.get("bidPrice", snapshot.bid)
            snapshot.ask = event.get("askPrice", snapshot.ask)
        elif event_type == "Trade":
            snapshot.last = event.get("price", snapshot.last)
        snapshot.updated_at = datetime.now(timezone.utc)

    return updates


def _merge_quote(existing: QuoteSnapshot | None, symbol: str, partial: QuoteSnapshot) -> QuoteSnapshot:
    merged = existing or QuoteSnapshot(symbol=symbol)
    merged.bid = partial.bid if partial.bid is not None else merged.bid
    merged.ask = partial.ask if partial.ask is not None else merged.ask
    merged.last = partial.last if partial.last is not None else merged.last
    merged.updated_at = partial.updated_at
    return merged


class TastytradeStream:
    def __init__(self):
        self._task: asyncio.Task | None = None
        self._symbols: set[str] = set()
        self._quotes: dict[str, QuoteSnapshot] = {}
        self._ws = None

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    def get_latest_quote(self, symbol: str) -> QuoteSnapshot | None:
        return self._quotes.get(symbol.upper())

    async def subscribe(self, symbol: str) -> None:
        symbol = symbol.upper()
        if symbol in self._symbols:
            return
        self._symbols.add(symbol)
        if self._ws is not None:
            await self._send_subscription(self._ws, [symbol])

    async def _run_loop(self) -> None:
        while True:
            try:
                await self._connect_and_listen()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Tastytrade DXLink connection failed; reconnecting")
            self._ws = None
            await asyncio.sleep(_RECONNECT_DELAY_SECONDS)

    async def _connect_and_listen(self) -> None:
        quote_token = await asyncio.to_thread(tastytrade_client.get_quote_token)
        url = quote_token["dxlink-url"]

        async with websockets.connect(url) as ws:
            self._ws = ws
            await self._handshake(ws, quote_token["token"])
            if self._symbols:
                await self._send_subscription(ws, sorted(self._symbols))

            keepalive_task = asyncio.create_task(self._keepalive_loop(ws))
            try:
                async for raw in ws:
                    message = json.loads(raw)
                    updates = _parse_feed_data(message)
                    for symbol, partial in updates.items():
                        self._quotes[symbol] = _merge_quote(self._quotes.get(symbol), symbol, partial)
            finally:
                keepalive_task.cancel()

    async def _handshake(self, ws, quote_token: str) -> None:
        await ws.send(json.dumps({
            "type": "SETUP",
            "channel": _CHANNEL_CONTROL,
            "version": "0.1-quant-platform",
            "keepaliveTimeout": 60,
            "acceptKeepaliveTimeout": 60,
        }))
        await ws.send(json.dumps({"type": "AUTH", "channel": _CHANNEL_CONTROL, "token": quote_token}))

        # Confirmed against a live connection: the server rejects
        # CHANNEL_REQUEST/FEED_SETUP with {"error":"BAD_ACTION","message":
        # "AUTH step missing"} if sent before AUTH_STATE reaches
        # AUTHORIZED. This drains the intervening SETUP ack and the
        # initial UNAUTHORIZED state before proceeding.
        while True:
            message = json.loads(await ws.recv())
            if message.get("type") == "AUTH_STATE" and message.get("state") == "AUTHORIZED":
                break

        await ws.send(json.dumps({
            "type": "CHANNEL_REQUEST",
            "channel": _CHANNEL_FEED,
            "service": "FEED",
            "parameters": {"contract": "AUTO"},
        }))
        await ws.recv()  # CHANNEL_OPENED

        await ws.send(json.dumps({
            "type": "FEED_SETUP",
            "channel": _CHANNEL_FEED,
            "acceptDataFormat": "FULL",
            "acceptEventFields": {
                "Quote": ["eventType", "eventSymbol", "bidPrice", "askPrice"],
                "Trade": ["eventType", "eventSymbol", "price"],
            },
        }))
        await ws.recv()  # FEED_CONFIG

    async def _send_subscription(self, ws, symbols: list[str]) -> None:
        add = [{"type": event_type, "symbol": symbol} for symbol in symbols for event_type in _EVENT_TYPES]
        await ws.send(json.dumps({"type": "FEED_SUBSCRIPTION", "channel": _CHANNEL_FEED, "add": add}))

    async def _keepalive_loop(self, ws) -> None:
        while True:
            await asyncio.sleep(_KEEPALIVE_INTERVAL_SECONDS)
            await ws.send(json.dumps({"type": "KEEPALIVE", "channel": _CHANNEL_CONTROL}))


# Module-level singleton, same pattern as tastytrade_client.session --
# app.main's lifespan starts/stops this exact instance, and
# tastytrade_routes reads from it, so both sides share one connection
# and one quote cache rather than each holding their own.
stream = TastytradeStream()
