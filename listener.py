import asyncio
import base64
import os
import json

try:
    import requests
    from flask import Flask, request, jsonify

    from rich.console import Console
    from rich.json import JSON
    from rich.theme import Theme
except ImportError:
    if __name__ != "__main__":
        pass

if __name__ != "__main__":
    from js import Object, Response, Headers, fetch, JSON
    from pyodide.ffi import to_js as _to_js
    from urllib.parse import urlparse

    def to_js(obj):
        return _to_js(obj, dict_converter=Object.fromEntries)


PIPEDRIVE_API_TOKEN = os.environ.get("PIPEDRIVE_API_TOKEN")
COMPANY = os.environ.get("COMPANY")
PIPEDRIVE_API_URL = f"https://{COMPANY}.pipedrive.com/api/v1"

MEDDPICC_SCORE_KEY = os.environ.get("MEDDPICC_SCORE_KEY")

METRICS_KEY = os.environ.get("METRICS_KEY")
ECONOMIC_BUYER_KEY = os.environ.get("ECONOMIC_BUYER_KEY")
DECISION_CRITERIA_KEY = os.environ.get("DECISION_CRITERIA_KEY")
DECISION_PROCESS_KEY = os.environ.get("DECISION_PROCESS_KEY")
PAPER_PROCESS_KEY = os.environ.get("PAPER_PROCESS_KEY")
IMPLICATIONS_OF_PAIN_KEY = os.environ.get("IMPLICATIONS_OF_PAIN_KEY")
CHAMPION_KEY = os.environ.get("CHAMPION_KEY")
COMPETITION_KEY = os.environ.get("COMPETITION_KEY")

AUTH_USER = os.environ.get("AUTH_USER")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD")


def get_env(env):
    global \
        PIPEDRIVE_API_TOKEN, \
        COMPANY, \
        PIPEDRIVE_API_URL, \
        MEDDPICC_SCORE_KEY, \
        METRICS_KEY
    global \
        ECONOMIC_BUYER_KEY, \
        DECISION_CRITERIA_KEY, \
        DECISION_PROCESS_KEY, \
        PAPER_PROCESS_KEY
    global \
        IMPLICATIONS_OF_PAIN_KEY, \
        CHAMPION_KEY, \
        COMPETITION_KEY, \
        AUTH_USER, \
        AUTH_PASSWORD

    PIPEDRIVE_API_TOKEN = env.PIPEDRIVE_API_TOKEN
    COMPANY = env.COMPANY
    PIPEDRIVE_API_URL = f"https://{COMPANY}.pipedrive.com/api/v1"

    MEDDPICC_SCORE_KEY = env.MEDDPICC_SCORE_KEY

    METRICS_KEY = env.METRICS_KEY
    ECONOMIC_BUYER_KEY = env.ECONOMIC_BUYER_KEY
    DECISION_CRITERIA_KEY = env.DECISION_CRITERIA_KEY
    DECISION_PROCESS_KEY = env.DECISION_PROCESS_KEY
    PAPER_PROCESS_KEY = env.PAPER_PROCESS_KEY
    IMPLICATIONS_OF_PAIN_KEY = env.IMPLICATIONS_OF_PAIN_KEY
    CHAMPION_KEY = env.CHAMPION_KEY
    COMPETITION_KEY = env.COMPETITION_KEY

    AUTH_USER = env.AUTH_USER
    AUTH_PASSWORD = env.AUTH_PASSWORD


DEBUG = False

if __name__ == "__main__":
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
        if AUTH_USER:
            if not do_basic_auth(request.headers.get("Authorization")):
                return jsonify(success=False), 403

        payload = request.get_json()
        if DEBUG:
            console.print("[bold red]DEBUG CUSTOM FIELDS[/]")
            json_string = json.dumps(payload["data"]["custom_fields"], indent=4)
            console.print(JSON(json_string))
        asyncio.run(process_deal_update(payload))
        return jsonify(success=True), 200
else:

    async def on_fetch(request, env):
        get_env(env)

        if AUTH_USER:
            if not do_basic_auth(request.headers.get("Authorization")):
                return Response.new("Denied", status=403)

        url = urlparse(request.url)

        if (
            url.path == "/webhook"
            and request.method == "POST"
            and request.body is not None
        ):
            payload = (
                await request.text()
            )  # use text() instead of json() to have a dict instead of JSON object
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                return Response.new("Could not fetch payload", status=400)

            await process_deal_update(payload)

            headers = Headers.new({"content-type": "application/json"}.items())
            return Response.new(json.dumps({"success": True}), headers=headers)

        return Response.new("Pipedrive webhook")


def do_basic_auth(auth_header):
    if not auth_header:
        return False
    creds = base64.b64decode(auth_header.split()[-1]).decode("utf-8").split(":")
    if creds[0] != AUTH_USER or creds[1] != AUTH_PASSWORD:
        return False

    return True


async def process_deal_update(payload):
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
        await process_custom_fields(deal_id, custom_fields, updated_fields)


def check_metric_value(input_var):
    try:
        num = int(input_var)
        if 0 <= num <= 10:
            return num
        else:
            return 0
    except ValueError:
        return 0


async def process_custom_fields(deal_id, custom_fields, updated_fields):
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
    await update_pipedrive_field(deal_id, total_sum)


async def update_pipedrive_field(deal_id, total_sum):
    url = f"{PIPEDRIVE_API_URL}/deals/{deal_id}?api_token={PIPEDRIVE_API_TOKEN}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    params = {"api_token": PIPEDRIVE_API_TOKEN, "id": deal_id}

    data = {
        MEDDPICC_SCORE_KEY: total_sum,
    }

    if DEBUG:
        console.print("[bold red]DEBUG DATA TO UPLOAD[/]")
        console.print(f"[bold red]URL: {url}[/]")
        console.print(f"[bold red]Params: {params}[/]")
        console.print(f"[bold red]Data: {data}[/]")

    if __name__ == "__main__":
        response = requests.put(url, headers=headers, params=params, json=data)
        if response.status_code == 200:
            console.print(
                f"[bold green]Successfully updated deal {deal_id} with total sum: {total_sum}[/]"
            )
        else:
            console.print(
                f"[bold red]Failed to update deal {deal_id}. Status code: {response}[/]"
            )
    else:
        options = {"body": json.dumps(data), "method": "PUT", "headers": headers}
        response = await fetch(url, to_js(options))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
