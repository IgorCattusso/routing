import requests
import base64
from config import *
from models import *
from helpers import *


'''
zendesk_endpoint_url = 'api/v2/search.json'
zendesk_search_query = 'query=type:ticket status:new'
api_url = API_BASE_URL + zendesk_endpoint_url + "?" + zendesk_search_query

# Autenticação
concatenate = USERNAME + '/token:' + ZENDESK_API_KEY

concatenate_bytes = concatenate.encode('ascii')
base64_bytes = base64.b64encode(concatenate_bytes)
base64_string = base64_bytes.decode('ascii')

# Montando Headers
headers = {'Authorization': 'Basic ' + base64_string}

# Enviando request e armazenando response em uma variável
api_response = requests.get(api_url, headers=headers).json()

# print(str(json.dumps(response, sort_keys=False, indent=4, ensure_ascii=False)))

print(api_response)
print(type(api_response))

results = api_response['results']
print(results)
print(type(results))

created_at_formatted = results[1]['created_at'].replace('T', ' ').replace('Z', '')
print(created_at_formatted)
'''


'''
api_response_as_str = str(api_response['results']) + ","
api_response_as_str = api_response_as_str[:-1]

print(type(api_response_as_str))

print("------------------")
print("Replacing required data...")
result = api_response_as_str.replace("'", '"')
result = result.replace("None", '"None"')
result = result.replace("False", '"False"')
result = result.replace("True", '"True"')

print("Replacing completed!")
print("------------------")
print("Data after replacement: " + result)
print("------------------")
'''

'''
zendesk_default_user_group(11490525550747)
'''
#
# zendesk_endpoint_url = '/api/v2/group_memberships'
# api_url = API_BASE_URL + zendesk_endpoint_url
#
# api_response = requests.get(api_url, headers=generate_zendesk_headers())
#
# data = api_response.json()
#
# results = data['group_memberships']
#
# inserted_users_and_groups = []
#
# for user in results:
#     test = match_false_true(user['default'])
#     print(type(user['default']))

#get_zendesk_users_id('11490525550747')

stmt = select(ZendeskUsers.id).where(ZendeskUsers.zendesk_user_id == 'null')
print(str(stmt))
with Session(engine) as session:
    db_user_id = session.execute(stmt)
    a = db_user_id.first()
    print(a[0])
