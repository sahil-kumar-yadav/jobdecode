from __future__ import annotations

import json
import sqlite3
from collections import Counter

DB_PATH = "jobdecode.sqlite3"


def _get_all_jobs():
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """
            SELECT company, location, skills_json, min_lpa, max_lpa, avg_lpa
            FROM jobs
            """
        ).fetchall()
        return rows
    finally:
        conn.close()


def compute_stats() -> dict:
    rows = _get_all_jobs()
    if not rows:
        return {
            "top_skills": [],
            "top_companies": [],
            "average_salary": None,
            "count": 0,
        }

    skill_counter: Counter[str] = Counter()
    company_counter: Counter[str] = Counter()
    avg_salaries: list[float] = []

    for company, _location, skills_json, _min_lpa, _max_lpa, avg_lpa in rows:
        company_counter[company] += 1
        if avg_lpa is not None:
            avg_salaries.append(float(avg_lpa))
        if skills_json:
            try:
                skills = json.loads(skills_json)
            except Exception:
                skills = []
            for s in skills:
                skill_counter[s] += 1

    top_skills = [{"skill": s, "count": c} for s, c in skill_counter.most_common(10)]
    top_companies = [{"company": c, "count": n} for c, n in company_counter.most_common(10)]
    average_salary = sum(avg_salaries) / len(avg_salaries) if avg_salaries else None

    return {
        "top_skills": top_skills,
        "top_companies": top_companies,
        "average_salary": average_salary,
        "count": len(rows),
    }


