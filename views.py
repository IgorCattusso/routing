import json
import requests
from helpers import *
from config import *
from app import app, db
from models import *


@app.route('/get-tickets')
def get_tickets():
    zendesk_endpoint_url = 'api/v2/search.json'
    zendesk_search_query = 'query=type:ticket status:new'
    api_url = API_BASE_URL + zendesk_endpoint_url + '?' + zendesk_search_query

    api_response = requests.get(api_url, headers=generate_zendesk_headers())

    data = api_response.json()

    results = data['results']

    inserted_tickets = []

    for ticket in results:
        existing_ticket = zendesk_tickets.query.filter_by(ticket_id=ticket['id']).first()
        if not existing_ticket:
            new_ticket = zendesk_tickets(ticket_id=ticket['id'], channel=ticket['via']['channel'],
                                         subject=ticket['subject'],
                                         created_at=ticket['created_at'].replace('T', ' ').replace('Z', ''))

            inserted_tickets.append(ticket['id'])

            db.session.add(new_ticket)
            db.session.commit()  # commit changes

    if inserted_tickets:
        return f'Usuários inseridos: {str(inserted_tickets)}'
    else:
        return f'Nenhum ticket inserido!'


@app.route('/get-users')
def get_users():
    for group in ZENDESK_SUPPORT_GROUP_ID:
        zendesk_endpoint_url = f'/api/v2/groups/{group}/users'
        api_url = API_BASE_URL + zendesk_endpoint_url

        api_response = requests.get(api_url, headers=generate_zendesk_headers())

        data = api_response.json()

        results = data['users']

        inserted_users = []

        for user in results:
            existing_ticket = zendesk_users.query.filter_by(zendesk_user_id=user['id']).first()
            if not existing_ticket:
                new_user = zendesk_users(zendesk_user_id=user['id'], name=user['name'],
                                         email=user['email'], suspended=match_false_true(user['suspended'])
                                         )

                inserted_users.append(user['name'])

                db.session.add(new_user)
                db.session.commit()  # commit changes

        if inserted_users:
            return f'Usuários inseridos: {str(inserted_users)}'
        else:
            return f'Nenhum usuário inserido!'


@app.route('/')
def home():
    return 'Hello World!'
