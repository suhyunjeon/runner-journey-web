# Runner Journey API

Python `FastAPI` backend for a mobile-first runner planning service.

## What is included

- Race data API
- Runner profile API
- Personalized recommendation API
- SQLAlchemy-based persistence layer
- Automatic seed data bootstrap
- Collector interface for future crawling integrations

## Quick start

1. Create a virtual environment
2. Install dependencies
3. Run the API server

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` for the mobile-first home screen.
API docs remain available at `http://127.0.0.1:8000/docs`.

## Deploy on Render

This project includes a Render blueprint at [render.yaml](/Users/suhyunjeon/Documents/Codex/2026-05-05-https-marathongo-co-kr-python/render.yaml).

### Recommended setup

- `Web Service`: FastAPI app
- `Postgres`: Render-managed Postgres

### Important note for free Render

- Render free web services spin down after idle time.
- Render free web services do **not** keep local SQLite files.
- Render free Postgres is suitable for testing, but it expires after 30 days unless upgraded.

### Deploy steps

1. Push this project to GitHub.
2. In Render, choose `New +` -> `Blueprint`.
3. Connect the GitHub repository.
4. Render will detect `render.yaml` and create:
   - `runner-journey-web`
   - `runner-journey-db`
5. Wait for the first deploy to finish.
6. Open the generated web URL.

### Manual service settings

If you prefer to create the service manually instead of using the blueprint:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variable: `DATABASE_URL=<Render Postgres connection string>`

## Database

By default the app uses SQLite at `./marathon.db`.

To switch to PostgreSQL, set `DATABASE_URL`.

```bash
export DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/marathon
```

## API examples

- `GET /api/v1/races`
- `GET /api/v1/profiles/me`
- `PUT /api/v1/profiles/me`
- `GET /api/v1/recommendations/me`
- `GET /api/v1/recommendations/me/home`
- `GET /health`

## Sync from MarathonGo

This project now includes a real collector for `marathongo.co.kr`.

```bash
source .venv/bin/activate
python -m app.sync --source marathongo
```

The sync job:

- loads MarathonGo listing pages including `접수중` and `오픈예정`
- follows pagination to gather many more race detail URLs
- parses each detail page's `__NEXT_DATA__`
- follows official/apply links when available
- enriches fee/cutoff/gift/course metadata from official pages
- upserts races into your database

If you want to test with a smaller batch first:

```bash
python -m app.sync --source marathongo --limit 20
```

## Product direction

This project is intentionally not a plain race listing clone.

- `races` are raw ingredients
- `runner profile` captures the user's goal and constraints
- `recommendations` becomes the mobile home experience

## Suggested next steps

- Add PostgreSQL driver and migrations
- Add an admin screen for manual review
- Build scheduled collectors for official race sites
- Add auth for organizer submissions
