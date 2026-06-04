import logging

from fastapi import FastAPI

from app.etl import run_etl_and_load

app = FastAPI(title="Job Market Analytics ETL", version="0.1.0")

logger = logging.getLogger("jobdecode")


@app.get("/")
def home():
    return {
        "status": "ok",
        "service": "jobdecode",
        "endpoints": ["/run-etl", "/jobs", "/stats"],
    }


@app.post("/run-etl")
def run_etl():
    result = run_etl_and_load()
    return {"status": "ok", **result}


@app.get("/jobs")
def get_jobs(location: str | None = None, skill: str | None = None, page: int = 1, page_size: int = 50):
    # Deferred import so app start is quick.
    from app.db import list_jobs

    return list_jobs(location=location, skill=skill, page=page, page_size=page_size)


@app.get("/stats")
def stats():
    from app.analytics import compute_stats

    return compute_stats()


