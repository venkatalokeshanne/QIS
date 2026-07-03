"""
Twelve Data historical bars client (https://twelvedata.com/docs).

Thin wrapper around Twelve Data's `/time_series` REST endpoint, used
only to pull historical OHLCV bars into the same normalized dataset
pipeline that CSV uploads go through (see app.data.loader's docstring
-- this is exactly the "broker loader" swap it anticipated). This does
NOT stream live data or place orders.

Requires TWELVEDATA_API_KEY set (backend/.env, or a real environment
variable of the same name) -- see backend/.env.example.
"""

import pandas as pd
import requests

from app.config.settings import settings
from app.core.exceptions import TwelveDataError

_TIMEOUT_SECONDS = 10


def fetch_historical_bars(
    symbol: str,
    interval: str = "1min",
    outputsize: int = 5000,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    """
    Fetch historical bars for `symbol` from Twelve Data and return a raw
    (not-yet-normalized) DataFrame with a "date" column plus lowercase
    open/high/low/close/volume -- the same shape app.data.loader.load_csv
    would produce -- so it can go through the exact same
    detect_columns -> normalize_ohlcv -> validate_ohlcv pipeline as an
    uploaded CSV.

    `interval` is one of Twelve Data's own strings, e.g. "1min", "5min",
    "15min", "1h", "1day". `outputsize` is the number of most-recent
    bars to return (max 5000 per request, 1 API credit per call).
    """
    if not settings.twelvedata_api_key:
        raise TwelveDataError(
            "TWELVEDATA_API_KEY is not set. Add it to backend/.env (see backend/.env.example)."
        )

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": settings.twelvedata_api_key,
        "format": "JSON",
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    try:
        resp = requests.get(f"{settings.twelvedata_base_url}/time_series", params=params, timeout=_TIMEOUT_SECONDS)
        resp.raise_for_status()
        body = resp.json()
    except requests.RequestException as exc:
        # Not f"...{exc}" -- requests' HTTPError message embeds the full
        # request URL, including the apikey query param, which would
        # otherwise leak the credential into an API error response.
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise TwelveDataError(f"Could not reach Twelve Data for '{symbol}' (HTTP {status}).") from exc

    if body.get("status") == "error":
        raise TwelveDataError(
            f"Twelve Data returned an error for '{symbol}': {body.get('message', 'unknown error')}"
        )

    values = body.get("values")
    if not values:
        raise TwelveDataError(
            f"Twelve Data returned no historical bars for '{symbol}'. Check the symbol and interval."
        )

    df = pd.DataFrame(values)
    df = df.rename(columns={"datetime": "date"})
    df["date"] = pd.to_datetime(df["date"])
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col])

    # Twelve Data returns newest-first; the rest of the pipeline expects
    # chronological order.
    return df.sort_values("date").reset_index(drop=True)
