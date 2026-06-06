# Smart Energy Consumption Monitoring System

A FastAPI-based platform for monitoring household electricity usage, with smart meter simulation, automated alerts, analytics, and a built-in web dashboard.

## Features

- Household and smart meter registration
- Meter reading ingestion via REST API
- Automatic alert generation for high usage and consumption spikes
- Monthly usage summaries and bill estimation
- Single-page web dashboard (Bootstrap 5) served directly from FastAPI
- Python-based simulator for generating realistic meter readings
- SQLite for local development, PostgreSQL via `DATABASE_URL`
- Alembic migrations for schema management
- Pytest test suite

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Uvicorn |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Database | SQLite (dev), PostgreSQL (prod) |
| Analytics | Pandas, NumPy |
| Frontend | Bootstrap 5 (CDN) |
| Simulation | Python + requests |
| Testing | Pytest |

## Project Structure

```
app/
├── routers/        # REST endpoints (households, meters, readings, alerts, reports)
├── services/       # Alert detection and analytics logic
├── views/          # Serves the single-page dashboard
├── models.py       # SQLAlchemy models
├── schemas.py      # Pydantic schemas
├── database.py     # DB session and engine
└── main.py         # App entry point
templates/index.html  # Single-page Bootstrap dashboard
alembic/            # Migration versions
simulator/          # Smart meter reading generator CLI
tests/              # Pytest suite
create_tables.py    # Quick local database bootstrap
run.py              # Shortcut to start the server
```

## Requirements

- Python 3.10+
- pip

## Quick Start

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Set up the database

```powershell
alembic upgrade head
```

Or for a quick local bootstrap:

```powershell
python create_tables.py
```

### 4. Start the server

```powershell
uvicorn app.main:app --reload --port 8000
```

### 5. Open the dashboard

- **Web UI:** `http://127.0.0.1:8000`
- **Swagger UI:** `http://127.0.0.1:8000/docs`

## Dashboard

All functionality is in a single page at `/`:

- Stat cards — households, meters, open/resolved alerts
- Households — list and add
- Smart Meters — list and register
- Post Reading — submit a meter reading
- Bill Estimate & Report — select a household to see kWh totals and estimated bill
- Alerts — list with resolve button

## API Overview

### Health

| Method | Route | Description |
|---|---|---|
| GET | `/api/status` | Health check |

### Households

| Method | Route | Description |
|---|---|---|
| POST | `/households/` | Create household |
| GET | `/households/` | List households |
| GET | `/households/{id}` | Get household |
| GET | `/households/{id}/readings` | All readings for a household |
| GET | `/households/{id}/alerts` | All alerts for a household |
| GET | `/households/{id}/bill-estimate` | Bill estimate |

### Meters

| Method | Route | Description |
|---|---|---|
| POST | `/meters/` | Register a smart meter |
| GET | `/meters/` | List all meters |
| GET | `/meters/{id}` | Get a meter |

### Readings

| Method | Route | Description |
|---|---|---|
| POST | `/readings/` | Post a meter reading |
| GET | `/readings/meter/{meter_id}` | Readings for a meter |
| GET | `/readings/household/{household_id}` | Readings for a household |

### Alerts

| Method | Route | Description |
|---|---|---|
| GET | `/alerts/` | List all alerts |
| GET | `/alerts/household/{household_id}` | Alerts for a household |
| POST | `/alerts/` | Create an alert manually |
| PUT | `/alerts/{id}/resolve` | Resolve alert |

### Reports

| Method | Route | Description |
|---|---|---|
| GET | `/reports/monthly/{id}` | Monthly usage report |
| GET | `/reports/bill-estimate/{id}` | Bill estimate |

## Simulator

Generates synthetic meter readings and posts them to the backend.

```powershell
python simulator\meter_simulator.py --url http://127.0.0.1:8000/readings --meters 2 --interval 10 --duration 60
```

Options:

| Flag | Description |
|---|---|
| `--meters` | Number of meters to simulate |
| `--meter-ids` | Target specific meter IDs |
| `--interval` | Seconds between reading cycles |
| `--duration` | Total run time in seconds |
| `--profile` | Usage pattern: `low`, `balanced`, `high`, `mixed` |
| `--seed` | Make runs reproducible |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./dev.db` | Database connection string |

Set in a `.env` file at the project root (not committed).

## Testing

```powershell
pytest -q
```

## Roadmap

- Authentication and user accounts
- Email and SMS alert notifications
- Docker Compose deployment
- PostgreSQL production setup
- Real-time readings via WebSocket

## License

No license has been added yet. Add one before publishing or sharing externally.
