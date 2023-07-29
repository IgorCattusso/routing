import base64
from flask import render_template, session, redirect, url_for
from config import *
import requests
from models import Users, Notifications
from sqlalchemy.orm import Session
from app import engine, app
from config import ZENDESK_BASE_URL
from flask_login import logout_user
import re
import json


def generate_zendesk_headers():
    concatenate = USERNAME + '/token:' + ZENDESK_API_KEY

    concatenate_bytes = concatenate.encode('ascii')
    base64_bytes = base64.b64encode(concatenate_bytes)
    base64_string = base64_bytes.decode('ascii')

    # Montando Headers
    headers = {'Authorization': 'Basic ' + base64_string}

    return headers


def match_false_true(value):
    match value:
        case False:
            return 0
        case True:
            return 1
        case _:
            return 0


def get_ticket_requester_locale(requester_id):
    zendesk_endpoint_url = f'/api/v2/users/{requester_id}'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

    return str(api_response['users']['locale'])


def get_user_profile_picture(user_id):
    profile_picture = '/static/assets/users/placeholder.png'

    for file_name in os.listdir(app.config['USER_PROFILE_PICTURE_UPLOAD_PATH']):
        if f'{user_id}-' in file_name:
            profile_picture = f'/static/assets/users/{file_name}'

    return profile_picture


def internal_render_template(template, **kwargs):
    if '_user_id' not in session:
        session['_user_id'] = 0

    if session:
        if session['_user_id']:
            with Session(engine) as db_session:
                user = Users.get_user(db_session, session['_user_id'])
                unread_notifications_count = Notifications.count_user_unread_notifications(db_session, session['_user_id'])
                user_notifications = Notifications.get_user_last_hundred_notifications(db_session, session['_user_id'])

            kwargs['routing_status'] = user.routing_status
            kwargs['authenticated'] = user.authenticated
            kwargs['user_id'] = user.id
            kwargs['user_name'] = user.name
            kwargs['unread_notifications_count'] = unread_notifications_count
            kwargs['user_notifications'] = user_notifications

            profile_picture = get_user_profile_picture(session['_user_id'])

            # Redirects the user to the login page in case they have been inactivated, deleted or logged out
            if not user.active or not user.authenticated or user.deleted:
                logout_user()
                return redirect(url_for('login'))

            return render_template(template, kwargs=kwargs, profile_picture=profile_picture)

    return render_template(template, kwargs=kwargs)


def fix_double_quotes_in_subject(request_json):
    """
    :param request_json:

    Receives a json that has double quotes on the ticket_subject's value
    Returns the same json with the double quotes replaced by single quotes
    """
    sanitized_string = repr(request_json.decode('utf-8')).replace(r'\n', '').replace(r'\r', '').replace('    ', '')

    start_index = sanitized_string.find('"ticket_subject": "') + len('"ticket_subject": "')
    end_index = sanitized_string.find('"ticket_channel":')
    new_ticket_subject = sanitized_string[start_index:end_index][:-2].replace('"', "'") + '",'

    fixed_string = sanitized_string[:start_index] + new_ticket_subject + sanitized_string[end_index:]
    fixed_json = json.loads(fixed_string[1:-1])

    print(f'aaa: {fixed_json}')

    return fixed_json
