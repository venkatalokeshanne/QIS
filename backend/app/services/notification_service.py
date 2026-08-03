"""
Notification Service.

Thin wrapper around Telegram's Bot API
(https://core.telegram.org/bots/api#sendmessage) -- the only
notification channel in this app (see app.services.poller, which
calls this on every new strategy signal and every Auto
Support/Resistance change).
"""

import logging

import requests

from app.config.settings import settings

_TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
_TIMEOUT_SECONDS = 10

logger = logging.getLogger("quant_platform")


def send_telegram_message(text: str) -> None:
    """
    Best-effort send: logs and swallows failures (missing settings,
    network errors, bad responses) rather than raising, so one bad
    send can't take down the poller loop for every other watch.
    """
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.debug("Telegram not configured (telegram_bot_token/telegram_chat_id unset) -- skipping send.")
        return

    url = _TELEGRAM_API_URL.format(token=settings.telegram_bot_token)
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        resp = requests.post(url, json=payload, timeout=_TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.RequestException:
        logger.exception("Failed to send Telegram message")
