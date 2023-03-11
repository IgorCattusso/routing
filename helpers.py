import base64
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from config import *
from models import *
from sqlalchemy import create_engine

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


class CustomFields:
    def __init__(self, field_id, value):
        self.field_id = field_id
        self.value = value
