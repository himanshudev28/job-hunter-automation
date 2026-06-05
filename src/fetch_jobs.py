"""Fetch and filter real job postings, focused on India + open-remote roles.

Sources (no API key required):
  - The Muse        : India-located software jobs across your target cities
  - Jobicy          : remote dev jobs (kept only if open to India / worldwide)
  - WeWorkRemotely  : programming RSS (kept only if "Anywhere in the World")
  - RemoteOK        : remote jobs (kept only if India / worldwide)

Import ``get_jobs()`` to get a combined, de-duplicated, filtered list.
"""

from __future__ import annotations

import urllib.parse

import feedparser
import requests

# Role-specific terms. A posting must match at least one of these.
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

# For remote feeds: keep a job only if it is open to India or fully worldwide.
OPEN_LOCATIONS = ["india", "anywhere", "worldwide", "global"]

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


def _is_open_remote(location: str) -> bool:
    """True if a remote-feed location is open to India or fully worldwide."""
    return any(loc in (location or "").lower() for loc in OPEN_LOCATIONS)


def fetch_themuse() -> list[dict]:
    """Fetch India-located software jobs from The Muse."""
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
                # Keep only genuinely India-located roles.
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
                    }
                )
        except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
            print(f"[The Muse] {city} error: {exc}")
    return jobs


def fetch_jobicy() -> list[dict]:
    """Fetch dev jobs from Jobicy, kept only if open to India / worldwide."""
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
            geo = (job.get("jobGeo") or "").strip()
            if _matches(title) and _is_open_remote(geo):
                jobs.append(
                    {
                        "title": title.strip(),
                        "company": (job.get("companyName") or "").strip(),
                        "location": geo or "Remote",
                        "url": job.get("url", ""),
                        "source": "Jobicy",
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[Jobicy] error: {exc}")
    return jobs


def fetch_weworkremotely() -> list[dict]:
    """Fetch programming jobs from WeWorkRemotely (worldwide-open only)."""
    jobs: list[dict] = []
    try:
        feed = feedparser.parse(
            "https://weworkremotely.com/categories/remote-programming-jobs.rss"
        )
        for entry in feed.entries:
            raw = entry.get("title", "")  # "Company Name: Role Title"
            company, _, role = raw.partition(":")
            role = role.strip() or raw
            region = entry.get("region", "") or ""
            if _matches(role) and _is_open_remote(region):
                jobs.append(
                    {
                        "title": role,
                        "company": company.strip(),
                        "location": region or "Anywhere in the World",
                        "url": entry.get("link", ""),
                        "source": "WeWorkRemotely",
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[WeWorkRemotely] error: {exc}")
    return jobs


def fetch_remoteok() -> list[dict]:
    """Fetch jobs from RemoteOK, kept only if open to India / worldwide."""
    jobs: list[dict] = []
    try:
        response = requests.get(
            "https://remoteok.com/api", headers=HEADERS, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        for job in response.json()[1:]:  # first element is API metadata
            if not isinstance(job, dict):
                continue
            location = job.get("location") or ""
            # RemoteOK with no location is global remote — keep it.
            open_remote = (not location.strip()) or _is_open_remote(location)
            if _matches(job.get("position", "")) and open_remote:
                url = job.get("url", "")
                if url and not url.startswith("http"):
                    url = f"https://remoteok.com{url}"
                jobs.append(
                    {
                        "title": (job.get("position") or "").strip(),
                        "company": (job.get("company") or "").strip(),
                        "location": location.strip() or "Remote",
                        "url": url,
                        "source": "RemoteOK",
                    }
                )
    except Exception as exc:  # noqa: BLE001 - keep one source failure non-fatal
        print(f"[RemoteOK] error: {exc}")
    return jobs


def get_jobs(limit: int = 25) -> list[dict]:
    """Return India-located jobs first, then open-remote jobs; de-duplicated."""
    india_jobs = fetch_themuse()
    remote_jobs = fetch_jobicy() + fetch_weworkremotely() + fetch_remoteok()

    seen: set[str] = set()
    unique: list[dict] = []
    for job in india_jobs + remote_jobs:  # India first
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
