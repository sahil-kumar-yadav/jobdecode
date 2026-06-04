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
        conn.commit()


def replace_jobs(df: pd.DataFrame):
    init_db()

    rows = []
    for _, r in df.iterrows():
        rows.append(
            (
                r["job_id"],
                r["title"],
                r["company"],
                r["location"],
                r["salary"],
                json.dumps(r["skills"] or []),
                str(r["posted_date"]) if pd.notna(r["posted_date"]) else None,
                r["experience_level"],
                r["description"],
                r["min_lpa"],
                r["max_lpa"],
                r["avg_lpa"],
            )
        )


    with get_conn() as conn:
        conn.execute("DELETE FROM jobs")
        conn.executemany(
            """
            INSERT INTO jobs (
                job_id, title, company, location, salary, skills_json, posted_date,
                experience_level, description, min_lpa, max_lpa, avg_lpa
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
            """,
            rows,
        )
        conn.commit()


def list_jobs(location: str | None, skill: str | None, page: int, page_size: int) -> dict[str, Any]:
    init_db()
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    offset = (page - 1) * page_size

    where_clauses = []
    params: list[Any] = []

    if location:
        where_clauses.append("LOWER(location) = LOWER(?)")
        params.append(location.strip())

    if skill:
        # naive filter: match substring in skills_json
        where_clauses.append("skills_json LIKE ?")
        params.append(f"%\"{skill.strip()}\"%")

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    with get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM jobs {where_sql}", params).fetchone()[0]

        jobs = conn.execute(
            f"""
            SELECT job_id, title, company, location, salary, skills_json, posted_date,
                   experience_level, description, min_lpa, max_lpa, avg_lpa
            FROM jobs
            {where_sql}
            ORDER BY posted_date DESC
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


