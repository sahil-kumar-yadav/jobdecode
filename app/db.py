from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from typing import Any

import pandas as pd

DB_PATH = "jobdecode.sqlite3"




@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                location TEXT,
                salary TEXT,
                skills_json TEXT,
                posted_date TEXT,
                experience_level TEXT,
                description TEXT,
                min_lpa REAL,
                max_lpa REAL,
                avg_lpa REAL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS job_skills (
                job_id TEXT NOT NULL,
                skill TEXT NOT NULL,
                PRIMARY KEY(job_id, skill),
                FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills(skill);
            """
        )
        conn.commit()


def replace_jobs(df: pd.DataFrame):
    init_db()

    # Build jobs rows + job_skills rows efficiently
    job_rows: list[tuple[Any, ...]] = []
    skill_rows: list[tuple[Any, ...]] = []

    # Ensure stable iteration + less pandas overhead
    for r in df.itertuples(index=False):
        # Columns order matches transform_jobs final_cols
        (
            job_id,
            title,
            company,
            location,
            salary,
            skills,
            posted_date,
            experience_level,
            description,
            min_lpa,
            max_lpa,
            avg_lpa,
        ) = r

        job_rows.append(
            (
                job_id,
                title,
                company,
                location,
                salary,
                json.dumps(skills or []),
                str(posted_date) if pd.notna(posted_date) else None,
                experience_level,
                description,
                min_lpa,
                max_lpa,
                avg_lpa,
            )
        )

        if skills:
            for s in skills:
                skill_rows.append((job_id, s))

    with get_conn() as conn:
        conn.execute("DELETE FROM jobs")

        conn.executemany(
            """
            INSERT INTO jobs (
                job_id, title, company, location, salary, skills_json, posted_date,
                experience_level, description, min_lpa, max_lpa, avg_lpa
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
            """,
            job_rows,
        )

        if skill_rows:
            conn.executemany(
                """
                INSERT OR IGNORE INTO job_skills (job_id, skill)
                VALUES (?, ?)
                """,
                skill_rows,
            )

        conn.commit()


def list_jobs(
    location: str | None,
    skill: str | None,
    page: int,
    page_size: int,
    sort: str = "posted_date",
    order: str = "desc",
) -> dict[str, Any]:
    init_db()
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    offset = (page - 1) * page_size

    sort_map = {
        "posted_date": "posted_date",
        "min_lpa": "min_lpa",
        "max_lpa": "max_lpa",
        "avg_lpa": "avg_lpa",
    }
    sort_col = sort_map.get(sort, "posted_date")
    order_sql = "DESC" if (order or "").lower() != "asc" else "ASC"

    where_clauses: list[str] = []
    params: list[Any] = []

    join_sql = ""
    if skill:
        join_sql = "JOIN job_skills js ON js.job_id = jobs.job_id"
        where_clauses.append("js.skill = ?")
        params.append(skill.strip())

    if location:
        where_clauses.append("LOWER(location) = LOWER(?)")
        params.append(location.strip())

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    with get_conn() as conn:
        total = conn.execute(
            f"SELECT COUNT(DISTINCT jobs.job_id) FROM jobs {join_sql} {where_sql}",
            params,
        ).fetchone()[0]

        jobs = conn.execute(
            f"""
            SELECT DISTINCT jobs.job_id, title, company, location, salary, skills_json, posted_date,
                            experience_level, description, min_lpa, max_lpa, avg_lpa
            FROM jobs
            {join_sql}
            {where_sql}
            ORDER BY {sort_col} {order_sql}
            LIMIT ? OFFSET ?
            """,
            [*params, page_size, offset],
        ).fetchall()

    items = []
    for row in jobs:
        (
            job_id,
            title,
            company,
            loc,
            salary,
            skills_json,
            posted_date,
            experience_level,
            description,
            min_lpa,
            max_lpa,
            avg_lpa,
        ) = row
        items.append(
            {
                "job_id": job_id,

                "title": title,
                "company": company,
                "location": loc,
                "salary": salary,
                "skills": json.loads(skills_json) if skills_json else [],
                "posted_date": posted_date,
                "experience_level": experience_level,
                "description": description,
                "min_lpa": min_lpa,
                "max_lpa": max_lpa,
                "avg_lpa": avg_lpa,
            }
        )

    return {"page": page, "page_size": page_size, "total": total, "items": items}



