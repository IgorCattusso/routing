from config import *
import base64
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import requests


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


def get_pages_urls(api_url):

    url_list = []

    zendesk_search_query = 'page=1'

    url = api_url + '?' + zendesk_search_query
    url_list.append(url)

    api_response = requests.get(url, headers=generate_zendesk_headers()).json()
    next_url = api_response['next_page']
    url_list.append(next_url)

    while next_url is not None:
        new_api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()
        next_url = new_api_response['next_page']
        url_list.append(next_url)

    url_list.pop(-1)

    return url_list
