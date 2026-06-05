import requests

jobs = []

# Remotive Jobs
try:
    response = requests.get(
        "https://remotive.com/api/remote-jobs",
        timeout=30
    )

    data = response.json()

    for job in data["jobs"]:
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("candidate_required_location"),
            "url": job.get("url")
        })

except Exception as e:
    print(e)

print(f"Found {len(jobs)} jobs")

for job in jobs[:10]:
    print(job["title"])
