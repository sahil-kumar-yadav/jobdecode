import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.etl import run_etl_and_load


app = FastAPI(title="Job Market Analytics ETL", version="0.1.0")

# Allow browser-based UIs (Next.js) to call this API during development.
# Keep permissive for local usage; tighten in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
def get_jobs(
    location: str | None = None,
    skill: str | None = None,
    page: int = 1,
    page_size: int = 50,
    sort: str = "posted_date",
    order: str = "desc",
):
    # Deferred import so app start is quick.
    from app.db import list_jobs

    return list_jobs(
        location=location,
        skill=skill,
        page=page,
        page_size=page_size,
        sort=sort,
        order=order,
    )


@app.get("/stats")
def stats():
    # Fast path: serve cached stats computed during the last /run-etl
    from app.app_state import cache, lock

    with lock:
        if cache.payload is not None:
            return cache.payload

    from app.analytics import compute_stats

    payload = compute_stats()
    with lock:
        cache.payload = payload
        cache.version += 1
    return payload



