import json
import requests
from helpers import generate_zendesk_headers
from config import *
from app import app, db
from models import zendesk_tickets


@app.route("/get-tickets")
def get_tickets():
    zendesk_endpoint_url = "api/v2/search.json"
    zendesk_search_query = "?query=type:ticket status:new"
    api_url = API_BASE_URL + zendesk_endpoint_url + zendesk_search_query

    api_response = requests.get(api_url, headers=generate_zendesk_headers())

    data = api_response.json()

    results = data['results']

    for ticket in results:
        new_ticket = zendesk_tickets(ticket_id=ticket['id'], channel=ticket['via']['channel'],
                                     subject=ticket['subject'],
                                     created_at=ticket['created_at'].replace("T", " ").replace("Z", ""))

        db.session.add(new_ticket)
        db.session.commit()  # commit changes

    return str(json.dumps(api_response.json(), sort_keys=False, indent=4, ensure_ascii=False))
