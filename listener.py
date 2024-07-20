from flask import Flask, request, jsonify
import requests
import os

PIPEDRIVE_API_TOKEN = os.environ["PIPEDRIVE_API_TOKEN"]
COMPANY = os.environ["COMPANY"]
PIPEDRIVE_API_URL = f"https://{COMPANY}.pipedrive.com/api/v1"

MEDDPICC_SCORE_KEY = "5ca44a9b86cc692ac0d5b1cc087a09b1ebb34e18"

METRICS_KEY = "d5963a386e13949b2a609db6450422bf122be4ab"
ECONOMIC_BUYER_KEY = "0892ab7022a18d2fc1939f571dbe2502f314d816"
DECISION_CRITERIA_KEY = "52c5717b0df9a00d4b2db69ea3ecb0a5adf81cf3"
DECISION_PROCESS_KEY = "89d9b1e8f9ee8d2837e7f305d9cdf7d73e8df682"
PAPER_PROCESS_KEY = "bb58c865d7a5c63389e262bb4403c3ffc49503ec"
IMPLICATIONS_OF_PAIN_KEY = "1db106e5b7613380d16098048cdd3788ba2cb983"
CHAMPION_KEY = "cb017cc71cfdfe72a427e6f3eee37c26e6afb0ab"
COMPETITION_KEY = "e7f64ff05103b77b3c3026095cf88d808b95c654"


app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_json()
    # print("DEBUG CUSTOM FIELDS:")
    # print(payload["data"]["custom_fields"])
    process_deal_update(payload)
    return jsonify(success=True), 200


def process_deal_update(payload):
    deal_id = payload["data"]["id"]
    custom_fields = payload["data"]["custom_fields"]

    relevant_fields = [
        METRICS_KEY,
        ECONOMIC_BUYER_KEY,
        DECISION_CRITERIA_KEY,
        DECISION_PROCESS_KEY,
        PAPER_PROCESS_KEY,
        IMPLICATIONS_OF_PAIN_KEY,
        CHAMPION_KEY,
        COMPETITION_KEY,
    ]
    updated_fields = [field for field in relevant_fields if field in custom_fields]

    if updated_fields:
        process_custom_fields(deal_id, custom_fields, updated_fields)


def check_metric_value(input_var):
    try:
        num = int(input_var)
        if 0 <= num <= 10:
            return num
        else:
            return 0
    except ValueError:
        return 0


def process_custom_fields(deal_id, custom_fields, updated_fields):
    numbers = []
    for field in updated_fields:
        field_value = custom_fields.get(field, "")
        try:
            numeric_value = field_value["value"]
        except TypeError:
            numeric_value = field_value
        number = check_metric_value(str(numeric_value))
        numbers.append(number)

    total_sum = sum(numbers)
    update_pipedrive_field(deal_id, total_sum)


def update_pipedrive_field(deal_id, total_sum):

    url = f"{PIPEDRIVE_API_URL}/deals/{deal_id}?api_token={PIPEDRIVE_API_TOKEN}"
    headers = {
        "Accept": "application/json",
    }

    params = {"api_token": PIPEDRIVE_API_TOKEN, "id": deal_id}

    data = {
        MEDDPICC_SCORE_KEY: total_sum,
    }

    response = requests.put(url, headers=headers, params=params, json=data)
    # if response.status_code == 200:
    #     print(f"Successfully updated deal {deal_id} with total sum: {total_sum}")
    # else:
    #     print(f"Failed to update deal {deal_id}. Status code: {response}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
