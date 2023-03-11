import requests
from helpers import *
from config import *
from app import app
from models import *
from sqlalchemy import create_engine, select, update, and_, or_, delete
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

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
        with Session(engine) as session:
            for ticket in api_response['results']:
                if ticket['assignee_id']:
                    zendesk_users_id = ZendeskUsers.get_zendesk_users_id(ticket['assignee_id'])
                    if zendesk_users_id != 'null':
                        ticket_id = int(ticket['id'])
                        ticket_status = str(ticket['status'])
                        custom_fields = ticket['custom_fields']
                        for field in custom_fields:
                            if field['id'] == ZENDESK_TICKET_LEVEL_ID:
                                ticket_level = str(field['value'])
                                if ticket_level == 'None':
                                    ticket_level = ''

                        new_user_backlog = ZendeskUserBacklog(
                            zendesk_users_id=zendesk_users_id,
                            ticket_id=ticket_id,
                            ticket_status=ticket_status,
                            ticket_level=ticket_level
                        )

                        # Se existe exatamente igual não fazer nada → é só não criar condição pra isso
                        # Se existe, mas tem coisa diferente, atualizar
                        # Se não existe, inserir
                        # No final, verificar se tem ticket no banco mas não na API
                        # Se existe, deletar do banco

                        '''
                        Verificando se o ticket existe exatamente igual
                        '''
                        stmt = select(ZendeskUserBacklog.id) \
                            .where(ZendeskUserBacklog.ticket_id == new_user_backlog.ticket_id) \
                            .where(ZendeskUserBacklog.zendesk_users_id == new_user_backlog.zendesk_users_id) \
                            .where(ZendeskUserBacklog.ticket_status == new_user_backlog.ticket_status) \
                            .where(ZendeskUserBacklog.ticket_level == new_user_backlog.ticket_level)
                        existing_backlog = session.execute(stmt).first()
                        if not existing_backlog:  # Se o ticket exatamente igual não existe, então atualizar ou inserir
                            '''
                            Verificando se o ticket existe, mas tem coisa diferente, então precisa atualizar
                            '''
                            stmt = select(ZendeskUserBacklog.id) \
                                .where(
                                and_(
                                    ZendeskUserBacklog.ticket_id == new_user_backlog.ticket_id
                                ),
                                or_(
                                    ZendeskUserBacklog.zendesk_users_id == new_user_backlog.zendesk_users_id,
                                    ZendeskUserBacklog.ticket_status == new_user_backlog.ticket_status,
                                    ZendeskUserBacklog.ticket_level == new_user_backlog.ticket_level
                                )
                            )
                            existing_ticket_id = session.execute(stmt).scalar()  # scalar() pra retornar só o ticket_id
                            if existing_ticket_id:  # Se retornou o ID do ticket, então atualizar as informações
                                session.execute(
                                    update(ZendeskUserBacklog).where(ZendeskUserBacklog.id == existing_ticket_id)
                                    .values(zendesk_users_id=new_user_backlog.zendesk_users_id,
                                            ticket_status=new_user_backlog.ticket_status,
                                            ticket_level=new_user_backlog.ticket_level)
                                )
                                session.commit()
                                updated_backlog.append(new_user_backlog.ticket_id)
                            else:  # Se não retornou o ID do ticket, então precisa inserir
                                session.add(new_user_backlog)
                                session.commit()
                                inserted_backlog.append(new_user_backlog.ticket_id)

                all_tickets_in_api_return.append(ticket['id'])

            stmt = select(ZendeskUserBacklog.ticket_id)
            for row in session.execute(stmt).all():
                all_tickets_in_database_backlog.append(row[0])

            tickets_to_be_removed_from_backlog = \
                [x for x in all_tickets_in_database_backlog if x not in all_tickets_in_api_return]

            for ticket_to_be_removed in tickets_to_be_removed_from_backlog:
                delete_stmt = delete(ZendeskUserBacklog).where(ZendeskUserBacklog.ticket_id == ticket_to_be_removed)
                session.execute(delete_stmt)
                session.commit()
                deleted_backlog.append(ticket_to_be_removed)

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    if inserted_backlog or updated_backlog or deleted_backlog:
        return f'Tickets inseridos: {str(inserted_backlog)}<br>' \
               f'Tickets atualizados: {str(updated_backlog)}<br>' \
               f'Tickets removidos: {str(deleted_backlog)}'
    else:
        return f'Nenhum backlog alterado!'


@app.route('/assign-tickets')
def assign_tickets():
    pass
    # tickets que precisam ser distribuídos
    # tickets = select(ZendeskTickets).outerjoin(AssignedTickets).where(AssignedTickets.id == None)
    # backlog = select(UserBacklog)

    # return str(tickets)
    # >>> SELECT * FROM zendesk_tickets
    # ... LEFT OUTER JOIN assigned_tickets
    # ... ON zendesk_tickets.id = assigned_tickets.zendesk_tickets_id
    # ... WHERE assigned_tickets.id IS NULL


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
