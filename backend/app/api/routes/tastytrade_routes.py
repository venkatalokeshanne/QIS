"""Tastytrade live-quote routes -- thin wrapper around app.services.tastytrade_stream."""

from fastapi import APIRouter

from app.api.schemas.tastytrade_schemas import TastytradeQuoteResponse
from app.services.tastytrade_stream import stream

router = APIRouter(prefix="/api/tastytrade", tags=["tastytrade"])


@router.get("/quote/{symbol}", response_model=TastytradeQuoteResponse)
async def get_quote(symbol: str):
    symbol = symbol.upper()
    await stream.subscribe(symbol)
    snapshot = stream.get_latest_quote(symbol)

    if snapshot is None:
        # Freshly subscribed -- streaming takes a moment to populate.
        # Not an error: the caller should just poll again shortly.
        return TastytradeQuoteResponse(symbol=symbol, bid=None, ask=None, last=None, updated_at=None, available=False)

    return TastytradeQuoteResponse(
        symbol=snapshot.symbol,
        bid=snapshot.bid,
        ask=snapshot.ask,
        last=snapshot.last,
        updated_at=snapshot.updated_at,
        available=True,
    )
