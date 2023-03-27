from helpers import *
from app import app
from models import *
from sqlalchemy import create_engine, select, insert
from sqlalchemy.orm import Session, sessionmaker
from flask import render_template, request, redirect, url_for, abort
import time

engine = create_engine(url_object)


@app.route('/routes/new')
def new_route():
    time.sleep(.35)

    form = RouteForm()

    stmt = select(ZendeskGroups.id, ZendeskGroups.name, func.group_concat(ZendeskUsers.name.distinct()).label('users')) \
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


@app.route('/routes/insert_new', methods=['POST', ])
def insert_new_route():
    if request.method == 'POST':
        data = request.get_json()

        with Session(engine) as session:
            new_route = Routes(
                name=data['route_name'],
                active=data['route_status'],
                deleted=False,
            )

            session.add(new_route)
            session.flush()

            if data['recipient_users'] and data['recipient_groups']:
                abort(422, 'Received both User and Group recipients, when only one is allowed')
            else:
                if data['recipient_users']:

                    new_route_recipient_type = RouteRecipientType(
                        routes_id=new_route.id,
                        recipient_type=0,
                    )
                    session.add(new_route_recipient_type)
                    session.flush()
                    for user in data['recipient_users']:
                        session.execute(
                            insert(RouteRecipientUsers), [
                                {'routes_id': new_route.id, 'zendesk_users_id': user}
                            ]
                        )
                        session.flush()
                else:
                    if data['recipient_groups']:
                        new_route_recipient_type = RouteRecipientType(
                            routes_id=new_route.id,
                            recipient_type=1,
                        )
                        session.add(new_route_recipient_type)
                        session.flush()

                        for group in data['recipient_groups']:
                            session.execute(
                                insert(RouteRecipientGroups), [
                                    {'routes_id': new_route.id, 'zendesk_groups_id': group}
                                ]
                            )
                            session.flush()
                    else:
                        abort(422, 'No recipient received, please select Users or Groups as recipients for the route')

            session.commit()

        return 'Data processed successfully'
