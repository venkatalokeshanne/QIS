"""
Shared low-level DXLink protocol helpers.

Used by one-shot historical-bar fetches
(app.integrations.tastytrade_client.fetch_historical_bars) -- kept
separate from that module so the handshake-ordering fix below (see its
docstring) is easy to find and reuse if another DXLink consumer is
added later.
"""

import json


async def handshake(
    ws,
    quote_token: str,
    accept_event_fields: dict,
    *,
    channel_control: int = 0,
    channel_feed: int = 1,
) -> None:
    """
    Perform the SETUP -> AUTH -> CHANNEL_REQUEST -> FEED_SETUP sequence.

    Confirmed against a live connection: the server rejects
    CHANNEL_REQUEST/FEED_SETUP with {"error":"BAD_ACTION","message":
    "AUTH step missing"} if sent before AUTH_STATE reaches AUTHORIZED,
    so this blocks on that -- draining the intervening SETUP ack and
    the initial UNAUTHORIZED state -- before proceeding.
    """
    await ws.send(json.dumps({
        "type": "SETUP",
        "channel": channel_control,
        "version": "0.1-quant-platform",
        "keepaliveTimeout": 60,
        "acceptKeepaliveTimeout": 60,
    }))
    await ws.send(json.dumps({"type": "AUTH", "channel": channel_control, "token": quote_token}))

    while True:
        message = json.loads(await ws.recv())
        if message.get("type") == "AUTH_STATE" and message.get("state") == "AUTHORIZED":
            break

    await ws.send(json.dumps({
        "type": "CHANNEL_REQUEST",
        "channel": channel_feed,
        "service": "FEED",
        "parameters": {"contract": "AUTO"},
    }))
    await ws.recv()  # CHANNEL_OPENED

    await ws.send(json.dumps({
        "type": "FEED_SETUP",
        "channel": channel_feed,
        "acceptDataFormat": "FULL",
        "acceptEventFields": accept_event_fields,
    }))
    await ws.recv()  # FEED_CONFIG
