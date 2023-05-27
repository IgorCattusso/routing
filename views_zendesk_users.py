from config import ZENDESK_BASE_URL
import requests
from helpers import generate_zendesk_headers, match_false_true
from models import ZendeskUsers, Notifications
from app import app, engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from flask import redirect, url_for, session
import time
from flask_login import login_required


@app.route('/get-zendesk-users')
@login_required
def get_zendesk_users():
    zendesk_endpoint_url = 'api/v2/search.json?page=1'
    zendesk_search_query = 'query=type:user routing_user:true'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url + '&' + zendesk_search_query

    inserted_users = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for user in api_response['results']:
            stmt = select(ZendeskUsers).where(ZendeskUsers.zendesk_user_id == user['id'])
            with Session(engine) as db_session:
                query_result = db_session.execute(stmt).first()
                if not query_result:
                    new_user = ZendeskUsers(zendesk_user_id=user['id'],
                                            name=user['name'],
                                            email=user['email'],
                                            suspended=match_false_true(user['suspended']),
                                            )
                    inserted_users.append(user['name'])
                    db_session.add(new_user)
                    db_session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    if inserted_users:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                f'Usuários inseridos: {inserted_users}',
            )
            db_session.commit()
        return redirect(url_for('zendesk_users'))
    else:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                f'Não há novos usuários para inserir ou alterar!',
            )
            db_session.commit()
        return redirect(url_for('zendesk_users'))
