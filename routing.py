from models import Notifications, ZendeskTickets, AssignedTickets, GeneralSettings, \
    UsersQueue, Users, UserBacklog, AssignedTicketsLog
from config import ZENDESK_BASE_URL
import requests
from helpers import generate_zendesk_headers, internal_render_template
from app import app, engine, csrf
from sqlalchemy.orm import Session
from flask import flash, request, session
import time
from flask_login import login_required
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, delete, update, insert, and_, or_
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from datetime import datetime, timedelta, date
from config import url_object, ZENDESK_BASE_URL
import uuid
import threading
from views_login import load_user, logout_user
from scheduler import scheduler

"""
    In case two tickets arrive together or very close one from another, it's a must to guarantee that the first ticket
    has been assigned before trying to assign the second one.
    If that's no the case, the same user could receive both tickets, depending on how fast the assignment of the first
    ticket happens.
    To ensure that, we'll be using the threading library by executing the method notify_all() after the assignment of 
    the first is finished.
"""
queue_threading = threading.Condition()


class Log:
    def __init__(self, queue_id, queue_position, user_id, user_name, user_active, user_deleted,
                 user_authenticated, user_status, user_latam, ticket_id, ticket_tags, message):
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
        self.ticket_tags = ticket_tags
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
            'ticket_tags': self.ticket_tags,
            'message': self.message,
        }

        return str(log)


@app.route('/request-ticket-assignment/', methods=['POST', ])
@csrf.exempt
def request_ticket_assignment():
    """
    :request_json:
        {
            "ticket_id": <int>,
            "ticket_subject": <str>,
            "ticket_channel": <str>,
            "ticket_tags": <str>,
        }
    """

    ticket_data_as_json = request.get_json()

    not_permitted_channels = ['chat', 'api', 'whatsapp', 'Messaging']

    if ticket_data_as_json['ticket_channel'] not in not_permitted_channels:
        new_ticket = ZendeskTickets(
            ticket_id=ticket_data_as_json['ticket_id'],
            ticket_subject=ticket_data_as_json['ticket_subject'],
            ticket_channel=ticket_data_as_json['ticket_channel'],
            ticket_tags=ticket_data_as_json['ticket_tags'],
        )

        with Session(engine) as db_session:
            # insert the new ticket, flush, call the assign ticket proccess, and only then commit so that it does not
            # interfere with the scheduled process that also assign tickets
            ZendeskTickets.insert_new_ticket(db_session, new_ticket)
            db_session.commit()

            assigned_ticket = assign_ticket_proxy(new_ticket)

        return assigned_ticket

    else:
        return 'Canal não aceito!', 406


# @scheduler.scheduled_job('interval', id='get_tickets_to_be_assigned', minutes=1)
def assign_next_pending_ticket():
    with Session(engine) as db_session:
        is_currently_hour_working_hours = GeneralSettings.is_currently_hour_working_hours(db_session)

    if is_currently_hour_working_hours:
        with Session(engine) as db_session:
            next_pending_ticket = ZendeskTickets.get_next_ticket_to_be_assigned(db_session)

        assign_ticket_proxy(next_pending_ticket)


def assign_ticket_proxy(ticket):
    with queue_threading:  # queue_threading necessary to prevent two request to be processed at the same time
        assigned_ticket = assign_ticket(ticket)
        queue_threading.notify_all()
        return assigned_ticket


def assign_ticket(ticket):
    with Session(engine) as db_session:
        general_settings = GeneralSettings.get_settings(db_session)
        is_current_hour_working_hours = GeneralSettings.is_currently_hour_working_hours(db_session)

    if is_current_hour_working_hours:
        if general_settings.routing_model == 0:
            ticket_assignment = assign_ticket_least_active(ticket)
        elif general_settings.routing_model == 1:
            ticket_assignment = assign_ticket_round_robin(ticket)
        else:
            return 'Modo de distribuição não configurado', 500

        return ticket_assignment, 200

    else:
        print('else')
        log = Log(
            None, None, None, None, None, None, None, None, None, ticket.ticket_id, ticket.ticket_tags,
            'Ticket recebido fora do horário de operação da aplicação.')
        with Session(engine) as db_session:
            AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), None)
            db_session.commit()
        return 'Fora do horário de funcionamento da aplicação! ' \
               'O ticket será distribuído após o início do horário de funcionamento.', 201


@app.route('/round-robin/<ticket>')
@csrf.exempt
def assign_ticket_round_robin(ticket):
    with Session(engine) as db_session:
        entire_queue = UsersQueue.get_users_in_queue(db_session)

    for queue in entire_queue:

        with Session(engine) as db_session:
            queue_user = UsersQueue.get_first_user_in_queue(db_session)

            user = Users.get_user(db_session, queue_user.users_id)
            user_backlog = UserBacklog.get_user_backlog(db_session, queue_user.users_id)
            tickets_in_the_last_hour = AssignedTickets.user_tickets_in_the_last_hour(db_session, queue_user.users_id)
            tickets_today = AssignedTickets.user_tickets_today(db_session, queue_user.users_id)
            is_user_in_working_hours = Users.is_user_on_working_hours(db_session, queue_user.users_id)
            app_settings = GeneralSettings.get_settings(db_session)
            db_ticket = ZendeskTickets.get_ticket_by_ticket_id(db_session, ticket.ticket_id)

            log = Log(
                queue.id, queue.position, user.id, user.name, user.active, user.deleted, user.authenticated,
                user.routing_status, user.latam_user, ticket.id, ticket.ticket_tags, None)

            if user.deleted or not user.active:
                UsersQueue.delete_user_from_queue(db_session, user.id)
                log.message = 'Usuário excluído da fila.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if user.routing_status == 0:  # 0 = offline
                UsersQueue.remove_user_from_queue(db_session, user.id)
                log.message = 'Usuário removido da fila.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if user.routing_status == 1:  # 1 = online
                pass

            if user.routing_status == 2:  # 2 = away
                log.message = 'Usuário ausente.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if user.backlog_limit > len(user_backlog) or app_settings.agent_backlog_limit > len(user_backlog):
                log.message = 'Usuário com backlog cheio.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if user.hourly_ticket_assignment_limit > tickets_in_the_last_hour or \
                app_settings.hourly_ticket_assignment_limit > tickets_in_the_last_hour:
                log.message = 'Usuário atingiu o limite de tickets atribuídos na hora corrente.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if user.daily_ticket_assignment_limit > tickets_today or \
                app_settings.daily_ticket_assignment_limit > tickets_today:
                UsersQueue.remove_user_from_queue(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 1,
                    "Você foi removido da fila de agentes! Motivo: você atingiu seu limite diário de tickets 😎"
                )
                log.message = 'Usuário atingiu o limite diário de tickets atribuídos.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if not is_user_in_working_hours:
                UsersQueue.remove_user_from_queue(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 1,
                    "Você foi removido da fila de agentes! Motivo: você está fora do seu horário de operação 🕗"
                )
                log.message = 'Usuário não está mais em horário de trabalho.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if 'contestacao_jnj' in ticket.ticket_tags and user.jnj_contestation_user:
                zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                AssignedTickets.insert_new_assigned_ticket(db_session, db_ticket.id, user.id)
                UsersQueue.move_user_to_queue_end(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 0,
                    f'Novo ticket! #{ticket.ticket_id} - {ticket.ticket_subject}',
                    ticket.ticket_id
                )
                log.message = f'Ticket #{ticket.ticket_id} atribuído ao usuário {user.name}.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                break
            if 'contestacao_jnj' in ticket.ticket_tags and not user.jnj_contestation_user:
                log.message = 'Ticket é de contestação, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if 'categoriza_ticket_homologacao_jnj' in ticket.ticket_tags and user.jnj_homologation_user:
                zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                AssignedTickets.insert_new_assigned_ticket(db_session, db_ticket.id, user.id)
                UsersQueue.move_user_to_queue_end(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 0,
                    f'Novo ticket! #{ticket.ticket_id} - {ticket.ticket_subject}',
                    ticket.ticket_id
                )
                log.message = f'Ticket #{ticket.ticket_id} atribuído ao usuário {user.name}.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                break
            if 'categoriza_ticket_homologacao_jnj' in ticket.ticket_tags and not user.jnj_homologation_user:
                log.message = 'Ticket é de homologação, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if 'cliente_sem_acesso_wpp' in ticket.ticket_tags and user.chatbot_no_service_user:
                zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                AssignedTickets.insert_new_assigned_ticket(db_session, db_ticket.id, user.id)
                UsersQueue.move_user_to_queue_end(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 0,
                    f'Novo ticket! #{ticket.ticket_id} - {ticket.ticket_subject}',
                    ticket.ticket_id
                )
                log.message = f'Ticket #{ticket.ticket_id} atribuído ao usuário f{user.name}.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                break
            if 'cliente_sem_acesso_wpp' in ticket.ticket_tags and not user.chatbot_no_service_user:
                log.message = 'Ticket é de Chatbot sem acesso, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if 'rock_stars' in ticket.ticket_tags and user.rock_star_user:
                zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                AssignedTickets.insert_new_assigned_ticket(db_session, db_ticket.id, user.id)
                UsersQueue.move_user_to_queue_end(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 0,
                    f'Novo ticket! #{ticket.ticket_id} - {ticket.ticket_subject}',
                    ticket.ticket_id
                )
                log.message = f'Ticket #{ticket.ticket_id} atribuído ao usuário f{user.name}.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                break
            if 'rock_stars' in ticket.ticket_tags and not user.rock_star_user:
                log.message = 'Ticket é Rock Stars, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if 'pais_' not in ticket.ticket_tags and user.latam_user == 0 or user.latam_user == 2:
                zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                AssignedTickets.insert_new_assigned_ticket(db_session, db_ticket.id, user.id)
                UsersQueue.move_user_to_queue_end(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 0,
                    f'Novo ticket! #{ticket.ticket_id} - {ticket.ticket_subject}',
                    ticket.ticket_id
                )
                log.message = f'Ticket #{ticket.ticket_id} atribuído ao usuário f{user.name}.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                break

            if 'pais_brasil' in ticket.ticket_tags and user.latam_user == 0 or user.latam_user == 2:
                zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                AssignedTickets.insert_new_assigned_ticket(db_session, db_ticket.id, user.id)
                UsersQueue.move_user_to_queue_end(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 0,
                    f'Novo ticket! #{ticket.ticket_id} - {ticket.ticket_subject}',
                    ticket.ticket_id
                )
                log.message = f'Ticket #{ticket.ticket_id} atribuído ao usuário f{user.name}.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                break
            if 'pais_brasil' in ticket.ticket_tags and user.latam_user == 1:
                log.message = 'Ticket é do Brasil, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

            if 'pais_brasil' not in ticket.ticket_tags and user.latam_user == 1 or user.latam_user == 2:
                zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                AssignedTickets.insert_new_assigned_ticket(db_session, db_ticket.id, user.id)
                UsersQueue.move_user_to_queue_end(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 0,
                    f'Novo ticket! #{ticket.ticket_id} - {ticket.ticket_subject}',
                    ticket.ticket_id
                )
                log.message = f'Ticket #{ticket.ticket_id} atribuído ao usuário f{user.name}.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                break
            if 'pais_brasil' not in ticket.ticket_tags and user.latam_user == 0:
                log.message = 'Ticket é LATAM, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                db_session.commit()
                continue

    log.message = 'Fim do ciclo de distribuição.'
    AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
    db_session.commit()

    return 'success'


def assign_ticket_least_active(ticket_data_as_json):
    return 'success'


def zendesk_assign_ticket(ticket_id, zendesk_user_id):
    zendesk_endpoint_url = f'/api/v2/tickets/{ticket_id}'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    assign_ticket_json = \
        {
            "ticket": {
                "status": "open",
                "assignee_id": zendesk_user_id
            }
        }

    request_json = assign_ticket_json
    api_response = requests.put(api_url, json=request_json, headers=generate_zendesk_headers())

    return str(api_response.status_code)
