from flask import Flask
from sqlalchemy import create_engine
from config import url_object
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_pyfile('config.py')

login_manager = LoginManager()
login_manager.init_app(app)

engine = create_engine(url_object)

from views import *
from views_login import *
from views_routes import *
from views_settings import *
from views_users import *
from views_zendesk import *
from views_zendesk_groups import *
from views_zendesk_tickets import *
from views_zendesk_users import *
from routing import *

if __name__ == '__main__':
    app.run(debug=True)
