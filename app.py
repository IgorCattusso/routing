from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine


app = Flask(__name__)
app.config.from_pyfile('config.py')

from views import *
from views_users import *
from views_groups import *
from views_tickets import *

engine = create_engine(url_object)

if __name__ == '__main__':
    app.run(debug=True)
