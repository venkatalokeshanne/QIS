"""
Calibration Store.

Persists each calibrated ticker's TickerProfile (see
app.services.calibration_service) as one JSON file under
{settings.data_dir}/calibration/{symbol}.json -- the first real use of
settings.data_dir, which existed as an unused stub before this. One
file per ticker: human-inspectable/editable, and forcing a
recalibration is just deleting the file -- no database dependency for
"a few tickers," matching the rest of this app's stateless-by-default
design (nothing else here uses a database either; db_path is an
unused stub too).
"""

import dataclasses
import json
from pathlib import Path

from app.config.settings import settings
from app.services.calibration_service import TickerProfile


def _calibration_dir() -> Path:
    path = settings.data_dir / "calibration"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _profile_path(symbol: str) -> Path:
    return _calibration_dir() / f"{symbol.upper()}.json"


def save_profile(profile: TickerProfile) -> None:
    path = _profile_path(profile.symbol)
    path.write_text(json.dumps(dataclasses.asdict(profile), indent=2), encoding="utf-8")


def load_profile(symbol: str) -> TickerProfile | None:
    path = _profile_path(symbol)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return TickerProfile(**data)


def load_all_profiles() -> dict[str, TickerProfile]:
    profiles: dict[str, TickerProfile] = {}
    for path in _calibration_dir().glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        profile = TickerProfile(**data)
        profiles[profile.symbol] = profile
    return profiles
