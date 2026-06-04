from __future__ import annotations

import logging
from pathlib import Path

from app.extractors.mock_generator import generate_mock_jobs
from app.transform.cleaning import transform_jobs
from app.db import replace_jobs

logger = logging.getLogger("jobdecode")

RAW_JSON_PATH = Path("data/raw.json")


def run_etl_and_load() -> dict:
    from app.logging_config import configure_logging

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

    logger.info("ETL completed: loaded %s jobs", len(df))
    return {"jobs_loaded": int(len(df))}


