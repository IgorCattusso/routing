from sqlalchemy import *
from config import *
import base64
from models import *
from app import db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound



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


def zendesk_default_user_group(zendesk_user_id):
    result = db.session.execute(select(ZendeskGroupMemberships.group_id).filter_by(
        zendesk_user_id=zendesk_user_id, default=1)).scalar_one()

    return result


def generate_assign_tickets_json(zendesk_user_id):
    try:
        json = \
            {
                "ticket": {
                    "status": "open",
                    "assignee_id": zendesk_user_id,
                    "group_id": zendesk_default_user_group(zendesk_user_id)
                }
            }

        return json

    except NoResultFound:
        return 'Usuário não possui grupo padrão!'

    except MultipleResultsFound:
        return 'Usuário possui mais de um registro de grupo padrão!'
