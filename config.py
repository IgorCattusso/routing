API_BASE_URL = "https://agilepromoter1671733243.zendesk.com/"

USERNAME = "igor.cattusso@involves.com"

ZENDESK_API_KEY = "dcAxT2yYGwZWmPIkUJuwZotJdwFAgn3GxzLBajPE"

SQLALCHEMY_DATABASE_URI = \
    '{SGBD}://{user}:{password}@{server}/{database}'.format(
        SGBD='mysql+mysqlconnector',
        user='igor',
        password='igor',
        server='localhost',
        database='jogoteca'
    )  # configurando conexão com o banco de dados