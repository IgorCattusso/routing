from config import ZENDESK_BASE_URL
import requests
from helpers import generate_zendesk_headers
from models import ZendeskViews, Notifications
from app import app, engine
from sqlalchemy.orm import Session
from flask import redirect, url_for, session
import time
from flask_login import login_required


@app.route('/get-zendesk-views')
@login_required
def get_zendesk_views():
    zendesk_endpoint_url = '/api/v2/views.json?page=1'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    modified_views = False
    views_in_api_response = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

    next_url = api_url

    while next_url:
        for view in api_response['views']:
            views_in_api_response.append(view['id'])
            with Session(engine) as db_session:
                existing_view = ZendeskViews.get_view_by_zendesk_id(db_session, view['id'])
                if not existing_view:
                    new_view = ZendeskViews(
                        zendesk_view_id=view['id'],
                        name=view['title'],
                        active=view['active'],
                        deleted=False,
                    )
                    ZendeskViews.insert_new_view(db_session, new_view)
                    modified_views = True
                    db_session.commit()
                elif existing_view.name != view['title'] and existing_view.active != view['active']:
                    ZendeskViews.update_view(db_session, existing_view.id, view['title'], view['active'], False)
                    modified_views = True
                    db_session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    with Session(engine) as db_session:
        for view in ZendeskViews.get_views(db_session):
            if view.zendesk_view_id not in views_in_api_response:
                ZendeskViews.delete_view(db_session, view.id)
                modified_views = True
                db_session.commit()

    if modified_views:
        notification_content = 'Novas views inseridas ou alteradas!'
    else:
        notification_content = 'Não há novas views para inserir ou alterar!'

    user_id = session['_user_id']

    with Session(engine) as db_session:
        Notifications.create_notification(
            db_session,
            user_id,
            1,
            notification_content,
        )
        db_session.commit()

    return redirect(url_for('views'))
