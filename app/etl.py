from __future__ import annotations

import logging
from pathlib import Path

from app.extractors.mock_generator import generate_mock_jobs
from app.transform.cleaning import transform_jobs
from app.db import replace_jobs
from app.app_state import cache as stats_cache, lock as stats_lock


logger = logging.getLogger("jobdecode")

RAW_JSON_PATH = Path("data/raw.json")


def run_etl_and_load() -> dict:
    from app.logging_config import configure_logging
    from app.analytics import compute_stats

    configure_logging()


    # Extract

    jobs = generate_mock_jobs(n=200)

    # Persist raw for realism
    RAW_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    import json

    RAW_JSON_PATH.write_text(json.dumps(jobs, ensure_ascii=False, indent=2))

    # Transform
    df = transform_jobs(jobs)

    # Load
    replace_jobs(df)

    # Refresh cached stats
    stats_payload = compute_stats()
    with stats_lock:
        stats_cache.payload = stats_payload
        stats_cache.version += 1

    logger.info("ETL completed: loaded %s jobs", len(df))
    return {"jobs_loaded": int(len(df)), "stats_version": stats_cache.version}


