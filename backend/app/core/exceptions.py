"""
Centralized exception hierarchy.

Services raise these; the API layer (app/main.py exception handlers)
is the ONLY place that translates them into HTTP status codes. This
keeps business logic free of any knowledge of HTTP.
"""


class AppError(Exception):
    """Base class for all application-level errors."""


class NotFoundError(AppError):
    """A requested resource (dataset, strategy, indicator...) doesn't exist."""


class DataValidationError(AppError):
    """Uploaded data failed validation. Carries a list of human-readable issues."""

    def __init__(self, message: str, issues: list[str] | None = None):
        super().__init__(message)
        self.issues = issues or []


class TwelveDataError(AppError):
    """Could not connect to, or fetch data from, the Twelve Data API."""

    def __init__(self, message: str, issues: list[str] | None = None):
        super().__init__(message)
        self.issues = issues or []


class TastytradeError(AppError):
    """Could not authenticate with, or fetch data from, the Tastytrade API."""

    def __init__(self, message: str, issues: list[str] | None = None):
        super().__init__(message)
        self.issues = issues or []
