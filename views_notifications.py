from models import Notifications
from app import app, engine
from sqlalchemy.orm import Session


@app.route('/get-users-next-notification/<int:user_id>')
def get_users_next_notification(user_id):
    with Session(engine) as db_session:
        notification = Notifications.get_next_pending_user_notification(db_session, user_id)

    keys = ('id', 'type', 'content', 'url')

    if notification:
        return dict(zip(keys, notification)), 200
    else:
        return 'No results', 204


@app.route('/flag-notification-as-sent/<int:notification_id>', methods=['POST', ])
def flag_notification_as_sent(notification_id):
    with Session(engine) as db_session:
        notification = Notifications.flag_notification_as_sent(db_session, notification_id)
        db_session.commit()

    if notification:
        return 'Success', 200
    else:
        return 'No results', 204


@app.route('/flag-notification-as-received/<int:notification_id>', methods=['POST', ])
def flag_notification_as_received(notification_id):
    with Session(engine) as db_session:
        notification = Notifications.flag_notification_as_received(db_session, notification_id)
        db_session.commit()

    if notification:
        return 'Success', 200
    else:
        return 'No results', 204


@app.route('/flag-notification-as-read/<int:notification_id>', methods=['POST', ])
def flag_notification_as_read(notification_id):
    with Session(engine) as db_session:
        notification = Notifications.flag_notification_as_read(db_session, notification_id)
        db_session.commit()

    if notification:
        return 'Success', 200
    else:
        return 'No results', 204


@app.route('/flag-all-notifications-as-read/<int:user_id>', methods=['POST', ])
def flag_all_notifications_as_read(user_id):
    with Session(engine) as db_session:
        notification = Notifications.flag_all_notifications_as_read(db_session, user_id)
        db_session.commit()

    if notification:
        return 'Success', 200
    else:
        return 'No results', 204
