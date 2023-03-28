from helpers import *
from app import app
from models import *
from sqlalchemy import create_engine, select, insert, case, update, delete
from sqlalchemy.orm import Session, sessionmaker
from flask import render_template, request, redirect, url_for, abort
import time

engine = create_engine(url_object)


@app.route('/routes/new')
def new_route():
    time.sleep(.35)

    recipient_groups_stmt = select(
            ZendeskGroups.id,
            ZendeskGroups.name,
            func.group_concat(ZendeskUsers.name.distinct()).label('users')
        ) \
        .join(ZendeskGroupMemberships, ZendeskGroupMemberships.zendesk_groups_id == ZendeskGroups.id) \
        .join(ZendeskUsers, ZendeskGroupMemberships.zendesk_users_id == ZendeskUsers.id) \
        .group_by(ZendeskGroups.id, ZendeskGroups.name)

    recipient_users_stmt = select(
            ZendeskGroupMemberships.zendesk_users_id,
            ZendeskUsers.name
        ) \
        .join(ZendeskUsers, isouter=True) \
        .group_by(ZendeskGroupMemberships.zendesk_users_id, ZendeskUsers.name)

    tickets_locales_stmt = select(
            ZendeskLocales.id,
            ZendeskLocales.locale,
            ZendeskLocales.presentation_name
        )

    tickets_groups_stmt = select(
            ZendeskGroups.id,
            ZendeskGroups.name
        )\
        .order_by(ZendeskGroups.name)

    with Session(engine) as session:
        recipient_groups_list = session.execute(recipient_groups_stmt).all()
        recipient_users_list = session.execute(recipient_users_stmt).all()
        tickets_locales_list = session.execute(tickets_locales_stmt).all()
        tickets_groups_list = session.execute(tickets_groups_stmt).all()

    return render_template('routes-new.html',
                           titulo='Routing home',
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


@app.route('/routes/delete/<int:route_id>', methods=['DELETE'])
def deactivate_route(route_id):
    delete_route_stmt = update(Routes).where(Routes.id == route_id).values(deleted=1)
    with Session(engine) as session:
        session.execute(delete_route_stmt)
        session.commit()

    return 'Data processed successfully'


@app.route('/routes/deactivate/<int:route_id>', methods=['PUT'])
def delete_route(route_id):
    deactivate_route_stmt = update(Routes).where(Routes.id == route_id).values(active=0)
    with Session(engine) as session:
        session.execute(deactivate_route_stmt)
        session.commit()

    return 'Data processed successfully'


@app.route('/routes/edit/<int:route_id>')
def edit_route(route_id):
    all_recipient_groups_stmt = select(
            ZendeskGroups.id,
            ZendeskGroups.name,
            func.group_concat(ZendeskUsers.name.distinct()).label('users')
        ) \
        .join(ZendeskGroupMemberships, ZendeskGroupMemberships.zendesk_groups_id == ZendeskGroups.id) \
        .join(ZendeskUsers, ZendeskGroupMemberships.zendesk_users_id == ZendeskUsers.id) \
        .group_by(ZendeskGroups.id, ZendeskGroups.name)

    all_recipient_users_stmt = select(
            ZendeskGroupMemberships.zendesk_users_id,
            ZendeskUsers.name
        ) \
        .join(ZendeskUsers, isouter=True) \
        .group_by(ZendeskGroupMemberships.zendesk_users_id, ZendeskUsers.name)

    all_tickets_locales_stmt = select(
            ZendeskLocales.id,
            ZendeskLocales.locale,
            ZendeskLocales.presentation_name
        )

    all_tickets_groups_stmt = select(
            ZendeskGroups.id,
            ZendeskGroups.name
        ).order_by(ZendeskGroups.name)

    routes_stmt = select(
            Routes.id,
            Routes.name,
            Routes.active
        ).where(Routes.id == route_id)

    route_recipient_type_stmt = select(RouteRecipientType.recipient_type) \
                               .where(RouteRecipientType.routes_id == route_id)

    route_recipient_users_stmt = select(RouteRecipientUsers.zendesk_users_id)\
                                .where(RouteRecipientUsers.routes_id == route_id)

    route_recipients_groups_stmt = select(RouteRecipientGroups.zendesk_groups_id)\
                                  .where(RouteRecipientGroups.routes_id == route_id)

    with Session(engine) as session:
        all_recipient_groups_list = session.execute(all_recipient_groups_stmt).all()
        all_recipient_users_list = session.execute(all_recipient_users_stmt).all()
        all_tickets_locales_list = session.execute(all_tickets_locales_stmt).all()
        all_tickets_groups_list = session.execute(all_tickets_groups_stmt).all()
        routes = session.execute(routes_stmt).first()
        route_recipient_type = session.execute(route_recipient_type_stmt).scalar()
        selected_route_recipient_users = session.execute(route_recipient_users_stmt).all()
        selected_route_recipient_groups = session.execute(route_recipients_groups_stmt).all()

    selected_route_recipient_users_list = []
    for users in selected_route_recipient_users:
        for user in users:
            selected_route_recipient_users_list.append(user)

    selected_route_recipient_groups_list = []
    for groups in selected_route_recipient_groups:
        for group in groups:
            selected_route_recipient_groups_list.append(group)

    time.sleep(.35)

    return render_template(
        'routes-edit.html',
        route_id=route_id,
        all_recipient_groups=all_recipient_groups_list,
        all_recipient_users=all_recipient_users_list,
        all_tickets_locales=all_tickets_locales_list,
        all_tickets_groups=all_tickets_groups_list,
        route_name=routes.name,
        route_status=routes.active,
        selected_route_recipient_type=route_recipient_type,
        selected_route_recuipient_users=selected_route_recipient_users_list,
        selected_route_recipient_groups=selected_route_recipient_groups_list,
    )


@app.route('/routes/update-existing-route/<int:route_id>', methods=['PUT', ])
def update_existing_route(route_id):
    if request.method == 'PUT':
        data = request.get_json()

        with Session(engine) as session:
            update_routes_stmt = (
                update(Routes)
                .where(Routes.id == route_id)
                .values(name=data['route_name'], active=data['route_status'])
            )
            session.execute(update_routes_stmt)

            if data['recipient_users'] and data['recipient_groups']:
                abort(422, 'Received both User and Group recipients, when only one is allowed')
            else:
                delete_recipient_users_stmt = (
                    delete(RouteRecipientUsers).where(RouteRecipientUsers.routes_id == route_id)
                )
                delete_recipient_groups_stmt = (
                    delete(RouteRecipientGroups).where(RouteRecipientGroups.routes_id == route_id)
                )
                delete_recipient_type_stmt = (
                    delete(RouteRecipientType).where(RouteRecipientType.routes_id == route_id)
                )

                session.execute(delete_recipient_users_stmt)
                session.flush()
                session.execute(delete_recipient_groups_stmt)
                session.flush()
                session.execute(delete_recipient_type_stmt)
                session.flush()

                if data['recipient_users']:
                    new_route_recipient_type = RouteRecipientType(
                        routes_id=route_id,
                        recipient_type=0,
                    )
                    session.add(new_route_recipient_type)
                    session.flush()
                    for user in data['recipient_users']:
                        session.execute(
                            insert(RouteRecipientUsers), [
                                {'routes_id': route_id, 'zendesk_users_id': user}
                            ]
                        )
                        session.flush()
                else:
                    if data['recipient_groups']:
                        new_route_recipient_type = RouteRecipientType(
                            routes_id=route_id,
                            recipient_type=1,
                        )
                        session.add(new_route_recipient_type)
                        session.flush()

                        for group in data['recipient_groups']:
                            session.execute(
                                insert(RouteRecipientGroups), [
                                    {'routes_id': route_id, 'zendesk_groups_id': group}
                                ]
                            )
                            session.flush()
                    else:
                        abort(422, 'No recipient received, please select Users or Groups as recipients for the route')

            session.commit()

        return 'Data processed successfully'
