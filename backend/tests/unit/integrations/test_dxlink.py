"""
Tests for app.integrations.dxlink.handshake.

Regression guard for a bug found against a live connection this
session: Tastytrade's DXLink server rejects CHANNEL_REQUEST/FEED_SETUP
with {"error":"BAD_ACTION","message":"AUTH step missing"} if sent
before AUTH_STATE reaches AUTHORIZED. The fake WebSocket below encodes
that same ordering constraint (raising if violated), so a regression in
handshake() fails loudly here instead of only showing up live.
"""

import asyncio
import json

from app.integrations import dxlink


class _FakeDXLinkWS:
    def __init__(self, recv_queue):
        self._recv_queue = list(recv_queue)
        self.sent = []
        self._authorized = False

    async def send(self, message):
        msg = json.loads(message)
        self.sent.append(msg)
        if msg["type"] in ("CHANNEL_REQUEST", "FEED_SETUP") and not self._authorized:
            raise AssertionError(f"{msg['type']} sent before AUTH_STATE reached AUTHORIZED")

    async def recv(self):
        raw = self._recv_queue.pop(0)
        parsed = json.loads(raw)
        if parsed.get("type") == "AUTH_STATE" and parsed.get("state") == "AUTHORIZED":
            self._authorized = True
        return raw


def test_handshake_sends_setup_and_auth_immediately_but_waits_to_proceed():
    recv_queue = [
        json.dumps({"type": "SETUP", "channel": 0}),
        json.dumps({"type": "AUTH_STATE", "channel": 0, "state": "UNAUTHORIZED"}),
        json.dumps({"type": "AUTH_STATE", "channel": 0, "state": "AUTHORIZED"}),
        json.dumps({"type": "CHANNEL_OPENED", "channel": 1}),
        json.dumps({"type": "FEED_CONFIG", "channel": 1}),
    ]
    ws = _FakeDXLinkWS(recv_queue)

    asyncio.run(dxlink.handshake(ws, "quote-token", {"Quote": ["eventType"]}))

    sent_types = [m["type"] for m in ws.sent]
    assert sent_types == ["SETUP", "AUTH", "CHANNEL_REQUEST", "FEED_SETUP"]
    assert ws.sent[1]["token"] == "quote-token"
    assert ws.sent[3]["acceptEventFields"] == {"Quote": ["eventType"]}


def test_handshake_drains_multiple_unauthorized_states_before_proceeding():
    recv_queue = [
        json.dumps({"type": "SETUP", "channel": 0}),
        json.dumps({"type": "AUTH_STATE", "channel": 0, "state": "UNAUTHORIZED"}),
        json.dumps({"type": "AUTH_STATE", "channel": 0, "state": "UNAUTHORIZED"}),
        json.dumps({"type": "AUTH_STATE", "channel": 0, "state": "UNAUTHORIZED"}),
        json.dumps({"type": "AUTH_STATE", "channel": 0, "state": "AUTHORIZED"}),
        json.dumps({"type": "CHANNEL_OPENED", "channel": 1}),
        json.dumps({"type": "FEED_CONFIG", "channel": 1}),
    ]
    ws = _FakeDXLinkWS(recv_queue)

    asyncio.run(dxlink.handshake(ws, "quote-token", {"Candle": ["eventType"]}))

    assert [m["type"] for m in ws.sent] == ["SETUP", "AUTH", "CHANNEL_REQUEST", "FEED_SETUP"]


def test_handshake_uses_custom_channels():
    recv_queue = [
        json.dumps({"type": "SETUP", "channel": 5}),
        json.dumps({"type": "AUTH_STATE", "channel": 5, "state": "AUTHORIZED"}),
        json.dumps({"type": "CHANNEL_OPENED", "channel": 9}),
        json.dumps({"type": "FEED_CONFIG", "channel": 9}),
    ]
    ws = _FakeDXLinkWS(recv_queue)

    asyncio.run(dxlink.handshake(ws, "tok", {"Quote": []}, channel_control=5, channel_feed=9))

    assert ws.sent[0]["channel"] == 5
    assert ws.sent[1]["channel"] == 5
    assert ws.sent[2]["channel"] == 9
    assert ws.sent[3]["channel"] == 9
