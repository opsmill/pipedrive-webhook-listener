# Pipedrive Webhook Listener

A webhook listener for Pipedrive - Allows for custom automations not possible in Pipedrive automations.

## Purpose

This is an example of how to implement [MEDDPICC](https://duckduckgo.com/?q=meddpicc&ia=web) scoring in Pipedrive by adding 9 custom fields defined as a type `Number`. The first 8 fields are each of the MEDDPICC scores:

- Metrics
- Economic Buyer
- Decision Criteria
- Decision Process
- Paper Process
- Implications of Pain
- Champion
- Competition

It's assumed the number values of the custom fields will range from 0 to 10. It is up to the implementer to determine the meaning of each number as relevant to their MEDDPICC implementation.

The remaining field is the sum of all MEDDPICC scores:

- MEDDPICC Score

When a Pipedrive deal gets updated, it causes a webhook to run. The script `listener.py` is a simple [flask](https://flask.palletsprojects.com/en/3.0.x/) app that listens for the webhook, looks for changes in the above list of custom fields by their key, calculates a sum of all the scores, then pushes the resulting score back to Pipedrive in to a custom field called `MEDDPICC Score`.

## Requirements

- Assumes [poetry](https://python-poetry.org/) installed for python package management
- A [Pipedrive API token](https://pipedrive.readme.io/docs/how-to-find-the-api-token)
- A [Pipedrive webhook](https://pipedrive.readme.io/docs/guide-for-webhooks-v2) has been created:
  - This python script uses v2 of the Pipedrive API, and webhooks can not be setup via their WebUI. It must be done via their v2 API.
  - An example of how to setup a webhook can be found in `generate-v2-webhook.py`

## Setup

Setup the following environmental variables:

```shell
export PIPEDRIVE_API_TOKEN = "<your pipedrive api token>"
export WEBHOOK_SUBSCRIPTION_URL = "http://<site.domain.com>:5000/webhook"
export COMPANY = "<company_name>"

export MEDDPICC_SCORE_KEY = "<pipedrive_key_for_this_custom_field>"

export METRICS_KEY = "<pipedrive_key_for_this_custom_field>"
export ECONOMIC_BUYER_KEY = "<pipedrive_key_for_this_custom_field>"
export DECISION_CRITERIA_KEY = "<pipedrive_key_for_this_custom_field>"
export DECISION_PROCESS_KEY = "<pipedrive_key_for_this_custom_field>"
export PAPER_PROCESS_KEY = "<pipedrive_key_for_this_custom_field>"
export IMPLICATIONS_OF_PAIN_KEY = "<pipedrive_key_for_this_custom_field>"
export CHAMPION_KEY = "<pipedrive_key_for_this_custom_field>"
export COMPETITION_KEY = "<pipedrive_key_for_this_custom_field>"
```

## Usage

```shell
poetry install --no-root
poetry run python3 listener.py
```

## Possible Improvements

- This script looks up custom fields by their key value. It could be possible to lookup custom field by name and do away with the need to set their key values as environmental variables.
- This could also be implemented via a custom field type of `Single option` but would require a bit more logic of learning the chosen option and turning that in to a number.

Pull requests welcome!
