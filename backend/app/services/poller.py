"""
Poller.

Background loop that periodically re-checks every active watch on its
own schedule (per-watch interval), calling signal_service.check_signal
and sending an Expo push through notification_service the moment a new
entry/exit event lands on the freshest bar. Runs as a single asyncio
task for the process lifetime (started/stopped from app.main's
lifespan) -- one task fans out to every watch rather than one task per
watch, so Twelve Data call volume stays bounded by each watch's own
interval regardless of how many watches exist.
"""

import asyncio
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.repositories.watch_repository import WatchRecord, WatchRepository
from app.services import notification_service, signal_service
from app.strategies.registry import get_strategy

logger = logging.getLogger("quant_platform")

_TICK_SECONDS = 30

_INTERVAL_SECONDS = {
    "1min": 60,
    "5min": 300,
    "15min": 900,
}

_NY_TZ = ZoneInfo("America/New_York")


def _is_market_hours(now_utc: datetime) -> bool:
    """Regular US equity session: 9:30-16:00 America/New_York, Mon-Fri."""
    now_ny = now_utc.astimezone(_NY_TZ)
    if now_ny.weekday() >= 5:
        return False
    open_time = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    close_time = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    return open_time <= now_ny <= close_time


def _is_due(watch: WatchRecord, now_utc: datetime) -> bool:
    if watch.last_checked_at is None:
        return True
    interval_seconds = _INTERVAL_SECONDS.get(watch.interval, 300)
    last_checked = datetime.fromisoformat(watch.last_checked_at)
    return (now_utc - last_checked).total_seconds() >= interval_seconds


def _format_notification(result: signal_service.SignalCheck) -> tuple[str, str]:
    display_name = get_strategy(result.strategy_name).metadata.display_name
    if result.event == "entry":
        title = f"{result.symbol} {result.direction.upper()} entry"
        body = f"{display_name} entered {result.direction} @ {result.price:.2f}"
    else:
        title = f"{result.symbol} exit"
        body = f"{display_name} exited ({result.exit_reason}) @ {result.price:.2f}"
    return title, body


class Poller:
    def __init__(self, repository: WatchRepository | None = None):
        self._repository = repository or WatchRepository()
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
        """Synchronous single pass over every due watch -- exposed (not
        private) so tests can call it directly without running the loop."""
        now_utc = datetime.now(timezone.utc)
        if not _is_market_hours(now_utc):
            return
        for watch in self._repository.list_all():
            if _is_due(watch, now_utc):
                self._check_watch(watch, now_utc)

    def _check_watch(self, watch: WatchRecord, now_utc: datetime) -> None:
        try:
            result = signal_service.check_signal(
                watch.symbol, watch.interval, watch.strategy_name, watch.strategy_params
            )
        except Exception:
            logger.exception("Signal check failed for watch %s (%s)", watch.id, watch.symbol)
            return

        now_iso = now_utc.isoformat()
        bar_time_iso = result.as_of.isoformat()
        already_notified = watch.last_notified_bar_time == bar_time_iso

        if result.event is not None and not already_notified:
            title, body = _format_notification(result)
            notification_service.send_push_notification(
                watch.expo_push_token,
                title,
                body,
                data={"watch_id": watch.id, "symbol": watch.symbol, "event": result.event},
            )
            self._repository.mark_checked(watch.id, now_iso, notified_bar_time=bar_time_iso)
        else:
            self._repository.mark_checked(watch.id, now_iso)
