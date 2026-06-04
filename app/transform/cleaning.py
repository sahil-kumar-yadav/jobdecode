from __future__ import annotations

import re
from typing import Any

import pandas as pd


TITLE_NORMALIZATION_RULES: list[tuple[str, str]] = [
    (r"software engineer", "Software Engineer"),
    (r"backend developer", "Backend Developer"),
    (r"data engineer", "Data Engineer"),
    (r"machine learning engineer", "Machine Learning Engineer"),
    (r"data analyst", "Data Analyst"),
    (r"product analyst", "Product Analyst"),
    (r"devops engineer", "DevOps Engineer"),
    (r"qa engineer", "QA Engineer"),
]


def normalize_title(title: str | None) -> str | None:
    if title is None:
        return None
    t = title.strip()
    if not t:
        return None
    t_lower = t.lower()
    for pattern, out in TITLE_NORMALIZATION_RULES:
        if re.search(pattern, t_lower):
            return out
    # Fallback: title case
    return t.title()


def normalize_location(location: str | None) -> str | None:
    if location is None:
        return None
    loc = location.strip()
    if not loc:
        return None
    loc = re.sub(r"\s+", " ", loc)
    # Normalize common patterns
    if loc.lower().startswith("remote"):
        return "Remote - India"
    # Capitalize each word
    return " ".join([w.capitalize() for w in loc.split(" ")])


def _extract_skills_from_description(description: str | None, known_skills: set[str]) -> set[str]:
    if not description:
        return set()
    desc_lower = description.lower()
    found: set[str] = set()

    for skill in known_skills:
        if skill.lower() in desc_lower:
            found.add(skill)

    return found


def parse_salary_to_numeric_range(salary: str | None) -> dict[str, Any]:
    """Return min_lpa, max_lpa, avg_lpa as floats.

    Supports patterns like:
      - "INR 12L - 20L"
      - "INR 12-20 LPA"
      - "12L - 20L INR"
    """
    if not salary:
        return {"min_lpa": None, "max_lpa": None, "avg_lpa": None}

    s = salary.strip()

    # Extract L (lakh) or plain numbers.
    # Examples: 12L - 20L, 12-20 LPA
    m = re.search(r"(?P<a>\d+(?:\.\d+)?)\s*(?:L|l)\s*(?:-|to)\s*(?P<b>\d+(?:\.\d+)?)\s*(?:L|l)", s)
    if m:
        a = float(m.group("a"))
        b = float(m.group("b"))
        lo, hi = sorted([a, b])
        return {"min_lpa": lo, "max_lpa": hi, "avg_lpa": (lo + hi) / 2}

    m2 = re.search(r"(?P<a>\d+(?:\.\d+)?)\s*-\s*(?P<b>\d+(?:\.\d+)?)\s*(?:LPA|lpa)", s)
    if m2:
        a = float(m2.group("a"))
        b = float(m2.group("b"))
        lo, hi = sorted([a, b])
        return {"min_lpa": lo, "max_lpa": hi, "avg_lpa": (lo + hi) / 2}

    # Single value like "INR 12L"
    m3 = re.search(r"(?P<a>\d+(?:\.\d+)?)\s*(?:L|l)\b", s)
    if m3:
        a = float(m3.group("a"))
        return {"min_lpa": a, "max_lpa": a, "avg_lpa": a}

    return {"min_lpa": None, "max_lpa": None, "avg_lpa": None}


def extract_skills(df: pd.DataFrame) -> pd.DataFrame:
    # known skills come from the provided skills column + common ones
    known = set()
    if "skills" in df.columns:
        for x in df["skills"].dropna().tolist():
            if isinstance(x, list):
                known.update(x)
    known.update({"Python", "SQL", "Pandas", "FastAPI", "Docker", "Kubernetes", "Airflow", "Spark"})
    # Extract additional from description
    out_skills = []
    for _, row in df.iterrows():
        base = set(row.get("skills") or [])
        desc_extra = _extract_skills_from_description(row.get("description"), known)
        merged = list(dict.fromkeys(list(base) + list(desc_extra)))
        out_skills.append(merged)
    df = df.copy()
    df["skills"] = out_skills
    return df


def transform_jobs(raw_jobs: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(raw_jobs)

    # Fill missing expected columns
    expected_cols = [
        "job_id",
        "title",
        "company",
        "location",
        "salary",
        "skills",
        "posted_date",
        "experience_level",
        "description",
    ]
    for c in expected_cols:
        if c not in df.columns:
            df[c] = None

    # Clean basic types
    df["job_id"] = df["job_id"].astype(str)
    df["title"] = df["title"].map(normalize_title)
    df["company"] = df["company"].astype(str).str.strip()
    df["location"] = df["location"].map(normalize_location)
    df["experience_level"] = df["experience_level"].astype(str).str.strip()

    # Skills
    df["skills"] = df["skills"].apply(lambda x: x if isinstance(x, list) else ([] if pd.isna(x) else list(x)))
    df = extract_skills(df)

    # Posted date
    df["posted_date"] = pd.to_datetime(df["posted_date"], errors="coerce").dt.date

    # Salary -> numeric
    salary_parsed = df["salary"].apply(parse_salary_to_numeric_range)
    df["min_lpa"] = salary_parsed.apply(lambda d: d["min_lpa"])
    df["max_lpa"] = salary_parsed.apply(lambda d: d["max_lpa"])
    df["avg_lpa"] = salary_parsed.apply(lambda d: d["avg_lpa"])

    # Drop rows missing job_id or title/company
    df = df.dropna(subset=["job_id", "title", "company"])

    # Final column order
    final_cols = [
        "job_id",
        "title",
        "company",
        "location",
        "salary",
        "skills",
        "posted_date",
        "experience_level",
        "description",
        "min_lpa",
        "max_lpa",
        "avg_lpa",
    ]
    for c in final_cols:
        if c not in df.columns:
            df[c] = None

    return df[final_cols]


