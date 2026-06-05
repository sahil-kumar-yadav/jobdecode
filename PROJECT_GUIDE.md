# jobdecode — Project Guide (Working & Usage)

Mini data engineering portfolio project: **ETL pipeline (Pandas) + SQLite storage + FastAPI API + Next.js UI**.

---

## What this project does

On demand, the backend will:
1. **Extract** mock job postings (`200` rows)
2. **Transform** them (normalize titles/locations, parse salary into numeric LPA range, extract skills)
3. **Load** results into a local **SQLite** database (`jobdecode.sqlite3`)
4. **Compute analytics** and cache them for the UI

The UI can:
- Browse jobs (`/jobs`) with filtering + pagination
- Trigger ETL and view aggregated stats (`/stats`)

---

## Prerequisites

- Python 3.10+ (recommended)
- Node.js 18+ (for the Next.js UI)

---

## 1) Run the backend (FastAPI)

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Start the API server

Run exactly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Open backend endpoints
- API status: http://127.0.0.1:8000/
- Swagger UI (useful for testing): http://127.0.0.1:8000/docs

### Trigger ETL

```bash
curl -X POST http://127.0.0.1:8000/run-etl
```

### Verify data exists
After ETL completes:

```bash
curl "http://127.0.0.1:8000/jobs?page=1&page_size=5"
```

```bash
curl "http://127.0.0.1:8000/stats"
```

---

## 2) What files/tables are produced

### Output files
- **SQLite DB (repo root):** `jobdecode.sqlite3`
- **Raw JSON snapshot:** `data/raw.json` (written during each ETL run)

### SQLite tables
Created (or ensured) by the loader:
- `jobs`
  - columns: `job_id`, `title`, `company`, `location`, `salary`, `skills_json`, `posted_date`, `experience_level`, `description`, `min_lpa`, `max_lpa`, `avg_lpa`
- `job_skills`
  - columns: `job_id`, `skill` (with an index on `skill`)

### ETL behavior (important)
- Every `POST /run-etl`:
  - regenerates mock jobs
  - transforms them
  - **replaces** job data by deleting from `jobs` and inserting fresh rows
  - refreshes cached stats used by `GET /stats`

---

## 3) API Reference

### `GET /`
Returns basic status and available endpoints.

### `POST /run-etl`
Triggers the full ETL.

**Response** (example):
```json
{"status":"ok","jobs_loaded":200,"stats_version":1}
```

### `GET /jobs`
Returns paginated jobs stored in SQLite.

**Query parameters**:
- `location` (optional, string)
  - matches normalized location text (e.g. `Bengaluru`, `Remote - India`)
- `skill` (optional, string)
  - filters via `job_skills`
- `page` (default `1`)
- `page_size` (default `50`, capped at `100`)
- `sort` (default `posted_date`)
  - allowed: `posted_date`, `min_lpa`, `max_lpa`, `avg_lpa`
- `order` (default `desc`)
  - `asc` or `desc`

**Example**:
```bash
curl "http://127.0.0.1:8000/jobs?skill=Python&page=1&page_size=20"
```

**Response shape**:
```json
{
  "page": 1,
  "page_size": 20,
  "total": 200,
  "items": [
    {
      "job_id": "JOB-1",
      "title": "Data Analyst",
      "company": "Acme Analytics",
      "location": "Bengaluru",
      "salary": "INR 12L - 20L",
      "skills": ["Python","SQL"],
      "posted_date": "2026-01-15",
      "experience_level": "Mid",
      "description": "...",
      "min_lpa": 12,
      "max_lpa": 20,
      "avg_lpa": 16
    }
  ]
}
```

### `GET /stats`
Returns analytics computed from the loaded SQLite data.

Behavior:
- If ETL already ran, returns the cached payload.
- If no cached payload exists yet, computes stats from the DB.

**Response shape**:
```json
{
  "top_skills": [{"skill":"Python","count":150}],
  "top_companies": [{"company":"Acme Analytics","count":30}],
  "average_salary": 12.7,
  "count": 200
}
```

---

## 4) Run the Next.js UI locally

### Install Node dependencies

From the project root:

```bash
cd web && npm ci
```

### Run the dev server

```bash
npm run dev
```

Then open the UI routes:
- Jobs page: `http://localhost:3000/jobs`
- Stats page: `http://localhost:3000/stats`

### Configure the backend URL (required)
The UI calls the backend using:
- `NEXT_PUBLIC_API_BASE` environment variable, defaulting to a public GitHub dev URL.

For local development, set:

```bash
# example (bash)
export NEXT_PUBLIC_API_BASE="http://localhost:8000"
```

Then start the UI server (or restart it) so the variable is picked up.

---

## 5) Common workflow

1. Start backend:
   - `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Trigger ETL once (via Swagger or curl):
   - `POST /run-etl`
3. Start UI:
   - `cd web && npm run dev`
4. Use:
   - `/jobs` for filtering + pagination
   - `/stats` to view aggregates (and optionally re-run ETL from the UI)

---

## Troubleshooting

### UI shows “No data yet”
- You likely didn’t run ETL yet.
- Run `POST /run-etl` and refresh `/stats`.

### UI can’t fetch data
- Ensure `NEXT_PUBLIC_API_BASE` points to your backend.
- Ensure backend is reachable from the browser (CORS is permissive in the backend, but the host/port must be correct).

---

## Where to look in the code

- `main.py`: FastAPI routes
- `app/etl.py`: ETL orchestration
- `app/extractors/mock_generator.py`: mock job generation
- `app/transform/cleaning.py`: transformation logic
- `app/db.py`: SQLite load/query + pagination
- `app/analytics.py`: stats computation
- `web/app/jobs/page.tsx`: jobs UI
- `web/app/stats/page.tsx`: stats UI

