import base64
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, PasswordField
from config import *
import requests


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
    api_url = API_BASE_URL + zendesk_endpoint_url

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

    return str(api_response['user']['locale'])
