"""
Application settings.

Centralizes everything environment-specific (storage paths, DB
location) so swapping SQLite -> PostgreSQL later, or moving storage to
S3, touches this one file plus the repository implementation — not
every module that needs a path.
"""

from pathlib import Path

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
    dataset_storage_dir: Path = Path("./data/datasets")

    # Set (e.g. in production, to a free-tier hosted Postgres) to switch
    # DatasetRepository from local SQLite + local CSV files to Postgres
    # with the CSV content stored as a column -- no local disk writes at
    # all, so data survives hosts with ephemeral filesystems (e.g.
    # Render's free tier). Unset (the default) keeps the original
    # SQLite + local CSV behavior everywhere else, including all tests.
    database_url: str = ""

    cors_allowed_origins: list[str] = ["http://localhost:5173"]

    # Twelve Data (twelvedata.com), used only for pulling historical bars
    # into a dataset -- not for streaming or order placement.
    # Set TWELVEDATA_API_KEY in backend/.env (never commit the real key).
    twelvedata_api_key: str = ""
    twelvedata_base_url: str = "https://api.twelvedata.com"

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.dataset_storage_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
