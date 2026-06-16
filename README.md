# Smart Energy Consumption Monitoring System

A FastAPI-based platform for monitoring household electricity usage, with smart meter simulation, automated alerts, analytics, and a built-in web dashboard.

## Features

- Household and smart meter registration (one meter per household enforced)
- User self-registration and login via `/auth/register` and `/auth/login`
- Meter reading ingestion via REST API
- Automatic alert generation for high usage and consumption spikes
- Monthly usage summaries and bill estimation
- Admin Panel (`/`) — full CRUD for households, meters, and alerts
- User Portal (`/user`) — self-service login, live dashboard, readings, and alerts
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
| Auth | PBKDF2-HMAC-SHA256 (stdlib, no extra deps) |
| Simulation | Python + requests |
| Testing | Pytest |

## Project Structure

```
app/
├── routers/        # REST endpoints (households, meters, readings, alerts, reports, auth)
├── services/       # Alert detection and analytics logic
├── views/          # Serves the HTML pages
├── models.py       # SQLAlchemy models
├── schemas.py      # Pydantic schemas
├── database.py     # DB session and engine
└── main.py         # App entry point
templates/
├── index.html      # Admin Panel (Bootstrap dashboard)
└── user.html       # User Portal (login / self-service dashboard)
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
python run.py
```

Or directly with uvicorn:

```powershell
uvicorn app.main:app --reload --port 8000
```

### 5. Open the app

| Page | URL |
|---|---|
| Admin Panel | `http://127.0.0.1:8000` |
| User Portal | `http://127.0.0.1:8000/user` |
| Swagger UI | `http://127.0.0.1:8000/docs` |

## Admin Panel (`/`)

Full management interface at the root URL:

- Stat cards — households, meters, open/resolved alert counts
- Households — list, add, edit, delete
- Smart Meters — list, register, delete
- Bill Estimate & Report — select a household to see kWh totals and estimated bill
- Alerts — filter by household, resolve with one click

Admin-created households receive a default password (`admin`). Users can claim their account via the User Portal.

## User Portal (`/user`)

Self-service page for household users:

- Register a new account or log in with email + password
- Dashboard showing meter readings, alert history, and bill estimate
- Alerts displayed as toast notifications for open HIGH/MEDIUM/LOW alerts

## API Overview

### Health

| Method | Route | Description |
|---|---|---|
| GET | `/api/status` | Health check |

### Auth

| Method | Route | Description |
|---|---|---|
| POST | `/auth/register` | Register a new household account |
| POST | `/auth/login` | Log in with email and password |

### Households

| Method | Route | Description |
|---|---|---|
| POST | `/households/` | Create household |
| GET | `/households/` | List households |
| GET | `/households/{id}` | Get household |
| PUT | `/households/{id}` | Update household |
| DELETE | `/households/{id}` | Delete household and its data |
| GET | `/households/{id}/readings` | All readings for a household |
| GET | `/households/{id}/alerts` | All alerts for a household |
| GET | `/households/{id}/bill-estimate` | Bill estimate |

### Meters

| Method | Route | Description |
|---|---|---|
| POST | `/meters/` | Register a smart meter |
| GET | `/meters/` | List all meters |
| GET | `/meters/{id}` | Get a meter |
| DELETE | `/meters/{id}` | Delete a meter and its readings |

> Each household may have at most one meter.

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

- Email and SMS alert notifications
- Docker Compose deployment
- PostgreSQL production setup guide
- Real-time readings via WebSocket

## License

No license has been added yet. Add one before publishing or sharing externally.
