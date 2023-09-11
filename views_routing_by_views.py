from app import app, engine
from models import ZendeskGroupMemberships, RoutingViews, Notifications, ZendeskSchedules, ZendeskViews, Users, \
    RoutingViewsUsers, RoutingViewsGroups
from sqlalchemy.orm import Session
from flask import request, session
import time
from helpers import internal_render_template
from flask_login import login_required
from zendesk_tickets import get_tickets_from_a_zendesk_view


@app.route('/routing-views/new')
@login_required
def new_routing_view():
    with Session(engine) as db_session:
        recipient_groups_list = ZendeskGroupMemberships.get_all_groups_and_mebers(db_session)
        recipient_users_list = Users.get_all_users(db_session)
        zendesk_schedules = ZendeskSchedules.get_schedules(db_session)
        zendesk_views = ZendeskViews.get_all_valid_views(db_session)

    time.sleep(.35)

    return internal_render_template(
        'routing-views-new.html',
        recipient_groups=recipient_groups_list,
        recipient_users=recipient_users_list,
        zendesk_schedules=zendesk_schedules,
        zendesk_views=zendesk_views,
    )


@app.route('/routing-views/insert', methods=['POST', ])
@login_required
def insert_routing_view():
    if request.method == 'POST':
        data = request.get_json()

        new_routing_views = RoutingViews(
            zendesk_views_id=data['zendesk_view_id'],
            zendesk_schedules_id=data['zendesk_schedule_id'],
            name=data['routing_view_name'],
            active=True,
            deleted=False,
        )

        with Session(engine) as db_session:
            routing_view_insert = RoutingViewsUsers.insert_new_users_in_view(db_session, new_routing_views)
            db_session.flush()
            if routing_view_insert:
                if data['recipient_users']:
                    for user in data['recipient_users']:
                        routing_views_users_insert = RoutingViewsUsers(
                            routing_views_id=new_routing_views.id,
                            users_id=int(user),
                        )
                        RoutingViewsUsers.insert_new_users_in_view(db_session, routing_views_users_insert)

                if data['recipient_groups']:
                    for group in data['recipient_groups']:
                        routing_views_groups_insert = RoutingViewsGroups(
                            routing_views_id=new_routing_views.id,
                            zendesk_groups_id=int(group),
                        )
                        RoutingViewsGroups.insert_new_groups_in_view(db_session, routing_views_groups_insert)

            db_session.commit()

        return 'Data processed successfully'


@app.route('/routing-views/delete/<int:routing_view_id>', methods=['DELETE'])
@login_required
def delete_routing_view(routing_view_id):
    with Session(engine) as db_session:
        RoutingViews.delete_routing_view(db_session, routing_view_id)
        RoutingViewsUsers.delete_all_users_from_view(db_session, routing_view_id)
        RoutingViewsGroups.delete_all_groups_from_view(db_session, routing_view_id)
        db_session.commit()

        user_id = session['_user_id']

        Notifications.create_notification(
            db_session,
            user_id,
            1,
            'Visualização excluída com sucesso!',
        )
        db_session.commit()

    return 'Data processed successfully'


@app.route('/routing-views/deactivate/<int:routing_view_id>', methods=['PUT'])
@login_required
def deactivate_routing_view(routing_view_id):
    with Session(engine) as db_session:
        RoutingViews.deactivate_routing_view(db_session, routing_view_id)
        db_session.commit()

    return 'Data processed successfully'


@app.route('/routing-views/edit/<int:routing_view_id>')
@login_required
def edit_routing_view(routing_view_id):
    with Session(engine) as db_session:
        recipient_groups_list = ZendeskGroupMemberships.get_all_groups_and_mebers(db_session)
        recipient_users_list = Users.get_all_users(db_session)
        zendesk_schedules = ZendeskSchedules.get_schedules(db_session)
        zendesk_views = ZendeskViews.get_all_valid_views(db_session)

        routing_view = RoutingViews.get_routing_view(db_session, routing_view_id)
        selected_routing_view_users = RoutingViewsUsers.get_view_users(db_session, routing_view_id)
        selected_routing_view_groups = RoutingViewsGroups.get_view_groups(db_session, routing_view_id)
        selected_zendesk_view = ZendeskViews.get_view(db_session, routing_view.zendesk_views_id)
        selected_zendesk_schedule = ZendeskSchedules.get_schedule(db_session, routing_view.zendesk_schedules_id)

        selected_routing_view_users_as_list = []
        for each_tuple in selected_routing_view_users:
            for each_value in each_tuple:
                selected_routing_view_users_as_list.append(each_value)

        selected_routing_view_groups_as_list = []
        for each_tuple in selected_routing_view_groups:
            for each_value in each_tuple:
                selected_routing_view_groups_as_list.append(each_value)

    time.sleep(.35)

    return internal_render_template(
        'routing-views-edit.html',
        recipient_groups=recipient_groups_list,
        recipient_users=recipient_users_list,
        zendesk_schedules=zendesk_schedules,
        zendesk_views=zendesk_views,
        routing_view=routing_view,
        selected_users=selected_routing_view_users_as_list,
        selected_groups=selected_routing_view_groups_as_list,
        selected_zendesk_view=selected_zendesk_view,
        selected_zendesk_schedule=selected_zendesk_schedule,
    )


@app.route('/routing-views/update/<int:routing_view_id>', methods=['PUT', ])
@login_required
def update_routing_view(routing_view_id):
    if request.method == 'PUT':
        data = request.get_json()

        with Session(engine) as db_session:
            RoutingViews.update_routing_view(
                db_session,
                routing_view_id,
                int(data['zendesk_view_id']),
                int(data['zendesk_schedule_id']),
                data['routing_view_name'],
                data['routing_view_status'],
                False,
            )

            if data['recipient_users']:
                RoutingViewsGroups.delete_all_groups_from_view(db_session, routing_view_id)

                existing_users = RoutingViewsUsers.get_view_users(db_session, routing_view_id)

                existing_users_as_list = []
                for each_tuple in existing_users:
                    for each_value in each_tuple:
                        existing_users_as_list.append(each_value)

                selected_users_as_list = []
                for each_value in data['recipient_users']:
                    selected_users_as_list.append(int(each_value))

                users_to_remove = list(set(existing_users_as_list) - set(selected_users_as_list))
                users_to_add = list(set(selected_users_as_list) - set(existing_users_as_list))

                for user in users_to_add:
                    new_user = RoutingViewsUsers(
                        routing_views_id=routing_view_id,
                        users_id=user
                    )
                    RoutingViewsUsers.insert_new_users_in_view(db_session, new_user)

                for user in users_to_remove:
                    RoutingViewsUsers.delete_user_from_view(db_session, routing_view_id, user)

            if data['recipient_groups']:
                RoutingViewsUsers.delete_all_users_from_view(db_session, routing_view_id)

                existing_groups = RoutingViewsGroups.get_view_groups(db_session, routing_view_id)

                existing_groups_as_list = []
                for each_tuple in existing_groups:
                    for each_value in each_tuple:
                        existing_groups_as_list.append(each_value)

                selected_groups_as_list = []
                for each_value in data['recipient_groups']:
                    selected_groups_as_list.append(int(each_value))

                groups_to_remove = list(set(existing_groups_as_list) - set(selected_groups_as_list))
                groups_to_add = list(set(selected_groups_as_list) - set(existing_groups_as_list))

                for group in groups_to_add:
                    new_group = RoutingViewsGroups(
                        routing_views_id=routing_view_id,
                        zendesk_groups_id=group
                    )
                    RoutingViewsGroups.insert_new_groups_in_view(db_session, new_group)

                for group in groups_to_remove:
                    RoutingViewsGroups.delete_group_from_view(db_session, routing_view_id, group)

            db_session.commit()

        return 'Data processed successfully'


@app.route('/routing-views/run-view/<int:routing_views_id>', methods=['POST', ])
def run_view(routing_views_id):
    with Session(engine) as db_session:
        routing_view = RoutingViews.get_routing_view(db_session, routing_views_id)
        zendesk_views = ZendeskViews.get_view(db_session, routing_view.zendesk_views_id)

    get_tickets_from_a_zendesk_view(zendesk_views.id)

    return 'Data processed successfully'

