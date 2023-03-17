from helpers import *
from config import *
from app import app
from models import *
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import Session
from flask import render_template

engine = create_engine(url_object)


@app.route('/')
def home():
    return render_template('home.html', titulo='Routing home')


@app.route('/settings')
def configuration():
    return render_template('settings.html', titulo='Routing home')


@app.route('/users')
def users():
    stmt = select(ZendeskUsers).order_by(ZendeskUsers.name)
    with Session(engine) as session:
        user_list = session.execute(stmt).all()
    return render_template('users.html', titulo='Users', users=user_list)


@app.route('/groups')
def groups():
    stmt = select(ZendeskGroups.id, ZendeskGroups.zendesk_group_id, ZendeskGroups.name,
                  func.count(ZendeskGroupMemberships.zendesk_users_id).label('count')) \
        .join(ZendeskGroupMemberships, isouter=True) \
        .group_by(ZendeskGroups.id, ZendeskGroups.name) \
        .order_by(desc('count'))
    with Session(engine) as session:
        group_list = session.execute(stmt).all()
    return render_template('groups.html', titulo='Groups', groups=group_list)


@app.route('/reports')
def reports():
    return render_template('reports.html', titulo='Routing home')
