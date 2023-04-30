from config import ZENDESK_BASE_URL
from models import ZendeskGroups, ZendeskGroupMemberships, ZendeskUsers
from helpers import generate_zendesk_headers, match_false_true, internal_render_template
import requests
from app import app, engine
from sqlalchemy import select, case
from sqlalchemy.orm import Session
from flask import flash, redirect, url_for
import time


@app.route('/get-zendesk-groups')
def get_zendesk_groups():
    zendesk_endpoint_url = '/api/v2/groups.json?page=1'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

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
                                              name=group['name'],
                                              )
                    inserted_groups.append(group['name'])
                    session.add(new_group)
                    session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    if inserted_groups:
        flash(f'Grupos inseridos: {str(inserted_groups)}')
        return redirect(url_for('zendesk_groups'))
    else:
        flash(f'Nenhum grupo inserido!')
        return redirect(url_for('zendesk_groups'))


@app.route('/get-all-zendesk-group-memberships')
def get_all_zendesk_group_memberships():
    zendesk_endpoint_url = f'/api/v2/group_memberships.json?page=1'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

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
                                                                 default=match_false_true(user['default']),
                                                                 )
                        session.add(new_user_group)
                        session.commit()
                        inserted_users_and_groups.append(f"Usuário: {user['user_id']} | Grupo: {user['group_id']}")

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    if inserted_users_and_groups:
        flash(f'Relação de usuários inseridos: {str(inserted_users_and_groups)}')
        return redirect(url_for('zendesk_groups'))
    else:
        flash(f'Nenhuma relação inserida!')
        return redirect(url_for('zendesk_groups'))


@app.route('/get-zendesk-group-memberships/<int:group_id>')
def get_zendesk_group_memberships(group_id):
    with Session(engine) as session:
        stmt = select(ZendeskGroups.zendesk_group_id) \
            .where(ZendeskGroups.id == group_id)
        group_id_on_zendesk = session.execute(stmt).scalar()

    zendesk_endpoint_url = f'/api/v2/groups/{group_id_on_zendesk}/memberships.json?page=1'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

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
                                                                 default=match_false_true(user['default']),
                                                                 )
                        session.add(new_user_group)
                        session.commit()
                        inserted_users_and_groups.append(user['user_id'])

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    if inserted_users_and_groups:
        flash(f'Usuários inseridos: {str(inserted_users_and_groups)}')
        return redirect(url_for('get_zendesk_users_in_group', group_id=group_id))
    else:
        flash(f'Nenhum usuário inserido!')
        return redirect(url_for('get_zendesk_users_in_group', group_id=group_id))


@app.route('/zendesk-users-in-group/<int:group_id>')
def get_zendesk_users_in_group(group_id):
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

    time.sleep(.35)

    if group:
        return internal_render_template(
            'zendesk-users-in-group.html',
            titulo='Groups',
            group_memberships=group_memberships,
            group_name=group.group_name,
            group_id=group_id,
        )
    else:
        with Session(engine) as session:
            stmt = select(ZendeskGroups.name).where(ZendeskGroups.id == group_id)
            group_name = session.execute(stmt).scalar()
        return internal_render_template(
            'zendesk-users-in-group.html',
            titulo='Groups',
            group_memberships=group_memberships,
            group_name=group_name,
            group_id=group_id,
        )
