import os
import requests
from dotenv import load_dotenv
import json

# Load credentials from .env
load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Adzuna API — search for data analyst jobs in South Africa
url = "https://api.adzuna.com/v1/api/jobs/za/search/1"
params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": 3,
    "what": "data analyst",
    "content-type": "application/json"
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

# Print the raw JSON of the first job
print("=" * 60)
print("SAMPLE JOB POSTING (raw JSON):")
print("=" * 60)
print(json.dumps(data["results"][0], indent=2))

print("\n" + "=" * 60)
print(f"Total results available: {data['count']}")
print("=" * 60)