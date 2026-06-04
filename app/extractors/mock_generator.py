from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class MockJob:
    job_id: str
    title: str
    company: str
    location: str
    salary: str
    skills: list[str]
    posted_date: str
    experience_level: str
    description: str


TITLES = [
    "Software Engineer",
    "Data Analyst",
    "Data Engineer",
    "Backend Developer",
    "Machine Learning Engineer",
    "Product Analyst",
    "DevOps Engineer",
    "QA Engineer",
]

COMPANIES = [
    "Acme Analytics",
    "Globex",
    "Initech",
    "Umbrella Corp",
    "Soylent Systems",
    "Stark Industries",
    "Wayne Enterprises",
]

LOCATIONS = [
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Delhi",
    "Pune",
    "Chennai",
    "Remote - India",
]

EXPERIENCE = ["Entry", "Mid", "Senior", "Lead"]

SKILL_BANK = [
    "Python",
    "SQL",
    "Pandas",
    "FastAPI",
    "Docker",
    "Kubernetes",
    "Airflow",
    "Spark",
    "PyTorch",
    "scikit-learn",
    "Machine Learning",
    "Tableau",
    "Power BI",
    "AWS",
    "GCP",
    "ETL",
    "Data Modeling",
    "NLP",
    "Statistics",
]


def _random_date_str(days_back: int = 120) -> str:
    d = datetime.utcnow() - timedelta(days=random.randint(0, days_back))
    return d.strftime("%Y-%m-%d")


def _salary_str() -> str:
    # Keep it simple: ranges like "INR 12L - 20L" or single values.
    base = random.choice([6, 8, 10, 12, 14, 16, 18, 20, 25, 30])
    width = random.choice([3, 4, 5, 6, 8])
    low = base
    high = base + width
    fmt = random.choice(["INR {low}L - {high}L", "INR {low}-{high} LPA", "{low}L - {high}L INR"])
    return fmt.format(low=low, high=high)


def _skills_for_title(title: str) -> list[str]:
    title_lower = title.lower()
    picks: list[str] = []

    if "data engineer" in title_lower or "engineer" in title_lower:
        picks += ["Python", "SQL", "ETL", "Pandas", random.choice(["Spark", "Data Modeling"])]
    if "analyst" in title_lower or "product analyst" in title_lower:
        picks += ["SQL", "Statistics", random.choice(["Tableau", "Power BI"]), "Pandas"]
    if "machine learning" in title_lower:
        picks += ["Python", "SQL", "Machine Learning", random.choice(["PyTorch", "scikit-learn"]), "NLP"]
    if "devops" in title_lower:
        picks += ["Docker", "AWS", random.choice(["Kubernetes", "GCP"]), "Python"]
    if "backend" in title_lower:
        picks += ["Python", "FastAPI", "SQL", random.choice(["Docker", "AWS"])]
    if "qa" in title_lower:
        picks += ["Python", random.choice(["SQL", "Statistics"]), "Docker"]

    # Add some random noise skills
    remaining = [s for s in SKILL_BANK if s not in picks]
    random.shuffle(remaining)
    picks += remaining[: random.randint(2, 4)]

    # Deduplicate while preserving order
    seen = set()
    out = []
    for s in picks:
        if s not in seen:
            out.append(s)
            seen.add(s)
    return out[:7]


def generate_mock_jobs(n: int = 200, start_id: int = 1) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for i in range(start_id, start_id + n):
        title = random.choice(TITLES)
        company = random.choice(COMPANIES)
        location = random.choice(LOCATIONS)
        experience_level = random.choice(EXPERIENCE)
        skills = _skills_for_title(title)
        salary = _salary_str()
        posted_date = _random_date_str()

        desc_bits = [
            f"We are seeking a {experience_level.lower()} {title.lower()} for {company}.",
            f"Responsibilities include ETL pipelines, data modeling and analytics.",
            f"Required skills: {', '.join(skills)}.",
            f"This role supports product teams using Python, SQL, and modern data tooling.",
        ]
        description = " ".join(desc_bits)

        jobs.append(
            {
                "job_id": f"JOB-{i}",
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "skills": skills,
                "posted_date": posted_date,
                "experience_level": experience_level,
                "description": description,
            }
        )

    return jobs


