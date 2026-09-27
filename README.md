# Pik Nirnay / पीक निर्णय

Marathi-first pre-sowing climate and financial risk decision-support prototype for rain-fed Kharif farmers in Dharashiv district, Maharashtra.

**This is an educational/research prototype.** It is not field-validated and does not replace an agronomist, Krishi Vigyan Kendra (KVK), or official government advisory. See [docs/product/PRD.md](docs/product/PRD.md) for the full product requirements.

## Current status

This repository currently contains only the **V1 project foundation**: a FastAPI backend skeleton, a React/Vite frontend skeleton, localization scaffolding, and local Postgres configuration. No crop recommendation, risk-scoring, or agronomic decision logic exists yet — see [docs/planning/v1-execution-graph.md](docs/planning/v1-execution-graph.md) for what comes next.

## Architecture

The system is a modular monolith (not microservices). See [docs/product/PRD.md](docs/product/PRD.md#11-technical-architecture--v1-direction) for the target module diagram.

```text
backend/app/
├── main.py            # FastAPI app factory
├── config.py          # Environment-driven settings
├── db/                # SQLAlchemy engine/session (no models yet)
├── i18n/              # Marathi + English locale catalogues and loader
├── api/v1/            # HTTP routes (health, i18n)
└── modules/           # Domain module boundaries (empty until their own tasks land)
    ├── field_profile/
    ├── agronomy_rules/
    ├── decision_engine/
    ├── provenance/
    └── data_adapters/{weather,climate,market}/
```

```text
frontend/src/
├── main.tsx           # App entry point
├── App.tsx            # Language toggle + prototype shell
└── i18n/              # Marathi + English locale catalogues, language context
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for local Postgres), or a local PostgreSQL 16 instance

## Local development

### 1. Database

```bash
docker compose up -d postgres
```

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp ../.env.example .env   # adjust DATABASE_URL etc. if needed

uvicorn app.main:app --reload
```

The API is served at `http://localhost:8000`. Key endpoints:

- `GET /api/v1/health/live` — liveness, no dependencies.
- `GET /api/v1/health/ready` — reports `degraded` (not a crash) if Postgres is unreachable.
- `GET /api/v1/i18n/{mr|en}` — full locale catalogue.
- `GET /docs` — interactive OpenAPI docs.

Run the backend tests:

```bash
cd backend
source .venv/bin/activate
pytest
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app is served at `http://localhost:5173`, defaulting to Marathi with an English toggle.

Run the frontend tests:

```bash
cd frontend
npm test
```

Type-check and production build:

```bash
cd frontend
npm run build
```

## Localization

User-facing text must never be hard-coded; it must go through a localization key (see [CLAUDE.md](CLAUDE.md#12-marathi-first-requirement)). Catalogues currently live independently in:

- `backend/app/i18n/locales/{mr,en}.json`
- `frontend/src/i18n/locales/{mr,en}.json`

These will be reconciled into a single source once the i18n module's ownership is finalized (see `docs/planning/v1-execution-graph.md`, Phase F1).

## Scope

See [CLAUDE.md](CLAUDE.md) for the full set of project instructions, non-goals and working method. Agricultural/financial decision rules are controlled requirements — they are never invented from general knowledge and must trace to an approved source (PoCRA, ICAR-CRIDA, or an explicitly accepted product assumption).
