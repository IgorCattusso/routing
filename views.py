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

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

    inserted_tickets = []

    for ticket in api_response['results']:
        existing_ticket = ZendeskTickets.query.filter_by(ticket_id=ticket['id']).first()
        if not existing_ticket:
            new_ticket = ZendeskTickets(ticket_id=ticket['id'], channel=ticket['via']['channel'],
                                        subject=ticket['subject'],
                                        created_at=ticket['created_at'].replace('T', ' ').replace('Z', ''))

            inserted_tickets.append(ticket['id'])

            db.session.add(new_ticket)
            db.session.commit()  # commit changes

    if inserted_tickets:
        return f'Tickets inseridos: {str(inserted_tickets)}'
    else:
        return f'Nenhum ticket inserido!'


@app.route('/get-users')
def get_users():
    zendesk_endpoint_url = 'api/v2/search.json'
    zendesk_search_query = 'query=type:user routing_user:true'
    api_url = API_BASE_URL + zendesk_endpoint_url + '?' + zendesk_search_query

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

    inserted_users = []

    for user in api_response['results']:
        existing_user = ZendeskUsers.query.filter_by(zendesk_user_id=user['id']).first()
        if not existing_user:
            new_user = ZendeskUsers(zendesk_user_id=user['id'], name=user['name'],
                                    email=user['email'], suspended=match_false_true(user['suspended'])
                                    )

            inserted_users.append(user['name'])

            db.session.add(new_user)
            db.session.commit()  # commit changes

    if inserted_users:
        return f'Usuários inseridos: {str(inserted_users)}'
    else:
        return f'Nenhum usuário inserido!'


@app.route('/assign-tickets')
def assign_tickets(ticket_id, zendesk_user_id):
    zendesk_endpoint_url = f'/api/v2/tickets/{ticket_id}'
    api_url = API_BASE_URL + zendesk_endpoint_url

    request_json = generate_assign_tickets_json(zendesk_user_id)
    api_response = requests.put(api_url, json=request_json, headers=generate_zendesk_headers()).json()

    return api_response['ticket']['status']


@app.route('/get-groups')
def get_groups():
    zendesk_endpoint_url = '/api/v2/groups'
    api_url = API_BASE_URL + zendesk_endpoint_url

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

    inserted_groups = []

    for group in api_response['groups']:
        existing_group = ZendeskGroups.query.filter_by(zendesk_group_id=group['id']).first()
        if not existing_group:
            new_group = ZendeskGroups(zendesk_group_id=group['id'], name=group['name'])

            inserted_groups.append(group['name'])

            db.session.add(new_group)
            db.session.commit()  # commit changes

    if inserted_groups:
        return f'Grupos inseridos: {str(inserted_groups)}'
    else:
        return f'Nenhum grupo inserido!'


@app.route('/get-group-memberships')
def get_group_memberships():
    zendesk_endpoint_url = f'/api/v2/group_memberships.json'
    api_url = API_BASE_URL + zendesk_endpoint_url

    inserted_users_and_groups = []

    for page in get_pages_urls(api_url):
        api_response = requests.get(page, headers=generate_zendesk_headers()).json()

        for user in api_response['group_memberships']:
            existing_user_and_group = \
                ZendeskGroupMemberships.query.filter_by(
                    user_id=user['user_id']).filter_by(group_id=user['group_id']).first()

            if not existing_user_and_group:
                zendesk_user_id = ZendeskUsers.query.filter_by(zendesk_user_id=user['user_id']).first()
                zendesk_group_id = ZendeskGroups.query.filter_by(zendesk_group_id=user['group_id']).first()

                if zendesk_user_id and zendesk_group_id:
                    new_user_group = ZendeskGroupMemberships(zendesk_user_id=zendesk_user_id.id,
                                                             user_id=user['user_id'],
                                                             zendesk_group_id=zendesk_group_id.id,
                                                             group_id=user['group_id'],
                                                             default=match_false_true(user['default']))

                    user_and_group_id = str(user['user_id']) + '|' + str(user['group_id']) + '|' + str(user['default'])
                    inserted_users_and_groups.append(user_and_group_id)

                    db.session.add(new_user_group)
                    db.session.commit()  # commit changes

    if inserted_users_and_groups:
        return f'Relação de Usuários e Grupos inserida: {str(inserted_users_and_groups)}'
    else:
        return f'Nenhuma relação inserida!'


@app.route('/')
def home():
    url = API_BASE_URL + '/api/v2/group_memberships.json'
    return get_pages_urls(url)
