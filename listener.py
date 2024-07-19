from flask import Flask, request, jsonify
import re
import requests
import os

PIPEDRIVE_API_TOKEN = os.environ["PIPEDRIVE_API_TOKEN"]
PIPEDRIVE_API_URL = "https://api.pipedrive.com/v1"

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_json()
    print("DEBUG PAYLOAD:")
    print(payload)
    process_deal_update(payload)
    return jsonify(success=True), 200


def process_deal_update(payload):
    deal_id = payload["current"]["id"]
    custom_fields = payload["current"]["custom_fields"]

    relevant_fields = ["Metrics", "Economic Buyer", "Decision Criteria", "Decision Process", "Paper Process", "Implications of Pain", "Champion", "Competition"]
    updated_fields = [field for field in relevant_fields if field in custom_fields]

    if updated_fields:
        process_custom_fields(deal_id, custom_fields, updated_fields)


def extract_number(text):
    match = re.match(r"^\d+", text)
    return int(match.group()) if match else 0

def process_custom_fields(deal_id, custom_fields, updated_fields):
    numbers = []
    for field in updated_fields:
        value = custom_fields.get(field, "")
        number = extract_number(str(value))
        numbers.append(number)

    total_sum = sum(numbers)
    update_pipedrive_field(deal_id, total_sum)

def update_pipedrive_field(deal_id, total_sum):
    url = f"{PIPEDRIVE_API_URL}/deals/{deal_id}?api_token={PIPEDRIVE_API_TOKEN}"

    data = {
        "custom_fields": {
            "MEDDPICC Score": total_sum
        }
    }

    response = requests.put(url, json=data)
    if response.status_code == 200:
        print(f"Successfully updated deal {deal_id} with total sum: {total_sum}")
    else:
        print(f"Failed to update deal {deal_id}. Status code: {response.status_code}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
