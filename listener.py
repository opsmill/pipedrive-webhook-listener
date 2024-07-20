from flask import Flask, request, jsonify
import requests
import os
from rich.console import Console
from rich.json import JSON
from rich.theme import Theme
import json

PIPEDRIVE_API_TOKEN = os.environ["PIPEDRIVE_API_TOKEN"]
COMPANY = os.environ["COMPANY"]
PIPEDRIVE_API_URL = f"https://{COMPANY}.pipedrive.com/api/v1"

MEDDPICC_SCORE_KEY = os.environ["MEDDPICC_SCORE_KEY"]

METRICS_KEY = os.environ["METRICS_KEY"]
ECONOMIC_BUYER_KEY = os.environ["ECONOMIC_BUYER_KEY"]
DECISION_CRITERIA_KEY = os.environ["DECISION_CRITERIA_KEY"]
DECISION_PROCESS_KEY = os.environ["DECISION_PROCESS_KEY"]
PAPER_PROCESS_KEY = os.environ["PAPER_PROCESS_KEY"]
IMPLICATIONS_OF_PAIN_KEY = os.environ["IMPLICATIONS_OF_PAIN_KEY"]
CHAMPION_KEY = os.environ["CHAMPION_KEY"]
COMPETITION_KEY = os.environ["COMPETITION_KEY"]

DEBUG = False

custom_theme = Theme(
    {
        "json.brace": "bold yellow",
        "json.bracket": "bold yellow",
        "json.colon": "bold white",
        "json.comma": "bold white",
        "json.key": "bold cyan",
        "json.value.string": "bold green",
        "json.value.number": "bold magenta",
        "json.value.boolean": "bold red",
        "json.value.null": "bold dim",
    }
)

# console = Console()
console = Console(theme=custom_theme)

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_json()
    if DEBUG:
        console.print("[bold red]DEBUG CUSTOM FIELDS[/]")
        json_string = json.dumps(payload["data"]["custom_fields"], indent=4)
        console.print(JSON(json_string))
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

    if DEBUG:
        console.print("[bold red]DEBUG DATA TO UPLOAD[/]")
        console.print(f"[bold red]URL: {url}[/]")
        console.print(f"[bold red]Params: {params}[/]")
        console.print(f"[bold red]Data: {data}[/]")

    response = requests.put(url, headers=headers, params=params, json=data)
    if response.status_code == 200:
        console.print(
            f"[bold green]Successfully updated deal {deal_id} with total sum: {total_sum}[/]"
        )
    else:
        console.print(
            f"[bold red]Failed to update deal {deal_id}. Status code: {response}[/]"
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
