import requests
from requests.auth import HTTPBasicAuth
import json
import os
from dotenv import load_dotenv

load_dotenv()

# TODO: Replace these with your actual credentials
EMAIL = os.getenv("ATLASSIAN_EMAIL")  # your Atlassian login email
API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")  # paste the token here
DOMAIN = os.getenv("ATLASSIAN_DOMAIN")  # your Jira domain, like example.atlassian.net

# API Endpoint
url = f"https://{DOMAIN}/rest/api/3/search"

# Basic authentication
auth = HTTPBasicAuth(EMAIL, API_TOKEN)

# Headers and JQL (Jira Query Language)
headers = {
    "Accept": "application/json"
}

query = {
    'jql': 'project = ASP',  # fetches tasks assigned to you
    'maxResults': 50
}

# Make the request
response = requests.get(url, headers=headers, params=query, auth=auth)

# Parse JSON response
data = response.json()

# Save response to file
with open("../data/raw_issues.json", "w", encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("✅ Jira issues fetched and saved to data/raw_issues.json")
