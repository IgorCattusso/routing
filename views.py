from helpers import *
from config import *
from app import app
from models import *
from sqlalchemy import create_engine, select, desc, case
from sqlalchemy.orm import Session
from flask import render_template
import time

engine = create_engine(url_object)


@app.route('/')
def home():
    time.sleep(.35)
    return render_template('home.html', titulo='Routing home')


@app.route('/settings')
def configuration():
    time.sleep(.35)
    return render_template('settings.html', titulo='Routing home')


@app.route('/users')
def users():
    stmt = select(ZendeskUsers).order_by(ZendeskUsers.name)
    with Session(engine) as session:
        user_list = session.execute(stmt).all()

    time.sleep(.35)
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

    time.sleep(.35)
    return render_template('groups.html', titulo='Groups', groups=group_list)


@app.route('/reports')
def reports():
    time.sleep(.35)
    return render_template('reports.html', titulo='Routing home')


@app.route('/locales')
def locales():
    stmt = select(ZendeskLocales.id, ZendeskLocales.zendesk_locale_id, ZendeskLocales.locale, ZendeskLocales.name,
                  case(
                      (ZendeskLocales.default == 1, 'Sim'),
                      (ZendeskLocales.default == 0, 'Não'),
                      else_='')
                  .label('default'))
    with Session(engine) as session:
        zendesk_locales = session.execute(stmt).all()

    time.sleep(.35)
    return render_template('locales.html', titulo='Routing home', locales=zendesk_locales)


@app.route('/routes')
def routes():
    stmt = select(Routes.id, Routes.name,
                  case(
                      (Routes.active == 1, 'Sim'),
                      (Routes.active == 0, 'Não'),
                      else_='')
                  .label('active')) \
                  .where(Routes.deleted == 0)
    with Session(engine) as session:
        app_routes = session.execute(stmt).all()

    time.sleep(.35)
    return render_template('routes.html', titulo='Routing home', routes=app_routes)
