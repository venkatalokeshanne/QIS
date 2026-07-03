# Quant Strategy Research Platform

A research platform for discovering which intraday trading strategies perform
best on historical data. See individual module docstrings for architecture
rationale — every Indicator, Filter, Strategy, and Metric is self-documenting.

## Architecture at a glance

```
backend/
  app/
    domain/interfaces/   # Indicator, Filter, Strategy, Metric contracts
    core/                # generic Registry (auto-discovery), exceptions
    indicators/          # one file per indicator, self-registering
    filters/              # one file per filter, self-registering
    strategies/           # one FOLDER per strategy, self-registering
    metrics/              # one file per metric, self-registering
    ranking/               # configurable weighted scoring across metrics
    data/                  # CSV load -> column detect -> normalize -> validate
    repositories/          # SQLite metadata + CSV storage for datasets
    services/               # orchestration (dataset upload, strategy runner)
    api/                    # FastAPI routes + pydantic schemas (thin, no logic)
  tests/                    # 102 tests, unit + integration, all passing

frontend/
  src/
    api/                   # axios client + one module per resource + React Query hooks
    store/                 # Zustand store for cross-page research workflow state
    components/            # reusable primitives (Card, Button, DataTable, ScoreBar...)
    pages/                 # Dashboard, Upload, Datasets, Strategy Library,
                            # Run Backtests, Results, Compare, Saved Research, Settings
    styles/tokens.css       # design token system (single source of truth)
```

## Running it

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173 (Vite proxies `/api` to the backend automatically —
see `vite.config.js`)

### Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
```

## Extending the platform

- **New indicator**: add one file to `app/indicators/`, decorate the class with
  `@indicator_registry.register("name")`. Nothing else changes.
- **New filter**: same pattern, in `app/filters/`.
- **New strategy**: add one folder to `app/strategies/<name>/` containing a
  `strategy.py` with metadata + entry/exit logic, decorated with
  `@strategy_registry.register("name")`. It composes existing indicators —
  it should never reimplement indicator math.
- **New metric**: add one file to `app/metrics/`, implementing `calculate(context)`.
  It automatically appears in every results table and is available to the
  Ranking Engine's configurable weights.
- **New frontend page**: add to `src/pages/`, wire into `src/App.jsx`'s routes
  and `src/components/Layout.jsx`'s nav list.

## What's built vs. what's next

Built: Indicator System, Filter System, Strategy System (ORB, EMA Cross),
Metrics Engine (14 metrics), Ranking Engine (configurable weighted scoring),
Data Engine (CSV upload/validation), full REST API, and a complete React
frontend covering the research workflow end-to-end.

Anticipated but not yet built (per the original architecture brief, and
possible without redesign): parameter optimization, walk-forward analysis,
Monte Carlo simulation, multi-timeframe testing, portfolio backtesting,
additional data source adapters (Polygon/Alpaca/IBKR), PostgreSQL migration.
