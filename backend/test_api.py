import requests

response = requests.post(
    "http://127.0.0.1:8000/api/jobs/scrape",
    json={"query": "Software Engineer", "location": "Remote"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
