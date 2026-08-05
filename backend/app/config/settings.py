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

    # Set (e.g. in production, to a free-tier hosted Postgres) to switch
    # WatchRepository from local SQLite to Postgres -- so watches survive
    # hosts with ephemeral filesystems (e.g. Render's free tier). Unset
    # (the default) keeps local SQLite everywhere else, including tests.
    database_url: str = ""

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

    # Tastytrade (tastytrade.com) -- the only market-data source in this
    # app now (live quotes/signals and historical bars for backtesting,
    # both via DXLink); not used for account data or order placement.
    # OAuth2 app credentials from Tastytrade's developer portal; set all
    # three in backend/.env (never commit the real values).
    tastytrade_client_id: str = ""
    tastytrade_client_secret: str = ""
    tastytrade_refresh_token: str = ""
    tastytrade_base_url: str = "https://api.tastyworks.com"

    # Telegram Bot API -- the only notification channel (see
    # app.services.notification_service). Message @BotFather to create
    # a bot and get telegram_bot_token; message the bot once, then hit
    # https://api.telegram.org/bot<token>/getUpdates to read chat.id
    # for telegram_chat_id.
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

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
