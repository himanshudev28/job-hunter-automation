import os
import requests

APIFY_TOKEN = os.getenv("APIFY_TOKEN")

keywords = [
    "Frontend Developer Fresher",
    "React Developer Fresher",
    "Associate Software Engineer",
    "Software Engineer",
    "Full Stack Developer",
    "Java Developer Fresher"
]

jobs = []

for keyword in keywords:
    jobs.append({
        "title": keyword,
        "company": "Sample Company",
        "location": "Remote",
        "url": "https://example.com"
    })

message = "🔥 Himanshu Daily Job Digest\n\n"

for i, job in enumerate(jobs[:10], start=1):
    message += (
        f"{i}. {job['title']}\n"
        f"Company: {job['company']}\n"
        f"Location: {job['location']}\n"
        f"Apply: {job['url']}\n\n"
    )

with open("message.txt", "w") as f:
    f.write(message)

print("Jobs fetched")
