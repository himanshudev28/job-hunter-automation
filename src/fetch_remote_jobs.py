import requests

url = "https://remotive.com/api/remote-jobs"

response = requests.get(url)

data = response.json()

print("Jobs Found:", len(data["jobs"]))

for job in data["jobs"][:5]:
    print(job["title"])
