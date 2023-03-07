import os
from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()

API_BASE_URL = 'https://agilepromoter1671733243.zendesk.com/'

USERNAME = 'igor.cattusso@involves.com'

ZENDESK_API_KEY = str(os.getenv('SECRET_KEY'))

SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{user}:{password}@{server}/{database}'.format(
        SGBD='mysql+mysqlconnector',
        user=str(os.getenv('DATABASE_USER')),
        password=str(os.getenv('DATABASE_PASSWORD')),
        server='localhost',
        database='routing'
    )  # configurando conexão com o banco de dados

ZENDESK_GROUP_IDS = [11490525550747]

url_object = URL.create(  # Creating connection string
    "mysql+pymysql",
    username="igor",
    password="igor",
    host="localhost",
    database="routing",
)
