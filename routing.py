from app import app, engine
from models import Users, Notifications
from flask import flash, request, redirect, url_for, render_template, session, jsonify
from flask_login import login_user
from helpers import UserForm
from sqlalchemy.orm import Session
from json import dumps


@app.route('/get-users-next-notification/<int:user_id>')
def get_users_next_notification(user_id):
    with Session(engine) as db_session:
        notification = Notifications.get_next_pending_user_notification(db_session, user_id)

    keys = ('id', 'type', 'content', 'url')

    if notification:
        return dict(zip(keys, notification)), 200
    else:
        return 'No results', 204


@app.route('/flag-notification-as-sent/<int:notification_id>', methods=['PUT', ])
def flag_notification_as_sent(notification_id):
    with Session(engine) as db_session:
        notification = Notifications.flag_notification_as_sent(db_session, notification_id)
        db_session.commit()

    if notification:
        return 'Success', 200
    else:
        return 'No results', 204


@app.route('/flag-notification-as-received/<int:notification_id>', methods=['PUT', ])
def flag_notification_as_received(notification_id):
    with Session(engine) as db_session:
        notification = Notifications.flag_notification_as_received(db_session, notification_id)
        db_session.commit()

    if notification:
        return 'Success', 200
    else:
        return 'No results', 204
