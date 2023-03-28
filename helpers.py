import base64
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from config import *
from models import *
from sqlalchemy import create_engine
import requests
from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, PasswordField, BooleanField

engine = create_engine(url_object)


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


def generate_assign_tickets_json(zendesk_user_id):
    try:
        json = \
            {
                "ticket": {
                    "status": "open",
                    "assignee_id": zendesk_user_id
                }
            }

        return json

    except NoResultFound:
        return 'Usuário não possui grupo padrão ou não está cadastrado!'

    except MultipleResultsFound:
        return 'Usuário possui mais de um registro de grupo padrão!'


def get_ticket_requester_locale(requester_id):
    zendesk_endpoint_url = f'/api/v2/users/{requester_id}'
    api_url = API_BASE_URL + zendesk_endpoint_url

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

    return str(api_response['user']['locale'])
