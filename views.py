import json
import requests
from helpers import generate_zendesk_headers
from config import *
from app import app


@app.route("/get-tickets")
def get_tickets():
    zendesk_endpoint_url = "api/v2/search.json"
    zendesk_search_query = "?query=type:ticket status:new"
    api_url = API_BASE_URL + zendesk_endpoint_url + zendesk_search_query

    response = requests.get(api_url, headers=generate_zendesk_headers())

    return str(json.dumps(response.json(), sort_keys=False, indent=4, ensure_ascii=False))


@app.route('/')
def hello_world():
    return 'Hello Woydrfydfyhrld!'
