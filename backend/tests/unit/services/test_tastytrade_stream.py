"""
Tests for app.services.tastytrade_stream.

_parse_feed_data and the cache-merge/subscribe logic are exercised
directly (no live socket) -- the connect/reconnect loop itself isn't
unit-tested here since it's a thin wrapper around websockets.connect
with nothing but I/O in it.
"""

import asyncio

from app.services.tastytrade_stream import QuoteSnapshot, TastytradeStream, _merge_quote, _parse_feed_data


def test_parse_feed_data_ignores_non_feed_data_messages():
    assert _parse_feed_data({"type": "AUTH_STATE", "state": "AUTHORIZED"}) == {}


def test_parse_feed_data_extracts_quote_fields():
    message = {
        "type": "FEED_DATA",
        "channel": 1,
        "data": [{"eventType": "Quote", "eventSymbol": "AAPL", "bidPrice": 150.1, "askPrice": 150.2}],
    }
    updates = _parse_feed_data(message)

    assert updates["AAPL"].bid == 150.1
    assert updates["AAPL"].ask == 150.2
    assert updates["AAPL"].last is None
    assert updates["AAPL"].updated_at is not None


def test_parse_feed_data_extracts_trade_fields_separately_from_quote():
    message = {
        "type": "FEED_DATA",
        "channel": 1,
        "data": [{"eventType": "Trade", "eventSymbol": "AAPL", "price": 150.15}],
    }
    updates = _parse_feed_data(message)

    assert updates["AAPL"].last == 150.15
    assert updates["AAPL"].bid is None
    assert updates["AAPL"].ask is None


def test_parse_feed_data_handles_multiple_symbols_in_one_message():
    message = {
        "type": "FEED_DATA",
        "data": [
            {"eventType": "Quote", "eventSymbol": "AAPL", "bidPrice": 150.0, "askPrice": 150.1},
            {"eventType": "Quote", "eventSymbol": "MSFT", "bidPrice": 300.0, "askPrice": 300.2},
        ],
    }
    updates = _parse_feed_data(message)

    assert set(updates) == {"AAPL", "MSFT"}
    assert updates["MSFT"].bid == 300.0


def test_parse_feed_data_ignores_unknown_event_types():
    message = {"type": "FEED_DATA", "data": [{"eventType": "Summary", "eventSymbol": "AAPL"}]}
    assert _parse_feed_data(message) == {}


def test_merge_quote_does_not_clobber_fields_absent_from_the_partial_update():
    existing = QuoteSnapshot(symbol="AAPL", bid=150.0, ask=150.1, last=150.05)
    # A Trade-only partial update (no bid/ask) must not wipe the
    # existing bid/ask -- only `last` should change.
    partial = QuoteSnapshot(symbol="AAPL", last=151.0)

    merged = _merge_quote(existing, "AAPL", partial)

    assert merged.bid == 150.0
    assert merged.ask == 150.1
    assert merged.last == 151.0


def test_merge_quote_creates_new_snapshot_when_none_exists():
    partial = QuoteSnapshot(symbol="TSLA", bid=200.0)
    merged = _merge_quote(None, "TSLA", partial)
    assert merged.symbol == "TSLA"
    assert merged.bid == 200.0


def test_get_latest_quote_returns_none_before_any_data():
    stream = TastytradeStream()
    assert stream.get_latest_quote("AAPL") is None


def test_get_latest_quote_is_case_insensitive():
    stream = TastytradeStream()
    stream._quotes["AAPL"] = QuoteSnapshot(symbol="AAPL", bid=1.0)
    assert stream.get_latest_quote("aapl").bid == 1.0


def test_subscribe_is_idempotent_and_does_not_touch_the_socket_when_already_subscribed():
    stream = TastytradeStream()
    stream._symbols.add("AAPL")
    stream._ws = object()  # any non-None sentinel; subscribe() must not call it for an already-subscribed symbol

    asyncio.run(stream.subscribe("AAPL"))

    assert stream._symbols == {"AAPL"}


def test_subscribe_before_connection_only_records_the_symbol():
    stream = TastytradeStream()
    asyncio.run(stream.subscribe("aapl"))
    assert stream._symbols == {"AAPL"}
    assert stream._ws is None
