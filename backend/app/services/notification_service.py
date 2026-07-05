"""
Notification Service.

Thin wrapper around Expo's push notification HTTP API
(https://docs.expo.dev/push-notifications/sending-notifications/) --
the free delivery mechanism for the mobile app's signal alerts. Expo's
endpoint is a stable public constant, not a credential, so it lives
here rather than in settings.
"""

import logging

import requests

_EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
_TIMEOUT_SECONDS = 10

logger = logging.getLogger("quant_platform")


def send_push_notification(expo_push_token: str, title: str, body: str, data: dict | None = None) -> None:
    """
    Best-effort send: logs and swallows failures rather than raising,
    so one bad/expired push token can't take down the poller loop for
    every other watch.
    """
    payload = {
        "to": expo_push_token,
        "title": title,
        "body": body,
        "sound": "default",
        "data": data or {},
    }
    try:
        resp = requests.post(_EXPO_PUSH_URL, json=payload, timeout=_TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to send Expo push notification to token %s", expo_push_token)
