"""
Poller.

Background loop that periodically re-checks every active level watch
(see level_watch_repository) for Auto Support/Resistance changes on a
fixed cadence, sending a Telegram message through notification_service
when they change. Runs as a single asyncio task for the process
lifetime (started/stopped from app.main's lifespan).

Signal watches (strategy buy/sell alerts) are NOT handled here anymore
-- see app.services.live_signal_engine, which detects those the moment
dxfeed reports a qualifying live bar instead of re-polling on a timer.
`is_market_hours` and `format_notification` below are public because
that module reuses both.
"""

import asyncio
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.repositories.level_watch_repository import LevelWatchRecord, LevelWatchRepository
from app.services import levels_service, notification_service, signal_service
from app.strategies.registry import get_strategy

logger = logging.getLogger("quant_platform")

_TICK_SECONDS = 30

# Level watches have no user-chosen interval (Auto Support/Resistance
# isn't tied to a timeframe the way strategy signals are) -- checked on
# a fixed cadence instead.
_LEVEL_WATCH_INTERVAL_SECONDS = 300

_NY_TZ = ZoneInfo("America/New_York")


def is_market_hours(now_utc: datetime) -> bool:
    """Regular US equity session: 9:30-16:00 America/New_York, Mon-Fri."""
    now_ny = now_utc.astimezone(_NY_TZ)
    if now_ny.weekday() >= 5:
        return False
    open_time = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    return open_time <= now_ny <= close_time


def _is_due(last_checked_at: str | None, interval_seconds: int, now_utc: datetime) -> bool:
    if last_checked_at is None:
        return True
    last_checked = datetime.fromisoformat(last_checked_at)
    return (now_utc - last_checked).total_seconds() >= interval_seconds


def _format_levels(levels: list[float]) -> list[str]:
    """2-decimal strings, not raw floats -- comparing these instead of
    the floats directly avoids false "changed" positives from
    indicator-recompute float noise."""
    return [f"{v:.2f}" for v in levels]


def format_notification(result: signal_service.SignalCheck) -> tuple[str, str]:
    display_name = get_strategy(result.strategy_name).metadata.display_name
    if result.event == "entry":
        title = f"{result.symbol} {result.direction.upper()} entry"
        body = f"{display_name} entered {result.direction} @ {result.price:.2f}"
    else:
        title = f"{result.symbol} exit"
        body = f"{display_name} exited ({result.exit_reason}) @ {result.price:.2f}"
    return title, body


class Poller:
    def __init__(self, level_watch_repository: LevelWatchRepository | None = None):
        self._level_watch_repository = level_watch_repository or LevelWatchRepository()
        self._task: asyncio.Task | None = None

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

    async def _run_loop(self) -> None:
        while True:
            try:
                await asyncio.to_thread(self.tick)
            except Exception:
                logger.exception("Poller tick failed")
            await asyncio.sleep(_TICK_SECONDS)

    def tick(self) -> None:
        """Synchronous single pass over every due level watch -- exposed
        (not private) so tests can call it directly without running the
        loop."""
        now_utc = datetime.now(timezone.utc)
        if not is_market_hours(now_utc):
            return
        for level_watch in self._level_watch_repository.list_all():
            if _is_due(level_watch.last_checked_at, _LEVEL_WATCH_INTERVAL_SECONDS, now_utc):
                self._check_level_watch(level_watch, now_utc)

    def _check_level_watch(self, level_watch: LevelWatchRecord, now_utc: datetime) -> None:
        try:
            levels = levels_service.get_daily_levels(level_watch.symbol)
        except Exception:
            logger.exception("Levels check failed for level watch %s (%s)", level_watch.id, level_watch.symbol)
            return

        now_iso = now_utc.isoformat()
        new_levels = levels.auto_support_resistance
        formatted_new = _format_levels(new_levels)
        formatted_old = _format_levels(level_watch.last_levels) if level_watch.last_levels is not None else None

        if formatted_new != formatted_old:
            message = f"*{level_watch.symbol} S/R updated*\n" + ", ".join(formatted_new)
            notification_service.send_telegram_message(message)
            self._level_watch_repository.update_levels(level_watch.id, new_levels, now_iso)
        else:
            self._level_watch_repository.mark_checked(level_watch.id, now_iso)
