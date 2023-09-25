import os
from dotenv import load_dotenv
from sqlalchemy import URL
import datetime

load_dotenv()

SECRET_KEY = str(os.getenv('APP_SECRET_KEY'))
WTF_CSRF_TIME_LIMIT = 43200  # 12 hours
PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=12)

ZENDESK_BASE_URL = 'https://agilepromoter1671733243.zendesk.com/'

USERNAME = 'igor.cattusso@involves.com'

ZENDESK_API_KEY = str(os.getenv('ZENDESK_API_KEY'))

USER_PROFILE_PICTURE_UPLOAD_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/assets/users/'

url_object = URL.create(  # Creating connection string
    "mysql+pymysql",
    username=str(os.getenv('DATABASE_USER')),
    password=str(os.getenv('DATABASE_PASSWORD')),
    host="localhost",
    database="routing",
)

ZENDESK_TICKET_LEVEL_ID = 11490675185819  # Campo atendimento no Zendesk

EMAIL_SENDER = str(os.getenv('GMAIL_ACCOUNT_EMAIL'))
EMAIL_PASSWORD = str(os.getenv('GMAIL_APP_PASSWORD'))
