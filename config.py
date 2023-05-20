import os
from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()

SECRET_KEY = str(os.getenv('APP_SECRET_KEY'))

ZENDESK_BASE_URL = 'https://agilepromoter1671733243.zendesk.com/'

USERNAME = 'igor.cattusso@involves.com'

ZENDESK_API_KEY = str(os.getenv('ZENDESK_API_KEY'))

USER_PROFILE_PICTURE_UPLOAD_PATH = os.path.dirname(os.path.abspath(__file__)) + '/static/assets/users/'

SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{user}:{password}@{server}/{database}'.format(
        SGBD='mysql+mysqlconnector',
        user=str(os.getenv('DATABASE_USER')),
        password=str(os.getenv('DATABASE_PASSWORD')),
        server='localhost',
        database='routing'
    )  # configurando conexão com o banco de dados

url_object = URL.create(  # Creating connection string
    "mysql+pymysql",
    username="igor",
    password="igor",
    host="localhost",
    database="routing",
)

ZENDESK_TICKET_LEVEL_ID = 11490675185819  # Campo atendimento no Zendesk

EMAIL_SENDER = str(os.getenv('GMAIL_ACCOUNT_EMAIL'))
EMAIL_PASSWORD = str(os.getenv('GMAIL_APP_PASSWORD'))

