from config import API_BASE_URL, ZENDESK_TICKET_LEVEL_ID
import requests
from models import ZendeskTickets, ZendeskUsers, UserBacklog, Users
from helpers import generate_zendesk_headers
from app import app, engine
from sqlalchemy import select, update, and_, or_, delete
from sqlalchemy.orm import Session
import time


@app.route('/get-tickets-to-be-assigned')
def get_tickets_to_be_assigned():
    zendesk_endpoint_url = 'api/v2/search.json?page=1'
    zendesk_search_query = 'query=type:ticket assignee:none'
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
                    new_ticket = ZendeskTickets(
                        ticket_id=ticket['id'],
                        channel=ticket['via']['channel'],
                        subject=ticket['subject'],
                        created_at=ticket['created_at'].replace('T', ' ').replace('Z', ''),
                    )

                    inserted_tickets.append(ticket['id'])

                    session.add(new_ticket)
                    session.commit()  # commit changes

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    if inserted_tickets:
        return f'Tickets inseridos: {str(inserted_tickets)}'
    else:
        return f'Nenhum ticket inserido!'


@app.route('/get-user-backlog')
def get_user_backlog():
    zendesk_endpoint_url = 'api/v2/search.json?page=1'
    zendesk_search_query = 'query=type:ticket status:open status:pending status:hold'

    api_url = API_BASE_URL + zendesk_endpoint_url + '&' + zendesk_search_query

    inserted_backlog = []
    updated_backlog = []
    deleted_backlog = []
    all_tickets_in_api_return = []
    all_tickets_in_database_backlog = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        with Session(engine) as db_session:
            for ticket in api_response['results']:
                if ticket['assignee_id']:
                    zendesk_users_id = ZendeskUsers.get_zendesk_users_id(db_session, ticket['assignee_id'])
                    users_id = Users.get_user_from_zendesk_users_id(db_session, zendesk_users_id)
                    if users_id != 'null':
                        ticket_id = int(ticket['id'])
                        ticket_status = str(ticket['status'])
                        custom_fields = ticket['custom_fields']
                        for field in custom_fields:
                            if field['id'] == ZENDESK_TICKET_LEVEL_ID:  # Campo Atendimento no Zendesk
                                ticket_level = str(field['value'])
                                if ticket_level == 'None':
                                    ticket_level = ''

                        new_user_backlog = UserBacklog(
                            users_id=users_id,
                            ticket_id=ticket_id,
                            ticket_status=ticket_status,
                            ticket_level=ticket_level,
                        )

                        '''
                        Verificando se o ticket existe exatamente igual
                        '''
                        stmt = select(UserBacklog.id) \
                            .where(UserBacklog.ticket_id == new_user_backlog.ticket_id) \
                            .where(UserBacklog.users_id == new_user_backlog.users_id) \
                            .where(UserBacklog.ticket_status == new_user_backlog.ticket_status) \
                            .where(UserBacklog.ticket_level == new_user_backlog.ticket_level)
                        existing_backlog = db_session.execute(stmt).first()
                        if not existing_backlog:  # Se o ticket exatamente igual não existe, então atualizar ou inserir
                            '''
                            Verificando se o ticket existe, mas tem coisa diferente, então precisa atualizar
                            '''
                            stmt = select(UserBacklog.id) \
                                .where(
                                and_(
                                    UserBacklog.ticket_id == new_user_backlog.ticket_id
                                ),
                                or_(
                                    UserBacklog.users_id == new_user_backlog.users_id,
                                    UserBacklog.ticket_status == new_user_backlog.ticket_status,
                                    UserBacklog.ticket_level == new_user_backlog.ticket_level
                                )
                            )
                            existing_ticket_id = db_session.execute(stmt).scalar()  # scalar() pra retornar só o ticket_id
                            if existing_ticket_id:  # Se retornou o ID do ticket, então atualizar as informações
                                db_session.execute(
                                    update(UserBacklog).where(UserBacklog.id == existing_ticket_id)
                                    .values(zendesk_users_id=new_user_backlog.users_id,
                                            ticket_status=new_user_backlog.ticket_status,
                                            ticket_level=new_user_backlog.ticket_level,
                                            )
                                )
                                db_session.commit()
                                updated_backlog.append(new_user_backlog.ticket_id)
                            else:  # Se não retornou o ID do ticket, então precisa inserir
                                db_session.add(new_user_backlog)
                                db_session.commit()
                                inserted_backlog.append(new_user_backlog.ticket_id)

                all_tickets_in_api_return.append(ticket['id'])

            stmt = select(UserBacklog.ticket_id)
            for row in db_session.execute(stmt).all():
                all_tickets_in_database_backlog.append(row[0])

            tickets_to_be_removed_from_backlog = \
                [x for x in all_tickets_in_database_backlog if x not in all_tickets_in_api_return]

            for ticket_to_be_removed in tickets_to_be_removed_from_backlog:
                delete_stmt = delete(UserBacklog).where(UserBacklog.ticket_id == ticket_to_be_removed)
                db_session.execute(delete_stmt)
                db_session.commit()
                deleted_backlog.append(ticket_to_be_removed)

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    if inserted_backlog or updated_backlog or deleted_backlog:
        return f'Tickets inseridos: {str(inserted_backlog)}<br>' \
               f'Tickets atualizados: {str(updated_backlog)}<br>' \
               f'Tickets removidos: {str(deleted_backlog)}'
    else:
        return f'Nenhum backlog alterado!'


@app.route('/assign-tickets')
def assign_tickets():
    pass


@app.route('/update-ticket')
def update_ticket(ticket_id, zendesk_user_id):
    zendesk_endpoint_url = f'/api/v2/tickets/{ticket_id}'
    api_url = API_BASE_URL + zendesk_endpoint_url

    request_json = generate_assign_tickets_json(zendesk_user_id)
    api_response = requests.put(api_url, json=request_json, headers=generate_zendesk_headers()).json()

    return api_response['ticket']['status']
