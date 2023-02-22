import requests
import json
import base64

# Base URL
api_url = "https://sup.involves.com/webservices/api/v1/88/pointofsale"

# Autenticação
username = "one.above.all"
password = "123456"
concatenate = username + ":" + password
concatenate_bytes = concatenate.encode("ascii")
base64_bytes = base64.b64encode(concatenate_bytes)
base64_string = base64_bytes.decode("ascii")

# Montando Headers
headers =  {"Content-Type":"application/json", "Authorization":"Basic " + base64_string, "X-AGILE-CLIENT":"EXTERNAL_APP"}

# Enviando request e armazenando response em uma variável
response = requests.get(api_url, headers=headers)

# Imprimindo response
print(response.json())
