from app import app, engine
from models import ZendeskUsers, Users, ZendeskSchedules
from sqlalchemy.orm import Session
from flask import render_template, request


@app.route('/users/new/', methods=['GET', 'POST', ])
def new_user():
    if request.method == 'GET':
        with Session(engine) as session:
            zendesk_users = ZendeskUsers.get_zendesk_users(session)
            zendesk_schedules = ZendeskSchedules.get_schedules(session)

        return render_template(
            'user-new.html', zendesk_users=zendesk_users, zendesk_schedules=zendesk_schedules,
        )

    if request.method == 'POST':
        data = request.get_json()

        with Session(engine) as session:
            Users.insert_new_user(
                session,
                data['user_name'],
                data['user_email'],
                data['user_status'],
                data['zendesk_users_id'],
                data['zendesk_schedules_id'],
                data['latam_user'],
            )
            session.commit()

        return 'Success'


@app.route('/users/delete/<int:user_id>', methods=['DELETE', ])
def delete_user(user_id):

    with Session(engine) as session:
        Users.delete_user(session, user_id)
        session.commit()

    return 'Data processed successfully'


@app.route('/users/edit/<int:user_id>', methods=['GET', 'PUT', ])
def get_user(user_id):

    if request.method == 'GET':
        with Session(engine) as session:
            user = Users.get_user(session, user_id)
            zendesk_users = ZendeskUsers.get_zendesk_users(session)
            zendesk_user_email = ZendeskUsers.get_zendesk_user_email_by_user_id(session, user.zendesk_users_id)
            zendesk_schedules = ZendeskSchedules.get_schedules(session)
            zendesk_schedule_name = ZendeskSchedules.get_zendesk_schedule_name_by_id(session, user.zendesk_schedules_id)

        return render_template(
            'user-edit.html',
            user=user,
            zendesk_users=zendesk_users,
            zendesk_user_email=zendesk_user_email,
            zendesk_schedules=zendesk_schedules,
            zendesk_schedule_name=zendesk_schedule_name,
        )

    if request.method == 'PUT':
        data = request.get_json()

        with Session(engine) as session:
            Users.update_user(
                session,
                data['user_id'],
                data['user_name'],
                data['user_email'],
                data['user_status'],
                data['zendesk_users_id'],
                data['zendesk_schedules_id'],
                data['latam_user'],
            )
            session.commit()

        return 'Success'
