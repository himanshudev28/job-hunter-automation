import requests

KEYWORDS = [
    "frontend",
    "react",
    "next",
    "software engineer",
    "associate software engineer",
    "graduate engineer trainee",
    "junior developer",
    "entry level",
    "full stack",
    "mern",
    "java developer"
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

jobs = []

response = requests.get(
    "https://remotive.com/api/remote-jobs",
    timeout=30
)

data = response.json()

for job in data["jobs"]:

    title = job.get("title", "").lower()

    if any(keyword in title for keyword in KEYWORDS):

        jobs.append({
            "title": job.get("title"),
            "company": job.get("company_name"),
            "url": job.get("url"),
            "location": job.get("candidate_required_location")
        })

print(f"Filtered Jobs: {len(jobs)}")

for job in jobs[:25]:
    print(
        f"{job['title']} | "
        f"{job['company']} | "
        f"{job['location']}"
    )
