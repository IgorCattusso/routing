from helpers import *
from config import *
from app import app
from models import *
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from flask import render_template
import time

engine = create_engine(url_object)


@app.route('/routes/new')
def new_route():
    time.sleep(.35)

    form = RouteForm()

    stmt = select(ZendeskGroups.id, ZendeskGroups.name, func.group_concat(ZendeskUsers.name.distinct()).label('users'))\
          .join(ZendeskGroupMemberships, ZendeskGroupMemberships.zendesk_groups_id == ZendeskGroups.id) \
          .join(ZendeskUsers, ZendeskGroupMemberships.zendesk_users_id == ZendeskUsers.id) \
          .group_by(ZendeskGroups.id, ZendeskGroups.name)
    with Session(engine) as session:
        recipient_groups_list = session.execute(stmt).all()

    stmt = select(ZendeskGroupMemberships.zendesk_users_id, ZendeskUsers.name) \
          .join(ZendeskUsers, isouter=True) \
          .group_by(ZendeskGroupMemberships.zendesk_users_id, ZendeskUsers.name)
    with Session(engine) as session:
        recipient_users_list = session.execute(stmt).all()

    stmt = select(ZendeskLocales.id, ZendeskLocales.locale, ZendeskLocales.presentation_name)
    with Session(engine) as session:
        tickets_locales_list = session.execute(stmt).all()

    stmt = select(ZendeskGroups.id, ZendeskGroups.name).order_by(ZendeskGroups.name)

    with Session(engine) as session:
        tickets_groups_list = session.execute(stmt).all()


    return render_template('routes-new.html',
                           titulo='Routing home',
                           form=form,
                           recipient_groups=recipient_groups_list,
                           recipient_users=recipient_users_list,
                           tickets_locales=tickets_locales_list,
                           tickets_groups=tickets_groups_list,
                           )
