"""Fetch and filter real job postings from free job APIs.

Sources (no API key required):
  - Jobicy           : https://jobicy.com/api/v2/remote-jobs   (dev industry)
  - WeWorkRemotely   : programming jobs RSS feed
  - RemoteOK         : https://remoteok.com/api

Import ``get_jobs()`` from other scripts to get a combined, de-duplicated,
filtered list of jobs.
"""

from __future__ import annotations

import feedparser
import requests

# Role-specific terms. A posting must match at least one of these. Kept
# specific (e.g. "java developer" not bare "java") to avoid non-dev noise.
KEYWORDS = [
    "frontend",
    "front end",
    "front-end",
    "react",
    "next.js",
    "nextjs",
    "software engineer",
    "software developer",
    "associate software engineer",
    "graduate engineer",
    "full stack",
    "fullstack",
    "full-stack",
    "mern",
    "java developer",
    "javascript developer",
    "web developer",
    "backend",
    "back end",
    "node",
    "python developer",
    "sde",
]

# Drop senior / leadership roles — focus on fresher / early-career.
EXCLUDE = [
    "senior",
    "sr.",
    "staff",
    "lead",
    "principal",
    "architect",
    "manager",
    "director",
    "head of",
    "vp ",
]

REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-hunter-automation)"}


def _matches(title: str) -> bool:
    """Return True if a job title passes the keyword / exclude rules."""
    t = (title or "").lower()
    if not any(keyword in t for keyword in KEYWORDS):
        return False
    if any(word in t for word in EXCLUDE):
        return False
    return True


def fetch_jobicy() -> list[dict]:
    """Fetch and filter dev jobs from the Jobicy API."""
    jobs: list[dict] = []
    try:
        response = requests.get(
            "https://jobicy.com/api/v2/remote-jobs?count=50&industry=dev",
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        for job in response.json().get("jobs", []):
            title = job.get("jobTitle", "")
            if _matches(title):
                jobs.append(
                    {
                        "title": title.strip(),
                        "company": (job.get("companyName") or "").strip(),
                        "location": (job.get("jobGeo") or "Remote").strip() or "Remote",
                        "url": job.get("url", ""),
                        "source": "Jobicy",
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[Jobicy] error: {exc}")
    return jobs


def fetch_weworkremotely() -> list[dict]:
    """Fetch and filter programming jobs from the WeWorkRemotely RSS feed."""
    jobs: list[dict] = []
    try:
        feed = feedparser.parse(
            "https://weworkremotely.com/categories/remote-programming-jobs.rss"
        )
        for entry in feed.entries:
            # WWR titles look like "Company Name: Role Title".
            raw = entry.get("title", "")
            company, _, role = raw.partition(":")
            role = role.strip() or raw
            if _matches(role):
                jobs.append(
                    {
                        "title": role,
                        "company": company.strip(),
                        "location": entry.get("region", "Remote") or "Remote",
                        "url": entry.get("link", ""),
                        "source": "WeWorkRemotely",
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[WeWorkRemotely] error: {exc}")
    return jobs


def fetch_remoteok() -> list[dict]:
    """Fetch and filter jobs from the RemoteOK API."""
    jobs: list[dict] = []
    try:
        response = requests.get(
            "https://remoteok.com/api", headers=HEADERS, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        for job in response.json()[1:]:  # first element is API metadata
            if not isinstance(job, dict):
                continue
            if _matches(job.get("position", "")):
                url = job.get("url", "")
                if url and not url.startswith("http"):
                    url = f"https://remoteok.com{url}"
                jobs.append(
                    {
                        "title": (job.get("position") or "").strip(),
                        "company": (job.get("company") or "").strip(),
                        "location": (job.get("location") or "Remote").strip()
                        or "Remote",
                        "url": url,
                        "source": "RemoteOK",
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[RemoteOK] error: {exc}")
    return jobs


def get_jobs(limit: int = 25) -> list[dict]:
    """Return a combined, de-duplicated, filtered list of jobs."""
    combined = fetch_jobicy() + fetch_weworkremotely() + fetch_remoteok()

    seen: set[str] = set()
    unique: list[dict] = []
    for job in combined:
        if not job.get("title"):
            continue
        key = job.get("url") or f"{job['title']}|{job['company']}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(job)

    return unique[:limit]


if __name__ == "__main__":
    found = get_jobs()
    print(f"Total filtered jobs: {len(found)}\n")
    for job in found:
        print(
            f"{job['title']} | {job['company']} | {job['location']} | {job['source']}"
        )
