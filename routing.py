from models import Notifications, ZendeskTickets, AssignedTickets, GeneralSettings, UsersQueue, Users, UserBacklog
from config import ZENDESK_BASE_URL
import requests
from helpers import generate_zendesk_headers, internal_render_template
from app import app, engine
from sqlalchemy.orm import Session
from flask import flash


class Log:
    def __init__(self, queue_id, queue_position, user_id, user_name, user_active, user_deleted,
                 user_authenticated, user_status, user_latam, ticket_id, tag_pais, message):
        self.queue_id = queue_id
        self.queue_position = queue_position
        self.user_id = user_id
        self.user_name = user_name
        self.user_active = user_active
        self.user_deleted = user_deleted
        self.user_authenticated = user_authenticated
        self.user_status = user_status
        self.user_latam = user_latam
        self.ticket_id = ticket_id
        self.tag_pais = tag_pais
        self.message = message

    def create_log(self):
        log = {
            'queue_id': self.queue_id,
            'queue_position': self.queue_position,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_active': self.user_active,
            'user_deleted': self.user_deleted,
            'user_authenticated': self.user_authenticated,
            'user_status': self.user_status,
            'user_latam': self.user_latam,
            'ticket_id': self.ticket_id,
            'tag_pais': self.tag_pais,
            'message': self.message,
        }

        return str(log)


def assign_ticket(db_session, next_ticket, user):
    assign_ticket_on_zendesk(next_ticket.ticket_id, user.id)
    UsersQueue.move_user_to_queue_end(db_session, user.id)
    AssignedTickets.insert_new_assigned_ticket(db_session, next_ticket.id, user.id)
    Notifications.create_notification(
        db_session,
        user.id,
        0,
        next_ticket.subject,
        next_ticket.ticket_id,
    )
    db_session.commit()
    assigned_ticket = True
    return assigned_ticket


@app.route('/assign-ticket')
def assign_ticket_route():

    count = 0
    next_ticket = None
    recipient_user_for_ticket = None
    user = None
    settings = None
    assigned_ticket = False

    with Session(engine) as db_session:
        next_ticket = ZendeskTickets.get_next_ticket_to_be_assigned(db_session)  # ticket that will be assigned
        recipient_user_for_ticket = get_recipient_user_for_ticket()  # get the next user that can receive ticket
        if recipient_user_for_ticket:
            user = Users.get_user(db_session, recipient_user_for_ticket.users_id)  # create an object with the user info
        settings = GeneralSettings.get_settings(db_session)

    print(str(next_ticket))
    print(str(recipient_user_for_ticket))
    print(str(user))
    print(str(settings))

    if not next_ticket:
        flash('Não há nenhum ticket para ser distribuído')
        return internal_render_template('home.html')

    if not recipient_user_for_ticket:
        flash('Não há nenhum agente para receber o próximo ticket')
        return internal_render_template('home.html')

    if not settings:
        flash('Não há configurações definidas')
        return internal_render_template('home.html')

    while not assigned_ticket:
        print(f'entering while for the {count + 1} time')
        count += 1
        if next_ticket and user and settings:
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
                    Notifications.create_notification(db_session, user.id, 1, 'Você foi removido da fila!')
                    db_session.commit()
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)

                elif not Users.is_user_on_working_hours(db_session, user.id):
                    print('if 7 - OK')
                    UsersQueue.remove_user_from_queue(db_session, user.id)
                    Notifications.create_notification(db_session, user.id, 1, 'Você foi removido da fila! ')
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
                    assign_ticket(db_session, next_ticket, user)
                    flash('success')
                    return internal_render_template('home.html')

                elif next_ticket.tag_pais == 'pais_brasil' and user.latam_user == 1:
                    print('if 10')
                    next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                    if next_user:
                        user = Users.get_user(db_session, next_user.users_id)

                elif next_ticket.tag_pais == 'pais_brasil' and user.latam_user == 0 or user.latam_user == 2:
                    print('if 11')
                    assign_ticket(db_session, next_ticket, user)
                    flash('success')
                    return internal_render_template('home.html')

        else:
            flash('Não há nenhum agente disponível para receber o ticket')
            break

    flash('Não há nenhum ticket para ser distribuído')
    return internal_render_template('home.html')


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
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

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
