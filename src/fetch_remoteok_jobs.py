import requests

KEYWORDS = [
    "frontend",
    "react",
    "next",
    "software engineer",
    "associate software engineer",
    "graduate engineer trainee",
    "graduate",
    "trainee",
    "intern",
    "junior",
    "entry level",
    "full stack",
    "mern",
    "java"
]

EXCLUDE = [
    "senior",
    "staff",
    "lead",
    "principal",
    "architect",
    "manager",
    "director"
]

try:
    response = requests.get(
        "https://remoteok.com/api",
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    jobs = response.json()

    filtered_jobs = []

    for job in jobs[1:]:  # first item is metadata

        title = str(job.get("position", "")).lower()

        if (
            any(keyword in title for keyword in KEYWORDS)
            and not any(word in title for word in EXCLUDE)
        ):
            filtered_jobs.append({
                "title": job.get("position"),
                "company": job.get("company"),
                "url": f"https://remoteok.com{job.get('url', '')}"
            })

    print(f"Filtered Jobs: {len(filtered_jobs)}")

    for job in filtered_jobs[:25]:
        print(
            f"{job['title']} | "
            f"{job['company']}"
        )

except Exception as e:
    print("Error:", e)
