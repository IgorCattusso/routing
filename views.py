import requests
from helpers import *
from config import *
from app import *
from models import *
from sqlalchemy import URL, create_engine, String, ForeignKey, insert, Table, Column, MetaData, Integer, select, \
    bindparam, func, cast, and_, or_, text
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, Session
import pymysql

engine = create_engine(url_object)


@app.route('/get-users')
def get_users():
    zendesk_endpoint_url = 'api/v2/search.json?page=1'
    zendesk_search_query = 'query=type:user routing_user:true'
    api_url = API_BASE_URL + zendesk_endpoint_url + '&' + zendesk_search_query

    inserted_users = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for user in api_response['results']:
            stmt = select(ZendeskUsers).where(ZendeskUsers.zendesk_user_id == user['id'])
            with Session(engine) as session:
                query_result = session.execute(stmt).first()
                if not query_result:
                    new_user = ZendeskUsers(zendesk_user_id=user['id'],
                                            name=user['name'],
                                            email=user['email'],
                                            suspended=match_false_true(user['suspended']))
                    inserted_users.append(user['name'])
                    session.add(new_user)
                    session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    if inserted_users:
        return f'Usuários inseridos: {str(inserted_users)}'
    else:
        return f'Nenhum usuário inserido!'


@app.route('/get-groups')
def get_groups():
    zendesk_endpoint_url = '/api/v2/groups.json?page=1'
    api_url = API_BASE_URL + zendesk_endpoint_url

    inserted_groups = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for group in api_response['groups']:
            stmt = select(ZendeskGroups).where(ZendeskGroups.zendesk_group_id == group['id'])
            with Session(engine) as session:
                query_result = session.execute(stmt).first()
                if not query_result:
                    new_group = ZendeskGroups(zendesk_group_id=group['id'],
                                              name=group['name'])
                    inserted_groups.append(group['name'])
                    session.add(new_group)
                    session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    if inserted_groups:
        return f'Grupos inseridos: {str(inserted_groups)}'
    else:
        return f'Nenhum grupo inserido!'


@app.route('/get-group-memberships')
def get_group_memberships():
    zendesk_endpoint_url = f'/api/v2/group_memberships.json?page=1'
    api_url = API_BASE_URL + zendesk_endpoint_url

    inserted_users_and_groups = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for user in api_response['group_memberships']:
            stmt = select(ZendeskGroupMemberships) \
                .where(ZendeskGroupMemberships.user_id == user['user_id']) \
                .where(ZendeskGroupMemberships.group_id == user['group_id'])
            with Session(engine) as session:
                query_result = session.execute(stmt).first()
                if not query_result:
                    user_in_database = \
                        session.execute(select(ZendeskUsers)
                                        .where(ZendeskUsers.zendesk_user_id == str(user['user_id']))).scalar()
                    group_in_database = \
                        session.execute(select(ZendeskGroups)
                                        .where(ZendeskGroups.zendesk_group_id == str(user['group_id']))).scalar()
                    if user_in_database and group_in_database:
                        new_user_group = ZendeskGroupMemberships(zendesk_user_id=user_in_database.id,
                                                                 user_id=user['user_id'],
                                                                 zendesk_group_id=group_in_database.id,
                                                                 group_id=user['group_id'],
                                                                 default=match_false_true(user['default'])
                                                                 )
                        session.add(new_user_group)
                        session.commit()
                        inserted_users_and_groups.append(user['user_id'])

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    if inserted_users_and_groups:
        return f'Relação de Usuários e Grupos inserida: {str(inserted_users_and_groups)}'
    else:
        return 'Nenhuma relação inserida!'


@app.route('/get-new-tickets')
def get_new_tickets():
    zendesk_endpoint_url = 'api/v2/search.json?page=1'
    zendesk_search_query = 'query=type:ticket status:new'
    api_url = API_BASE_URL + zendesk_endpoint_url + '&' + zendesk_search_query

    inserted_tickets = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for ticket in api_response['results']:
            stmt = select(ZendeskTickets).where(ZendeskTickets.ticket_id == str(ticket['id']))
            with Session(engine) as session:
                existing_ticket = session.execute(stmt).first()
                if not existing_ticket:
                    new_ticket = ZendeskTickets(ticket_id=ticket['id'], channel=ticket['via']['channel'],
                                                subject=ticket['subject'],
                                                created_at=ticket['created_at'].replace('T', ' ').replace('Z', ''))

                    inserted_tickets.append(ticket['id'])

                    session.add(new_ticket)
                    session.commit()  # commit changes

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    if inserted_tickets:
        return f'Tickets inseridos: {str(inserted_tickets)}'
    else:
        return f'Nenhum ticket inserido!'


@app.route('/assign-tickets')
def assign_tickets():
    tickets = ZendeskTickets.query \
        .join(AssignedTickets, ZendeskTickets.id == AssignedTickets.zendesk_tickets_id, isouter=True)

    q = AssignedTickets.query.with_entities(AssignedTickets.zendesk_users_id, func.count(AssignedTickets.id)) \
        .group_by(AssignedTickets.zendesk_users_id).first()

    return str(tickets)


@app.route('/update-ticket')
def update_ticket(ticket_id, zendesk_user_id):
    zendesk_endpoint_url = f'/api/v2/tickets/{ticket_id}'
    api_url = API_BASE_URL + zendesk_endpoint_url

    request_json = generate_assign_tickets_json(zendesk_user_id)
    api_response = requests.put(api_url, json=request_json, headers=generate_zendesk_headers()).json()

    return api_response['ticket']['status']


@app.route('/')
def home():
    return 'Home'
