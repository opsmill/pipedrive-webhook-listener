import requests
import os

PIPEDRIVE_API_TOKEN = os.environ["PIPEDRIVE_API_TOKEN"]
PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1"
WEBHOOK_SUBSCRIPTION_URL = os.environ["WEBHOOK_SUBSCRIPTION_URL"]
COMPANY = os.environ["COMPANY"]

url = f"{PIPEDRIVE_API_URL}/webhooks"

headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

params = {
        "api_token": PIPEDRIVE_API_TOKEN
    }

data = {
    "subscription_url": WEBHOOK_SUBSCRIPTION_URL,
    "event_action": "change",
    "event_object": "deal",
    "version": "2.0",
}

response = requests.post(url, headers=headers, params=params, json=data)
if response.status_code == 201:
    print(f"Successfully added webhook: {response}")
else:
    print(f"Failed to add webhook. Status code: {response.status_code}")
