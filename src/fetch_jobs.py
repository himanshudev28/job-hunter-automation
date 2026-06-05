"""Fetch and filter real job postings for a fresher.

Two groups are produced:
  - "India"        : India-located dev jobs (big AND small companies)
  - "Foreign (WFH)": remote jobs from foreign companies that allow work-from-home

Sources (no API key required, except Adzuna which is free + optional):
  - The Muse        : India-located software jobs across target cities
  - Adzuna          : India job board incl. small companies / freshers (optional)
  - Jobicy          : remote dev jobs (foreign WFH)
  - WeWorkRemotely  : programming RSS (foreign WFH)
  - RemoteOK        : remote jobs (foreign WFH)

Import ``get_jobs()`` to get a combined, de-duplicated, filtered list. Each job
carries a ``group`` field ("India" or "Foreign (WFH)").
"""

from __future__ import annotations

import os
import urllib.parse

import feedparser
import requests

# Role-specific terms. A posting must match at least one of these. Includes
# fresher / early-career dev variants so small-company junior roles show up.
KEYWORDS = [
    "frontend",
    "front end",
    "front-end",
    "react",
    "next.js",
    "nextjs",
    "software engineer",
    "software developer",
    "associate software",
    "associate engineer",
    "graduate engineer",
    "graduate trainee",
    "junior developer",
    "junior software",
    "developer intern",
    "software intern",
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
    "sr ",
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

# India cities to search on The Muse.
INDIA_CITIES = [
    "Bangalore, India",
    "Delhi, India",
    "Noida, India",
    "Gurgaon, India",
    "Hyderabad, India",
    "Pune, India",
    "Mumbai, India",
    "Chennai, India",
]

REQUEST_TIMEOUT = 30
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; job-hunter-automation)"}

GROUP_INDIA = "India"
GROUP_FOREIGN = "Foreign (WFH)"


def _matches(title: str) -> bool:
    """Return True if a job title passes the keyword / exclude rules."""
    t = (title or "").lower()
    if not any(keyword in t for keyword in KEYWORDS):
        return False
    if any(word in t for word in EXCLUDE):
        return False
    return True


def _not_senior(title: str) -> bool:
    """Lighter check used for sources that already searched dev terms."""
    t = (title or "").lower()
    return not any(word in t for word in EXCLUDE)


def fetch_themuse() -> list[dict]:
    """Fetch India-located software jobs from The Muse (incl. mid/entry)."""
    jobs: list[dict] = []
    for city in INDIA_CITIES:
        try:
            url = (
                "https://www.themuse.com/api/public/jobs"
                "?category=Software%20Engineering"
                f"&location={urllib.parse.quote(city)}&page=0"
            )
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            for job in response.json().get("results", []):
                title = job.get("name", "")
                levels = [lv.get("name", "").lower() for lv in job.get("levels", [])]
                if "senior level" in levels or "management" in levels:
                    continue
                locations = [loc.get("name", "") for loc in job.get("locations", [])]
                if not any("india" in loc.lower() for loc in locations):
                    continue
                if not _matches(title):
                    continue
                jobs.append(
                    {
                        "title": title.strip(),
                        "company": (job.get("company", {}).get("name") or "").strip(),
                        "location": ", ".join(locations) or "India",
                        "url": job.get("refs", {}).get("landing_page", ""),
                        "source": "The Muse",
                        "group": GROUP_INDIA,
                    }
                )
        except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
            print(f"[The Muse] {city} error: {exc}")
    return jobs


def fetch_adzuna() -> list[dict]:
    """Fetch India jobs (incl. small companies / freshers) from Adzuna.

    Optional: requires the free ADZUNA_APP_ID and ADZUNA_APP_KEY env vars.
    Skipped gracefully when they are not set.
    """
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        print("[Adzuna] skipped (set ADZUNA_APP_ID and ADZUNA_APP_KEY to enable)")
        return []

    jobs: list[dict] = []
    try:
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": 50,
            "what_or": "software developer engineer frontend backend "
            "react java python full stack fresher trainee graduate",
            "what_exclude": "senior lead principal staff manager director architect",
            "max_days_old": 21,
            "sort_by": "date",
            "content-type": "application/json",
        }
        response = requests.get(
            "https://api.adzuna.com/v1/api/jobs/in/search/1",
            params=params,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        for job in response.json().get("results", []):
            title = job.get("title", "")
            # Adzuna already searched dev terms; just drop senior roles here.
            if _not_senior(title):
                jobs.append(
                    {
                        "title": title.strip(),
                        "company": (job.get("company", {}).get("display_name") or "").strip(),
                        "location": (job.get("location", {}).get("display_name") or "India").strip(),
                        "url": job.get("redirect_url", ""),
                        "source": "Adzuna",
                        "group": GROUP_INDIA,
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[Adzuna] error: {exc}")
    return jobs


def fetch_jobicy() -> list[dict]:
    """Fetch remote dev jobs from Jobicy (foreign WFH)."""
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
                        "group": GROUP_FOREIGN,
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[Jobicy] error: {exc}")
    return jobs


def fetch_weworkremotely() -> list[dict]:
    """Fetch programming jobs from WeWorkRemotely RSS (foreign WFH)."""
    jobs: list[dict] = []
    try:
        feed = feedparser.parse(
            "https://weworkremotely.com/categories/remote-programming-jobs.rss"
        )
        for entry in feed.entries:
            raw = entry.get("title", "")  # "Company Name: Role Title"
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
                        "group": GROUP_FOREIGN,
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[WeWorkRemotely] error: {exc}")
    return jobs


def fetch_remoteok() -> list[dict]:
    """Fetch remote jobs from RemoteOK (foreign WFH)."""
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
                        "location": (job.get("location") or "Remote").strip() or "Remote",
                        "url": url,
                        "source": "RemoteOK",
                        "group": GROUP_FOREIGN,
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[RemoteOK] error: {exc}")
    return jobs


def get_jobs(limit: int = 30) -> list[dict]:
    """Return India jobs first, then foreign WFH jobs; de-duplicated."""
    india_jobs = fetch_themuse() + fetch_adzuna()
    foreign_jobs = fetch_jobicy() + fetch_weworkremotely() + fetch_remoteok()

    seen: set[str] = set()
    unique: list[dict] = []
    for job in india_jobs + foreign_jobs:  # India first
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
            f"[{job['group']}] {job['title']} | {job['company']} | "
            f"{job['location']} | {job['source']}"
        )
