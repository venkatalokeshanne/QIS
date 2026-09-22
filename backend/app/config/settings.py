"""
Application settings.

Centralizes everything environment-specific (storage paths, DB
location) so swapping SQLite -> PostgreSQL later, or moving storage to
S3, touches this one file plus the repository implementation — not
every module that needs a path.
"""

import json
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Anchored to backend/.env regardless of the process's cwd -- uvicorn's
    # --app-dir flag changes import resolution, not the working directory,
    # so a plain relative ".env" silently misses the file.
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    data_dir: Path = Path("./data")
    db_path: Path = Path("./data/app.db")

    # Plain string, not list[str]: pydantic-settings tries to JSON-decode
    # any env var bound to a list-typed field before validators ever run,
    # so a host dashboard's plain-text field (e.g. Render's) must contain
    # exact JSON array syntax or the app crashes on startup. Parsing this
    # ourselves in the property below accepts a bare URL or comma-separated
    # URLs too.
    cors_allowed_origins_env: str = Field(
        default="http://localhost:5173", validation_alias="CORS_ALLOWED_ORIGINS"
    )

    @property
    def cors_allowed_origins(self) -> list[str]:
        value = self.cors_allowed_origins_env.strip()
        if value.startswith("["):
            return json.loads(value)
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    # Twelve Data (twelvedata.com) -- the only market-data source in
    # this app (historical bars for backtesting, Scanner, Day Prep, and
    # Daily Levels); not used for account data or order placement.
    # Up to 5 separate subscriptions/API keys, round-robinned by
    # app.integrations.twelvedata_client to spread load and stay under
    # each key's own per-minute rate limit -- set as many of
    # TWELVEDATA_API_KEY_1..TWELVEDATA_API_KEY_5 as you have.
    twelvedata_api_key_1: str = ""
    twelvedata_api_key_2: str = ""
    twelvedata_api_key_3: str = ""
    twelvedata_api_key_4: str = ""
    twelvedata_api_key_5: str = ""
    # Single-key name the deploy docs used to give; still honoured so a
    # host configured that way keeps working.
    twelvedata_api_key: str = ""
    twelvedata_base_url: str = "https://api.twelvedata.com"

    # Tastytrade (market data only: extended-hours candles, VIX, earnings
    # dates) for the Strategy Selection Engine. Never used for orders.
    tastytrade_client_id: str = ""
    tastytrade_client_secret: str = ""
    tastytrade_refresh_token: str = ""
    tastytrade_base_url: str = "https://api.tastyworks.com"
    # Twelve Data's Basic (free) tier limit, per key -- override if you
    # upgrade plans. Daily credit caps (e.g. 800/day on Basic) are NOT
    # tracked here; only the per-minute pace is locally enforced.
    twelvedata_requests_per_minute_per_key: int = 8

    @property
    def twelvedata_api_keys(self) -> list[str]:
        keys = [
            key
            for key in (
                self.twelvedata_api_key,
                self.twelvedata_api_key_1,
                self.twelvedata_api_key_2,
                self.twelvedata_api_key_3,
                self.twelvedata_api_key_4,
                self.twelvedata_api_key_5,
            )
            if key
        ]
        return list(dict.fromkeys(keys))

    # How many separate OS processes run strategy computation
    # concurrently (see backtest_routes.py) -- each worker is a full
    # extra Python interpreter (pandas/numpy/the whole strategy
    # registry loaded again), real memory per worker, not just CPU.
    # Deliberately NOT os.cpu_count(): a container's reported core
    # count often doesn't reflect its actual resource allocation (e.g.
    # Render's free tier is ~0.1 vCPU / 512MB total), and over-
    # provisioning workers there risks an out-of-memory kill, worse
    # than running fewer workers slower. Override via env var on a
    # host that actually has the RAM/cores to spare.
    strategy_worker_processes: int = 2

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
