"""Market light routes -- thin wrapper around app.services.market_light_service."""

from fastapi import APIRouter, Query

from app.services.market_light_service import get_market_light

router = APIRouter(prefix="/api/market-light", tags=["market-light"])


@router.get("")
def market_light(timeframe: str = Query("1D", description="1D, 1h or 15m")):
    return get_market_light(timeframe)
