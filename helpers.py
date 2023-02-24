from config import *
import base64
from models import *


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
    user_default_group = ZendeskGroupMemberships.query.filter_by(zendesk_user_id=zendesk_user_id, default=1).first()

    return user_default_group


def generate_assign_tickets_json(zendesk_user_id):
    json = '[ { \
      "ticket": { \
        "status": "open", \
        "assignee_id": {}, \
        "group_id": {} \
      } \
    } ]'.format(zendesk_user_id, zendesk_default_user_group(zendesk_user_id))

    return json
