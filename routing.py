from models import Notifications, ZendeskTickets, AssignedTickets, GeneralSettings, UsersQueue, Users, UserBacklog
from config import API_BASE_URL
import requests
from helpers import generate_zendesk_headers
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


@app.route('/assign-ticket')
def assign_ticket():
    with Session(engine) as db_session:
        next_ticket = ZendeskTickets.get_next_ticket_to_be_assigned(db_session)  # ticket that will be assigned
        recipient_user_for_ticket = get_recipient_user_for_ticket()  # get the next user that can receive ticket
        user = Users.get_user(db_session, recipient_user_for_ticket.users_id)  # create an object with the user info
        settings = GeneralSettings.get_settings(db_session)

    assigned_ticket = False

    while not assigned_ticket:
        if next_ticket and recipient_user_for_ticket and user and settings:
            with Session(engine) as db_session:
                if user.deleted:  # if the user is deleted, delete it from the queue and get the next user in queue
                    print('if 1')
                    UsersQueue.delete_user_from_queue(db_session, user.id)
                    db_session.commit()
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)
                elif not user.active or user.routing_status == 0:  # if the user is not active or offline, remove it
                    print('if 2')                                  # from the queue and get the next user in queue
                    UsersQueue.remove_user_from_queue(db_session, user.id)
                    db_session.commit()
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)
                elif user.routing_status == 2:  # if the user is away, get the next user in the queue
                    print('if 3 - OK')
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)
                elif not UserBacklog.get_agent_backlog_count(db_session, user.id) < settings.agent_backlog_limit:
                    # if the user has more tickets than the backlog limit, move the user
                    # to the end of the queue and get the next user
                    print('if 4')
                    UsersQueue.move_user_to_queue_end(db_session, user.id)
                    db_session.commit()
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)
                elif not AssignedTickets.get_user_assigned_ticket_count_on_the_last_hour(db_session, user.id) \
                        < settings.hourly_assignment_limit:
                    print('if 5 - OK')
                    UsersQueue.move_user_to_queue_end(db_session, user.id)
                    db_session.commit()
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)
                elif not AssignedTickets.get_user_assigned_ticket_count_at_today(db_session, user.id) \
                        < settings.daily_assignment_limit:
                    print('if 6')
                    UsersQueue.remove_user_from_queue(db_session, user.id)
                    db_session.commit()
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)
                elif not Users.is_user_on_working_hours(db_session, user.id):
                    print('if 7 - OK')
                    UsersQueue.remove_user_from_queue(db_session, user.id)
                    db_session.commit()
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)
                elif not next_ticket.tag_pais == 'pais_brasil' and user.latam_user == 0:
                    print('if 8')
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)
                elif not next_ticket.tag_pais == 'pais_brasil' and user.latam_user == 1 or user.latam_user == 2:
                    print('if 9')
                    assign_ticket_on_zendesk(next_ticket.ticket_id, user.id)
                    UsersQueue.move_user_to_queue_end(db_session, user.id)
                    AssignedTickets.insert_new_assigned_ticket(db_session, next_ticket.id, user.id)
                    db_session.commit()
                    assigned_ticket = True
                    return 'success'
                elif next_ticket.tag_pais == 'pais_brasil' and user.latam_user == 1:
                    print('if 10')
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)
                elif next_ticket.tag_pais == 'pais_brasil' and user.latam_user == 0 or user.latam_user == 2:
                    print('if 11')
                    assign_ticket_on_zendesk(next_ticket.ticket_id, user.id)
                    UsersQueue.move_user_to_queue_end(db_session, user.id)
                    AssignedTickets.insert_new_assigned_ticket(db_session, next_ticket.id, user.id)
                    db_session.commit()
                    assigned_ticket = True
                    return 'success'
            return 'Não há nenhum agente disponível para receber o ticket'
        else:
            break

    return 'Não há nenhum ticket para ser distribuído'


@app.route('/get-recipient-user-for-ticket')
def get_recipient_user_for_ticket():
    with Session(engine) as db_session:
        routing_model = GeneralSettings.get_settings(db_session)

    if routing_model.routing_model == 1:  # Round Robin
        with Session(engine) as db_session:
            recipient_user_for_ticket = UsersQueue.get_first_user_in_queue(db_session)

        return recipient_user_for_ticket


@app.route('/assign-ticket-on-zendesk/<int:ticket_id>/<int:user_id>')
def assign_ticket_on_zendesk(ticket_id, user_id):
    zendesk_endpoint_url = f'/api/v2/tickets/{ticket_id}'
    api_url = API_BASE_URL + zendesk_endpoint_url

    with Session(engine) as db_session:
        user = Users.get_user(db_session, user_id)

    assign_ticket_json = \
        {
            "ticket": {
                "status": "open",
                "assignee_id": user.zendesk_user_id
            }
        }

    request_json = assign_ticket_json
    api_response = requests.put(api_url, json=request_json, headers=generate_zendesk_headers())

    return str(api_response.status_code)
