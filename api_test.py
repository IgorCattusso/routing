import requests
import base64

# Base URL
api_url = "https://agilepromoter1671733243.zendesk.com/api/v2/tickets"

search = "type:ticket status:new"

# Autenticação
username = "igor.cattusso@involves.com"
api_key = "dcAxT2yYGwZWmPIkUJuwZotJdwFAgn3GxzLBajPE"

concatenate = username + "/token:" + api_key

concatenate_bytes = concatenate.encode("ascii")
base64_bytes = base64.b64encode(concatenate_bytes)
base64_string = base64_bytes.decode("ascii")

# Montando Headers
headers = {"Authorization": "Basic " + base64_string}

# Enviando request e armazenando response em uma variável
response = requests.get(api_url, headers=headers).json()

print(response)
