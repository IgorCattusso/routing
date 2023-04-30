from app import app, engine
from models import ZendeskGroups, ZendeskGroupMemberships, ZendeskUsers, ZendeskLocales, ZendeskTicketForms, ZendeskTags, ZendeskTicketFields, ZendeskTicketFieldsInForms, Routes, RouteRecipientType, RouteRecipientUsers, RouteRecipientGroups, RouteTicketTags, RouteTicketLocales, RouteTicketGroups
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.orm import Session
from flask import render_template, request, abort
import time
from helpers import internal_render_template


@app.route('/routes/new')
def new_route():
    recipient_groups_stmt = select(
        ZendeskGroups.id,
        ZendeskGroups.name,
        func.group_concat(ZendeskUsers.name.distinct()).label('users'),
    ) \
        .join(ZendeskGroupMemberships, ZendeskGroupMemberships.zendesk_groups_id == ZendeskGroups.id) \
        .join(ZendeskUsers, ZendeskGroupMemberships.zendesk_users_id == ZendeskUsers.id) \
        .group_by(ZendeskGroups.id, ZendeskGroups.name)

    recipient_users_stmt = select(
        ZendeskGroupMemberships.zendesk_users_id,
        ZendeskUsers.name,
    ) \
        .join(ZendeskUsers, isouter=True) \
        .group_by(ZendeskGroupMemberships.zendesk_users_id, ZendeskUsers.name)

    ticket_locales_stmt = select(
        ZendeskLocales.id,
        ZendeskLocales.locale,
        ZendeskLocales.presentation_name,
    )

    ticket_groups_stmt = select(
        ZendeskGroups.id,
        ZendeskGroups.name,
    ).order_by(ZendeskGroups.name)

    ticket_forms_stmt = select(
        ZendeskTicketForms.id,
        ZendeskTicketForms.name,
    ).order_by(ZendeskTicketForms.default.desc(), ZendeskTicketForms.name)

    ticket_tags_stmt = select(
        ZendeskTags.id,
        ZendeskTags.tag,
    ).order_by(ZendeskTags.tag)

    ticket_fields_in_forms = select(
        ZendeskTicketFieldsInForms.id,
        ZendeskTicketFieldsInForms.zendesk_ticket_forms_id,
        ZendeskTicketFieldsInForms.zendesk_ticket_fields_id,
        ZendeskTicketFields.title,
    ).join(ZendeskTicketFields)

    with Session(engine) as session:
        recipient_groups_list = session.execute(recipient_groups_stmt).all()
        recipient_users_list = session.execute(recipient_users_stmt).all()
        ticket_locales_list = session.execute(ticket_locales_stmt).all()
        ticket_groups_list = session.execute(ticket_groups_stmt).all()
        ticket_forms_list = session.execute(ticket_forms_stmt).all()
        ticket_tags_list = session.execute(ticket_tags_stmt).all()
        ticket_fields_in_forms_list = session.execute(ticket_fields_in_forms).all()

    time.sleep(.35)

    return internal_render_template(
        'routes-new.html',
        titulo='Routing home',
        recipient_groups=recipient_groups_list,
        recipient_users=recipient_users_list,
        ticket_locales=ticket_locales_list,
        ticket_groups=ticket_groups_list,
        ticket_forms=ticket_forms_list,
        ticket_tags=ticket_tags_list,
        ticket_fields=ticket_fields_in_forms_list,
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
                        abort(422, 'No recipient received, please select User or Groups as recipients for the route')

            for tag in data['ticket_tags']:
                session.execute(
                    insert(RouteTicketTags), [
                        {'routes_id': new_route.id, 'zendesk_tags_id': tag}
                    ]
                )
                session.flush()

            for locale in data['ticket_locales']:
                session.execute(
                    insert(RouteTicketLocales), [
                        {'routes_id': new_route.id, 'zendesk_locales_id': locale}
                    ]
                )
                session.flush()

            if data['ticket_groups']:
                RouteTicketGroups.insert_list_of_groups(session, new_route.id, data['ticket_groups'])
                session.flush()

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
    routes_stmt = select(
        Routes.id,
        Routes.name,
        Routes.active
    ).where(Routes.id == route_id)

    all_recipient_users_stmt = select(
        ZendeskGroupMemberships.zendesk_users_id,
        ZendeskUsers.name
    ) \
        .join(ZendeskUsers, isouter=True) \
        .group_by(ZendeskGroupMemberships.zendesk_users_id, ZendeskUsers.name)

    all_recipient_groups_stmt = select(
        ZendeskGroups.id,
        ZendeskGroups.name,
        func.group_concat(ZendeskUsers.name.distinct()).label('users')
    ) \
        .join(ZendeskGroupMemberships, ZendeskGroupMemberships.zendesk_groups_id == ZendeskGroups.id) \
        .join(ZendeskUsers, ZendeskGroupMemberships.zendesk_users_id == ZendeskUsers.id) \
        .group_by(ZendeskGroups.id, ZendeskGroups.name)

    all_tickets_locales_stmt = select(
        ZendeskLocales.id,
        ZendeskLocales.locale,
        ZendeskLocales.presentation_name
    )

    all_tickets_groups_stmt = select(
        ZendeskGroups.id,
        ZendeskGroups.name
    ).order_by(ZendeskGroups.name)

    all_tickets_tags_stmt = select(
        ZendeskTags.id,
        ZendeskTags.tag
    ).order_by(ZendeskTags.tag)

    route_recipient_type_stmt = select(RouteRecipientType.recipient_type) \
        .where(RouteRecipientType.routes_id == route_id)

    route_recipient_users_stmt = select(RouteRecipientUsers.zendesk_users_id) \
        .where(RouteRecipientUsers.routes_id == route_id)

    route_recipients_groups_stmt = select(RouteRecipientGroups.zendesk_groups_id) \
        .where(RouteRecipientGroups.routes_id == route_id)

    route_ticket_locales_stmt = select(RouteTicketLocales.zendesk_locales_id) \
        .where(RouteTicketLocales.routes_id == route_id)

    route_ticket_groups_stmt = select(RouteTicketGroups.zendesk_groups_id) \
        .where(RouteTicketGroups.routes_id == route_id)

    route_ticket_tags_stmt = select(RouteTicketTags.zendesk_tags_id) \
        .where(RouteTicketTags.routes_id == route_id)

    with Session(engine) as session:
        with session.begin():
            all_recipient_groups_list = session.execute(all_recipient_groups_stmt).all()
            all_recipient_users_list = session.execute(all_recipient_users_stmt).all()
            all_tickets_locales_list = session.execute(all_tickets_locales_stmt).all()
            all_tickets_groups_list = session.execute(all_tickets_groups_stmt).all()
            all_tickets_tags_list = session.execute(all_tickets_tags_stmt).all()
            routes = session.execute(routes_stmt).first()
            route_recipient_type = session.execute(route_recipient_type_stmt).scalar()
            selected_route_recipient_users = session.execute(route_recipient_users_stmt).all()
            selected_route_recipient_groups = session.execute(route_recipients_groups_stmt).all()
            selected_route_ticket_locales = session.execute(route_ticket_locales_stmt).all()
            selected_route_ticket_groups = session.execute(route_ticket_groups_stmt).all()
            selected_route_ticket_tags = session.execute(route_ticket_tags_stmt).all()

    selected_route_recipient_users_list = []
    for users in selected_route_recipient_users:
        for user in users:
            selected_route_recipient_users_list.append(user)

    selected_route_recipient_groups_list = []
    for groups in selected_route_recipient_groups:
        for group in groups:
            selected_route_recipient_groups_list.append(group)

    selected_route_ticket_locales_list = []
    for locales in selected_route_ticket_locales:
        for locale in locales:
            selected_route_ticket_locales_list.append(locale)

    selected_route_ticket_groups_list = []
    for ticket_groups in selected_route_ticket_groups:
        for ticket_group in ticket_groups:
            selected_route_ticket_groups_list.append(ticket_group)

    selected_route_ticket_tags_list = []
    for tags in selected_route_ticket_tags:
        for tag in tags:
            selected_route_ticket_tags_list.append(tag)

    time.sleep(.35)

    return internal_render_template(
        'routes-edit.html',
        route_id=route_id,
        all_recipient_groups=all_recipient_groups_list,
        all_recipient_users=all_recipient_users_list,
        all_tickets_locales=all_tickets_locales_list,
        all_tickets_groups=all_tickets_groups_list,
        all_tickets_tags=all_tickets_tags_list,
        route_name=routes.name,
        route_status=routes.active,
        selected_route_recipient_type=route_recipient_type,
        selected_route_recipient_users=selected_route_recipient_users_list,
        selected_route_recipient_groups=selected_route_recipient_groups_list,
        selected_route_ticket_locales=selected_route_ticket_locales_list,
        selected_route_ticket_groups=selected_route_ticket_groups_list,
        selected_route_ticket_tags=selected_route_ticket_tags_list,
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
            session.commit()

        if data['recipient_users'] and data['recipient_groups']:
            abort(422, 'Received both User and Group recipients, when only one is allowed')
        else:
            if data['recipient_users']:
                # Create an object with the info from POST
                route_recipient_type = RouteRecipientType(
                    routes_id=route_id,
                    recipient_type=0,
                )

                with Session(engine) as session:
                    # Check if the Recipient Type received in the POST already exists in the database
                    route_recipient_type_group_exists = session.execute(
                        select(RouteRecipientType)
                        .where(RouteRecipientType.routes_id == route_recipient_type.routes_id)
                        .where(RouteRecipientType.recipient_type == route_recipient_type.recipient_type)
                    ).scalar()

                    # If it does not exist, then it must be a different recipient_type because this is the edit route,
                    # so update the type from group (1) to user (0)
                    if not route_recipient_type_group_exists:
                        session.execute(update(RouteRecipientType)
                                        .where(RouteRecipientType.routes_id == route_recipient_type.routes_id)
                                        .values(recipient_type=0)
                                        )

                    # Delete any Recipient Groups bound to the Route, because,
                    # as of this point, we know it was saved with User instead
                    session.execute(delete(RouteRecipientGroups).where(RouteRecipientGroups.routes_id == route_id))

                    # If by any chance there's no record on the route_recipient_type table, insert it
                    route_recipient_type_exists = session.execute(
                        select(RouteRecipientType)
                        .where(RouteRecipientType.routes_id == route_recipient_type.routes_id)
                    ).first()
                    if not route_recipient_type_exists:
                        session.add(route_recipient_type)

                    session.commit()

                with Session(engine) as session:
                    # List of users received on the POST
                    # Check if each user already exists on the table
                    for user in data['recipient_users']:
                        existing_recipient_user = session.execute(
                            select(RouteRecipientUsers)
                            .where(RouteRecipientUsers.routes_id == route_id)
                            .where(RouteRecipientUsers.zendesk_users_id == user)
                        ).first()
                        if not existing_recipient_user:  # If it does not, insert it
                            new_user_recipient = RouteRecipientUsers(
                                routes_id=route_id,
                                zendesk_users_id=user
                            )
                            session.add(new_user_recipient)
                            session.flush()

                    # Make a list of all users received to be able to delete the ones which were not received
                    list_of_received_recipient_users = [user for user in data['recipient_users']]
                    list_of_received_recipient_users_as_str = []  # Make the list into ints because they came between ""
                    for user in list_of_received_recipient_users:
                        list_of_received_recipient_users_as_str.append(int(user))

                    # Get the users that were already on the database
                    recipient_users_in_database = session.execute(
                        select(RouteRecipientUsers.zendesk_users_id)
                        .where(RouteRecipientUsers.routes_id == route_id)
                    ).all()
                    list_of_recipient_users_in_database = []  # Make a list out of them
                    for user in recipient_users_in_database:
                        list_of_recipient_users_in_database.append(user[0])

                    # Subtract one list from another
                    recipient_users_to_be_deleted = \
                        list(set(list_of_recipient_users_in_database) - set(list_of_received_recipient_users_as_str))
                    session.execute(delete(RouteRecipientUsers)  # And delete the resulting list
                                    .where(RouteRecipientUsers.zendesk_users_id.in_(recipient_users_to_be_deleted))
                                    )

                    session.commit()

            else:
                with Session(engine) as session:
                    if data['recipient_groups']:
                        # Create an object with the info from POST
                        route_recipient_type = RouteRecipientType(
                            routes_id=route_id,
                            recipient_type=1,
                        )

                        # Check if the Recipient Type received in the POST already exists in the database
                        route_recipient_type_group_exists = session.execute(
                            select(RouteRecipientType)
                            .where(RouteRecipientType.routes_id == route_id)
                            .where(RouteRecipientType.recipient_type == 1)
                        ).scalar()

                        # If it does not exist, then it must be a different recipient_type because this is the edit route,
                        # so update the type from user (1) to group (0)
                        if not route_recipient_type_group_exists:
                            session.execute(update(RouteRecipientType)
                                            .where(RouteRecipientType.routes_id == route_id)
                                            .values(recipient_type=1)
                                            )

                        # Delete any Recipient User bound to the Route, because,
                        # as of this point, we know it was saved with groups instead
                        session.execute(delete(RouteRecipientUsers).where(RouteRecipientUsers.routes_id == route_id))

                        # If by any chance there's no record on the route_recipient_type table, insert it
                        route_recipient_type_exists = session.execute(
                            select(RouteRecipientType)
                            .where(RouteRecipientType.routes_id == route_id)
                        ).first()
                        if not route_recipient_type_exists:
                            session.add(route_recipient_type)

                        # List of groups received on the POST
                        # Check if each group already exists on the table
                        for group in data['recipient_groups']:
                            existing_recipient_group = session.execute(
                                select(RouteRecipientGroups)
                                .where(RouteRecipientGroups.routes_id == route_id)
                                .where(RouteRecipientGroups.zendesk_groups_id == group)
                            ).first()
                            if not existing_recipient_group:  # If it does not, insert it
                                new_group_recipient = RouteRecipientGroups(
                                    routes_id=route_id,
                                    zendesk_groups_id=group
                                )
                                session.add(new_group_recipient)
                                session.flush()

                        # Make a list of all groups received to be able to delete the ones which were not received
                        list_of_received_recipient_groups = [group for group in data['recipient_groups']]
                        list_of_received_recipient_groups_as_str = []  # Make the list into ints because they came between ""
                        for group in list_of_received_recipient_groups:
                            list_of_received_recipient_groups_as_str.append(int(group))

                        # Get the groups that were already on the database
                        recipient_groups_in_database = session.execute(
                            select(RouteRecipientGroups.zendesk_groups_id)
                            .where(RouteRecipientGroups.routes_id == route_id)
                        ).all()
                        list_of_recipient_groups_in_database = []  # Make a list out of them
                        for group in recipient_groups_in_database:
                            list_of_recipient_groups_in_database.append(group[0])

                        # Subtract one list from another
                        recipient_groups_to_be_deleted = \
                            list(
                                set(list_of_recipient_groups_in_database)
                                -
                                set(list_of_received_recipient_groups_as_str)
                            )
                        session.execute(delete(RouteRecipientUsers)  # And delete the resulting list
                                        .where(RouteRecipientUsers.zendesk_users_id.in_(recipient_groups_to_be_deleted))
                                        )

                        session.commit()

                    else:
                        abort(422, 'No recipient received, please select User or Groups as recipients for the route')

        if data['ticket_tags']:
            with Session(engine) as session:
                with session.begin():
                    list_of_received_ticket_tags = []
                    for tag in data['ticket_tags']:
                        list_of_received_ticket_tags.append(int(tag))
                        if not RouteTicketTags.check_existing_tag_in_route(session, route_id, tag):
                            RouteTicketTags.insert_one_tag(session, route_id, tag)

                    list_of_ticket_locales_in_database = []
                    for tag in RouteTicketTags.select_all_tags_in_a_route(session, route_id):
                        list_of_ticket_locales_in_database.append(tag[0])

                    ticket_tags_to_be_deleted = \
                        list(
                            set(list_of_ticket_locales_in_database)
                            -
                            set(list_of_received_ticket_tags)
                        )

                    RouteTicketTags.delete_list_of_tags_in_route(session, route_id, ticket_tags_to_be_deleted)

        else:
            if not data['ticket_tags']:
                with Session(engine) as session:
                    with session.begin():
                        RouteTicketTags.delete_all_tags_in_route(session, route_id)

        if data['ticket_locales']:
            with Session(engine) as session:
                with session.begin():
                    list_of_received_ticket_locales = []
                    for locale in data['ticket_locales']:
                        list_of_received_ticket_locales.append(int(locale))
                        if not RouteTicketLocales.check_existing_locale_in_route(session, route_id, locale):
                            RouteTicketLocales.insert_one_locale(session, route_id, locale)

                    list_of_ticket_locales_in_database = []
                    for locale in RouteTicketLocales.select_all_locales_in_a_route(session, route_id):
                        list_of_ticket_locales_in_database.append(locale[0])

                    ticket_locales_to_be_deleted = \
                        list(
                            set(list_of_ticket_locales_in_database)
                            -
                            set(list_of_received_ticket_locales)
                        )

                    RouteTicketLocales.delete_list_of_locales_in_route(session, route_id, ticket_locales_to_be_deleted)

        else:
            if not data['ticket_locales']:
                with Session(engine) as session:
                    with session.begin():
                        RouteTicketLocales.delete_all_locales_in_route(session, route_id)

        if data['ticket_groups']:
            with Session(engine) as session:
                with session.begin():
                    list_of_received_ticket_groups = []
                    for group in data['ticket_groups']:
                        list_of_received_ticket_groups.append(int(group))
                        if not RouteTicketGroups.check_existing_group_in_route(session, route_id, group):
                            RouteTicketGroups.insert_one_group(session, route_id, group)

                    list_of_ticket_groups_in_database = []
                    for group in RouteTicketGroups.select_all_groups_in_a_route(session, route_id):
                        list_of_ticket_groups_in_database.append(group[0])

                    ticket_groups_to_be_deleted = \
                        list(
                            set(list_of_ticket_groups_in_database)
                            -
                            set(list_of_received_ticket_groups)
                        )

                    RouteTicketGroups.delete_list_of_groups_in_route(session, route_id, ticket_groups_to_be_deleted)

        else:
            if not data['ticket_groups']:
                with Session(engine) as session:
                    with session.begin():
                        RouteTicketGroups.delete_all_groups_in_route(session, route_id)

        return 'Data processed successfully'


@app.route('/forms/get-form-fields/<int:form_id>')
def get_form_fields(form_id):
    with Session(engine) as session:
        ticket_fields_in_form = ZendeskTicketFieldsInForms.get_form_fields(session, form_id)

    result = {'fields': []}

    for field in ticket_fields_in_form:
        result['fields'].append({'id': field[0], 'title': field[1]})

    return result
