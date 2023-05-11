import base64
from flask_wtf import FlaskForm
from flask import render_template, session
from wtforms import validators, StringField, SubmitField, PasswordField
from config import *
import requests
from models import Users, Notifications
from sqlalchemy.orm import Session
from app import engine


class UserForm(FlaskForm):
    email = StringField(
        'E-mail',
        [validators.DataRequired(),
         validators.Length(min=1, max=150)],
        render_kw={"placeholder": "E-mail"}
    )
    password = PasswordField(
        'Senha',
        [validators.DataRequired(),
         validators.Length(min=1, max=150)],
        render_kw={"placeholder": "Senha"}
    )
    submit = SubmitField('LOGIN')


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

    return str(api_response['user']['locale'])


def internal_render_template(template, **kwargs):

    if session:
        if session['_user_id']:
            with Session(engine) as db_session:
                user = Users.get_user(db_session, session['_user_id'])
                notification_count = Notifications.count_user_unread_notifications(db_session, session['_user_id'])
                user_notifications = Notifications.get_user_last_hundred_notifications(db_session, session['_user_id'])

            kwargs['routing_status'] = user.routing_status
            kwargs['authenticated'] = user.authenticated
            kwargs['user_id'] = user.id
            kwargs['notification_count'] = notification_count
            kwargs['user_notifications'] = user_notifications

    return render_template(template, kwargs=kwargs)
