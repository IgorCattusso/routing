import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = str(os.getenv('SECRET_KEY'))

API_BASE_URL = "https://agilepromoter1671733243.zendesk.com/"

USERNAME = "igor.cattusso@involves.com"

ZENDESK_API_KEY = SECRET_KEY

SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{user}:{password}@{server}/{database}'.format(
        SGBD='mysql+mysqlconnector',
        user=str(os.getenv('DATABASE_USER')),
        password=str(os.getenv('DATABASE_PASSWORD')),
        server='localhost',
        database='routing'
    )  # configurando conexão com o banco de dados
