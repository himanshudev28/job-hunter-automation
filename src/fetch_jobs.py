"""Fetch recent job postings and hand them off for notification.

Uses the public Remotive API (https://remotive.com/api/remote-jobs) which
requires no API key. Filter the results with the SEARCH_QUERY and
MAX_JOBS environment variables.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import requests

REMOTIVE_API = "https://remotive.com/api/remote-jobs"
DEFAULT_QUERY = "python"
DEFAULT_MAX_JOBS = 10
REQUEST_TIMEOUT = 30


def fetch_jobs(query: str, limit: int) -> list[dict[str, Any]]:
    """Return up to ``limit`` job postings matching ``query``."""
    params = {"search": query, "limit": limit}
    response = requests.get(REMOTIVE_API, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    jobs = response.json().get("jobs", [])
    return jobs[:limit]


def format_job(job: dict[str, Any]) -> str:
    """Render a single job posting as a short, readable block."""
    title = job.get("title", "Unknown role")
    company = job.get("company_name", "Unknown company")
    location = job.get("candidate_required_location", "Anywhere")
    url = job.get("url", "")
    return f"💼 *{title}*\n🏢 {company}\n🌍 {location}\n🔗 {url}"


def main() -> None:
    query = os.getenv("SEARCH_QUERY", DEFAULT_QUERY)
    limit = int(os.getenv("MAX_JOBS", DEFAULT_MAX_JOBS))

    print(f"[{datetime.now(timezone.utc).isoformat()}] Searching for '{query}' jobs...")
    jobs = fetch_jobs(query, limit)
    print(f"Found {len(jobs)} job(s).")

    if not jobs:
        print("No jobs found — nothing to notify.")
        return

    # Imported lazily so a missing token only matters when there is something to send.
    from telegram_notify import send_message

    header = f"🚀 {len(jobs)} new *{query}* job(s) found:\n"
    body = "\n\n".join(format_job(job) for job in jobs)
    send_message(f"{header}\n{body}")


if __name__ == "__main__":
    main()
