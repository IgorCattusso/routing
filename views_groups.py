from views import *
from helpers import *
from config import *
from app import app
from models import *
from sqlalchemy import create_engine, select, case, desc
from sqlalchemy.orm import Session
from flask import render_template, flash, redirect, url_for

engine = create_engine(url_object)


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
        flash(f'Grupos inseridos: {str(inserted_groups)}')
        return redirect(url_for('groups'))
    else:
        flash(f'Nenhum grupo inserido!')
        return redirect(url_for('groups'))


@app.route('/get-all-group-memberships')
def get_all_group_memberships():
    zendesk_endpoint_url = f'/api/v2/group_memberships.json?page=1'
    api_url = API_BASE_URL + zendesk_endpoint_url

    inserted_users_and_groups = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for user in api_response['group_memberships']:
            stmt = select(ZendeskGroupMemberships) \
                .where(ZendeskGroupMemberships.user_id_on_zendesk == user['user_id']) \
                .where(ZendeskGroupMemberships.group_id_on_zendesk == user['group_id'])
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
                        new_user_group = ZendeskGroupMemberships(zendesk_users_id=user_in_database.id,
                                                                 user_id_on_zendesk=user['user_id'],
                                                                 zendesk_groups_id=group_in_database.id,
                                                                 group_id_on_zendesk=user['group_id'],
                                                                 default=match_false_true(user['default'])
                                                                 )
                        session.add(new_user_group)
                        session.commit()
                        inserted_users_and_groups.append(f"Usuário: {user['user_id']} | Grupo: {user['group_id']}")

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    if inserted_users_and_groups:
        flash(f'Relação de usuários inseridos: {str(inserted_users_and_groups)}')
        return redirect(url_for('groups'))
    else:
        flash(f'Nenhuma relação inserida!')
        return redirect(url_for('groups'))


@app.route('/get-group-memberships/<int:group_id>')
def get_group_memberships(group_id):
    with Session(engine) as session:
        stmt = select(ZendeskGroups.zendesk_group_id) \
            .where(ZendeskGroups.id == group_id)
        group_id_on_zendesk = session.execute(stmt).scalar()

    zendesk_endpoint_url = f'/api/v2/groups/{group_id_on_zendesk}/memberships.json?page=1'
    api_url = API_BASE_URL + zendesk_endpoint_url

    inserted_users_and_groups = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for user in api_response['group_memberships']:
            stmt = select(ZendeskGroupMemberships) \
                .where(ZendeskGroupMemberships.user_id_on_zendesk == user['user_id']) \
                .where(ZendeskGroupMemberships.group_id_on_zendesk == user['group_id'])
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
                        new_user_group = ZendeskGroupMemberships(zendesk_users_id=user_in_database.id,
                                                                 user_id_on_zendesk=user['user_id'],
                                                                 zendesk_groups_id=group_in_database.id,
                                                                 group_id_on_zendesk=user['group_id'],
                                                                 default=match_false_true(user['default'])
                                                                 )
                        session.add(new_user_group)
                        session.commit()
                        inserted_users_and_groups.append(user['user_id'])

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    if inserted_users_and_groups:
        flash(f'Usuários inseridos: {str(inserted_users_and_groups)}')
        return redirect(url_for('get_users_in_group', group_id=group_id))
    else:
        flash(f'Nenhum usuário inserido!')
        return redirect(url_for('get_users_in_group', group_id=group_id))


@app.route('/users-in-group/<int:group_id>')
def get_users_in_group(group_id):
    stmt = select(
        ZendeskGroupMemberships.id,
        ZendeskGroupMemberships.group_id_on_zendesk,
        ZendeskGroupMemberships.user_id_on_zendesk,
        ZendeskUsers.name.label('user_name'),
        ZendeskGroups.name.label('group_name'),
        case(
            (ZendeskGroupMemberships.default == 1, 'Sim'),
            (ZendeskGroupMemberships.default == 0, 'Não'),
            else_='')
        .label('default')) \
        .join(ZendeskUsers) \
        .join(ZendeskGroups) \
        .where(ZendeskGroupMemberships.zendesk_groups_id == group_id)

    with Session(engine) as session:
        group_memberships = session.execute(stmt).all()
        group = session.execute(stmt).first()

    if group:
        return render_template('users-in-group.html', titulo='Groups',
                               group_memberships=group_memberships, group_name=group.group_name, group_id=group_id)
    else:
        with Session(engine) as session:
            stmt = select(ZendeskGroups.name).where(ZendeskGroups.id == group_id)
            group_name = session.execute(stmt).scalar()
        return render_template('users-in-group.html', titulo='Groups',
                               group_memberships=group_memberships, group_name=group_name, group_id=group_id)
