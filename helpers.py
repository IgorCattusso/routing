from config import *
import base64


def generate_zendesk_headers():
    concatenate = USERNAME + "/token:" + ZENDESK_API_KEY

    concatenate_bytes = concatenate.encode("ascii")
    base64_bytes = base64.b64encode(concatenate_bytes)
    base64_string = base64_bytes.decode("ascii")

    # Montando Headers
    headers = {"Authorization": "Basic " + base64_string}

    return headers
