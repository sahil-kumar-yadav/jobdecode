# jobdecode - Job Market Analytics ETL (FastAPI + Pandas + SQLite)

Mini data engineering portfolio project.

## Features
- Mock job posting generator (in-memory -> `data/raw.json`)
- Pandas transformations: cleaning, skill extraction, salary parsing, location normalization
- SQLite load into `jobs` table
- FastAPI API:
  - `GET /` status
  - `POST /run-etl` trigger full ETL
  - `GET /jobs` list with pagination + filters
  - `GET /stats` analytics (top skills/companies, avg salary)

## Run in GitHub Codespaces
### 1) Install dependencies
```bash
pip install -r requirements.txt
```

### 2) Start the server
Run exactly this command:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open:
- Swagger UI: http://127.0.0.1:8000/docs
- Home: http://127.0.0.1:8000/
- Jobs: http://127.0.0.1:8000/jobs
- Stats: http://127.0.0.1:8000/stats

### 3) Trigger ETL
In Swagger UI or via curl:
```bash
curl -X POST http://127.0.0.1:8000/run-etl
```

After triggering, `/jobs` and `/stats` will return data.

## Example API responses
### `POST /run-etl`
```json
{"status":"ok","jobs_loaded":200}
```

### `GET /stats`
```json
{
  "top_skills": [{"skill": "Python", "count": 150}, {"skill": "SQL", "count": 140}],
  "top_companies": [{"company": "Acme Analytics", "count": 30}],
  "average_salary": 12.7,
  "count": 200
}
```

## Project structure
- `main.py` - FastAPI app
- `app/etl.py` - run full pipeline (extract -> transform -> load)
- `app/extractors/mock_generator.py` - mock dataset generator
- `app/transform/cleaning.py` - Pandas transforms
- `app/db.py` - SQLite storage + queries
- `app/analytics.py` - compute analytics

## Outputs / Files
- Database: `jobdecode.sqlite3` (created in repo root)
- Raw dataset: `data/raw.json` (created on ETL run)

