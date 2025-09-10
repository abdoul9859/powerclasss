# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project: GEEK TECHNOLOGIE – Gestion de Stock (FastAPI + SQLAlchemy + Jinja + static JS)

What this covers
- Day-to-day commands (setup, run, Docker). No linter/test tooling is configured in-repo.
- High-level architecture so you can navigate and modify features quickly.

Commands (Windows PowerShell and Docker)

Setup (local)
- Create venv and install dependencies
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

Run (local, FastAPI via uvicorn)
- Default run
  ```powershell
  python start.py
  ```
- Enable autoreload (development)
  ```powershell
  $env:RELOAD = "true"; python start.py
  ```
- Alternative direct uvicorn
  ```powershell
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  ```

Database initialization and seed
- On startup, main.py can initialize tables and optionally seed defaults controlled by env flags.
- For a first run against an empty DB (development):
  ```powershell
  $env:INIT_DB_ON_STARTUP = "true"; $env:SEED_DEFAULT_DATA = "true"; python start.py
  ```
- Large synthetic dataset (optional):
  ```powershell
  $env:SEED_LARGE_TEST_DATA = "true"; python start.py
  ```

Run with Docker (app + PostgreSQL)
- Build and start
  ```powershell
  docker compose up -d --build
  ```
- Tail app logs
  ```powershell
  docker compose logs -f app
  ```
- Stop and remove
  ```powershell
  docker compose down
  ```
Notes
- The compose file exposes http://localhost:8000 and a Postgres 15 container.
- The app reads DATABASE_URL and DB_SSLMODE; see Environment below.

Testing and linting
- No test suite or linter configuration is present in this repository (no pytest/ruff/flake8 configs). Add tooling before assuming commands exist.

High-level architecture

Entrypoints and runtime
- start.py: CLI entry that runs uvicorn (honors HOST, PORT, RELOAD envs).
- main.py: FastAPI app factory and wiring:
  - Registers routers for all domains (auth, products, clients, stock_movements, invoices, quotations, suppliers, supplier_invoices, debts, delivery_notes, bank_transactions, reports, user_settings, migrations, cache, dashboard, daily_recap, daily_purchases).
  - Mounts /static and configures Jinja2Templates (templates/). Injects ASSET_VERSION for cache busting.
  - Adds a lightweight HTTP middleware for cache headers (static assets long-cache; HTML no-store).
  - Startup/shutdown hooks:
    - Optional DB initialization/seed via INIT_DB_ON_STARTUP and SEED_DEFAULT_DATA.
    - Optional background migration worker via ENABLE_MIGRATIONS_WORKER.
- api/index.py: Serverless entry (e.g., Vercel) that exports the FastAPI app symbol.

Web UI and assets
- Jinja templates in templates/ render the HTML UI (e.g., desktop.html) and pull versioned assets with ASSET_VERSION.
- Static frontend logic is in static/js/*.js (feature-aligned files like products.js, invoices.js, etc.).

API surface (by domain)
- Routers under app/routers/ encapsulate domain endpoints and depend on get_current_user for access control.
  Examples: auth.py, products.py, clients.py, stock_movements.py, invoices.py, quotations.py, supplier_invoices.py, debts.py, delivery_notes.py, bank_transactions.py, reports.py, user_settings.py, dashboard.py, daily_recap.py, daily_purchases.py.
- Most routes are JSON APIs under /api/...; main.py also serves HTML routes for the UI (/, /login, /products, …).

Data layer
- app/database.py defines:
  - Engine creation from DATABASE_URL with driver normalization (postgresql+psycopg) and SSL mode heuristics.
  - SessionLocal and Base.
  - ORM models for users, products/variants/attributes, stock movements, clients, quotations, invoices (and payments), bank transactions, suppliers, supplier invoices (and payments), daily purchases and categories, and more.
  - A create_tables() helper (invoked by init_db) to create all tables when desired.
- app/init_db.py seeds:
  - Default admin/user accounts and baseline categories/clients when SEED_DEFAULT_DATA=true.
  - Optional large synthetic dataset when SEED_LARGE_TEST_DATA=true (sizes controllable via SEED_* envs).

Authentication and authorization
- app/auth.py provides JWT issuance/verification and user resolution via cookies or Authorization header.
  - Cookie name and attributes configurable (AUTH_COOKIE_NAME, AUTH_COOKIE_SECURE, AUTH_COOKIE_SAMESITE, AUTH_COOKIE_PATH).
  - Role helpers (require_role, require_any_role) and get_current_active_user.
  - Claims-based mode (AUTH_TRUST_JWT_CLAIMS=true) can bypass DB lookups by trusting JWT claims.
- app/routers/auth.py exposes login/verify/logout and basic user CRUD (admin-gated).

Background processing
- app/services/migration_processor.py runs a background worker (opt-in) to process Migration tasks persisted in DB, importing CSV/JSON (Excel stubbed), and writing MigrationLog entries. Controlled by ENABLE_MIGRATIONS_WORKER.

Caching and performance
- Simple in-process caching for dashboard stats (app/routers/dashboard.py) with a short TTL to ease testing.
- HTTP cache headers middleware in main.py: long cache for /static/, no-store for HTML.
- ASSET_VERSION (commit SHA or timestamp) enables static asset cache busting in templates.

Deployment notes
- Dockerfile uses Python 3.12 slim, installs requirements, exposes PORT (default 8000), and runs python -u start.py. Healthcheck hits /api.
- docker-compose.yml wires Postgres and the app; app container runs start.py and mounts the repo as a volume for iterative dev.
- api/index.py allows serverless hosting that speaks ASGI.

Environment
Set via .env or the process environment. Key variables read across the codebase:
- Server
  - HOST (default 0.0.0.0), PORT (default 8000), RELOAD (true|false)
  - ASSET_VERSION (fallbacks to commit SHA or timestamp)
- Database
  - DATABASE_URL (normalized to postgresql+psycopg, sslmode appended when not specified)
  - DB_SSLMODE (e.g., disable, require)
  - DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, DB_POOL_RECYCLE
  - INIT_DB_ON_STARTUP (true|false), SEED_DEFAULT_DATA (true|false)
  - SEED_LARGE_TEST_DATA plus SEED_CLIENTS, SEED_PRODUCTS, SEED_VARIANTS_MIN/SEED_VARIANTS_MAX, SEED_INVOICES, SEED_QUOTATIONS, SEED_BANK_TX
- Auth
  - SECRET_KEY, ALGORITHM (HS256), ACCESS_TOKEN_EXPIRE_MINUTES
  - AUTH_TRUST_JWT_CLAIMS (true|false)
  - AUTH_COOKIE_NAME (default gt_access), AUTH_COOKIE_SECURE, AUTH_COOKIE_SAMESITE, AUTH_COOKIE_PATH
- Migrations
  - ENABLE_MIGRATIONS_WORKER (true|false)

Tips for navigation (big picture)
- To add or modify an API feature: start in app/routers/<feature>.py, adjust schemas in app/schemas.py, and model fields in app/database.py as needed.
- To extend UI: map a new HTML route in main.py to a template in templates/, and add the corresponding static/js/<feature>.js.
- When introducing new models: update database models, include them in init_db seeding if needed, and wire to routers.

Read this first (from README.md)
- Local run: python start.py (use RELOAD=true for dev).
- Docker dev: docker compose up -d --build; logs via docker compose logs -f app; stop with docker compose down.
- The API is reachable at /api (see README for the detailed endpoint list). Default dev accounts are created when seeding is enabled.

