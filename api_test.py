import requests
import base64
import json
from config import *


search = "type:ticket status:new"

zendesk_endpoint_url = "api/v2/search.json"
zendesk_search_query = "?query=type:ticket status:new"
api_url = API_BASE_URL + zendesk_endpoint_url + zendesk_search_query

# Autenticação
concatenate = USERNAME + "/token:" + ZENDESK_API_KEY

concatenate_bytes = concatenate.encode("ascii")
base64_bytes = base64.b64encode(concatenate_bytes)
base64_string = base64_bytes.decode("ascii")

# Montando Headers
headers = {"Authorization": "Basic " + base64_string}

# Enviando request e armazenando response em uma variável
response = requests.get(api_url, headers=headers).json()

# print(str(json.dumps(response, sort_keys=False, indent=4, ensure_ascii=False)))

result_str = str(response['results']) + ","
result_str = result_str[:-1]

print(type(result_str))

print("------------------")
print("Replacing required data...")
result = result_str.replace("'", '"')
result = result.replace("None", '"None"')
result = result.replace("False", '"False"')
result = result.replace("True", '"True"')

print("Replacing completed!")
print("------------------")
print("Data after replacement: " + result)
print("Data type after: " + str(type(result)))
print("------------------")

json = json.loads(result)
print(type(json))
