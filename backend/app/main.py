"""
Application entrypoint.

This is the ONLY place that translates internal AppError exceptions
into HTTP responses (centralized exception handling), and the only
place that assembles routers. Run with:
    uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import backtest_routes, catalog_routes, levels_routes, signal_routes, watch_routes
from app.config.settings import settings
from app.core.exceptions import AppError, DataValidationError, NotFoundError, TastytradeError
from app.services.poller import Poller
from app.strategies.registry import discover_strategies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quant_platform")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_dirs()
    discover_strategies()
    poller = Poller()
    poller.start()
    yield
    await poller.stop()


app = FastAPI(title="Quant Strategy Research Platform API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog_routes.router)
app.include_router(backtest_routes.router)
app.include_router(levels_routes.router)
app.include_router(watch_routes.router)
app.include_router(signal_routes.router)


@app.exception_handler(NotFoundError)
def handle_not_found(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DataValidationError)
def handle_validation_error(request: Request, exc: DataValidationError):
    return JSONResponse(status_code=422, content={"detail": str(exc), "issues": exc.issues})


@app.exception_handler(TastytradeError)
def handle_tastytrade_error(request: Request, exc: TastytradeError):
    return JSONResponse(status_code=502, content={"detail": str(exc), "issues": exc.issues})


@app.exception_handler(AppError)
def handle_generic_app_error(request: Request, exc: AppError):
    logger.exception("Unhandled AppError")
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
