from models import Notifications, ZendeskTickets, AssignedTickets, GeneralSettings, UsersQueue, Users, UserBacklog, \
    AssignedTicketsLog
import requests
from helpers import generate_zendesk_headers, fix_double_quotes_in_subject
from app import app, engine, csrf
from sqlalchemy.orm import Session
from flask import request
from config import ZENDESK_BASE_URL
import threading
import json
import re
import time


"""
    In case two tickets arrive together or very close one from another, it's a must to guarantee that the first ticket
    has been assigned before trying to assign the second one.
    If that's no the case, the same user could receive both tickets, depending on how fast the assignment of the first
    ticket happens.
    To ensure that, we'll be using the threading library by executing the method notify_all() after the assignment of 
    the first is finished.
"""
queue_threading = threading.Condition()

national_ticket_tags = ['pais_brasil', 'pais_franca']


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


class ZendeskAPIResponse:
    def __init__(self, status_code, reason, text):
        self.status_code = status_code
        self.reason = reason
        self.text = text


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

    try:
        ticket_data_as_json = json.loads(request.get_data())
    except ValueError:
        ticket_data_as_json = fix_double_quotes_in_subject(request.get_data())

    print(ticket_data_as_json)

    unallowed_ticket_channels = ['api', 'whatsapp', 'messaging', 'serviço web', 'mensagens']
    """
        Central de ajuda: Formulário Web
        Aberto pelo Agent Workspace: Formulário Web
        Via API: Serviço Web ou API
        Mensagens do Zendesk (chatbot): Mensagens e Messaging
        Whatsapp: whatsapp
        Chat (web widget clássico): Chat
        E-mail: E-mail
    """

    if ticket_data_as_json['ticket_channel'].lower() not in unallowed_ticket_channels:
        new_ticket = ZendeskTickets(
            ticket_id=ticket_data_as_json['ticket_id'],
            ticket_subject=str(ticket_data_as_json['ticket_subject']).replace('"', ''),
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
        log = Log(
            None, None, None, None, None, None, None, None, None, ticket.ticket_id, ticket.ticket_tags,
            'Ticket recebido fora do horário de operação da aplicação.')
        with Session(engine) as db_session:
            AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), None)
            db_session.commit()
        return 'Fora do horário de funcionamento da aplicação! ' \
               'O ticket será distribuído após o início do horário de funcionamento.', 201


@app.route('/round-robin/<ticket>')
def assign_ticket_round_robin(ticket):
    with Session(engine) as db_session:
        entire_queue = UsersQueue.get_users_in_queue(db_session)
        queue_user = UsersQueue.get_first_user_in_queue(db_session)

    print(entire_queue)

    for queue in entire_queue:

        print(f'queue.id: {queue.id}')

        with Session(engine) as db_session:
            # queue_user = UsersQueue.get_first_user_in_queue(db_session)
            user = Users.get_user(db_session, queue_user.users_id)
            user_backlog = UserBacklog.get_user_backlog(db_session, queue_user.users_id)
            tickets_in_the_last_hour = AssignedTickets.user_tickets_in_the_last_hour(db_session, queue_user.users_id)
            tickets_today = AssignedTickets.user_tickets_today(db_session, queue_user.users_id)
            is_user_in_working_hours = Users.is_user_on_working_hours(db_session, queue_user.users_id)
            app_settings = GeneralSettings.get_settings(db_session)
            db_ticket = ZendeskTickets.get_ticket_by_ticket_id(db_session, ticket.ticket_id)
            ticket_tags = ticket.ticket_tags.split()

            log = Log(
                queue.id, queue.position, user.id, user.name, user.active, user.deleted, user.authenticated,
                user.routing_status, user.latam_user, ticket.ticket_id, ticket.ticket_tags, None)

            # TODO Condition 0: ** OK **
            if user.deleted:
                print('Condition: 0')
                log.message = 'Usuário excluído da fila. Motivo: usuário foi excluído.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue.users_id)
                UsersQueue.delete_user_from_queue(db_session, user.id)
                db_session.commit()
                continue

            # TODO Condition 1: ** OK **
            if not user.active:
                print('Condition: 1')
                log.message = 'Usuário excluído da fila. Motivo: usuário está inativo.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue.users_id)
                UsersQueue.delete_user_from_queue(db_session, user.id)
                db_session.commit()
                continue

            # TODO Condition 2: **OK**
            if user.routing_status == 0:  # 0 = offline
                print('Condition: 2')
                UsersQueue.remove_user_from_queue(db_session, user.id)
                log.message = 'Usuário removido da fila. Motivo: Usuário está offline.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 3: **OK**
            if user.routing_status == 1:  # 1 = online
                print('Condition: 3')
                pass

            # TODO: Condition 4: **OK**
            if user.routing_status == 2:  # 2 = away
                print('Condition: 4')
                log.message = 'Usuário ausente.'
                print(user.id)
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 5: **OK**
            if int(len(user_backlog) or 0) > int(user.backlog_limit or 9999) or \
                    int(len(user_backlog) or 0) > int(app_settings.agent_backlog_limit or 9999):
                print('Condition: 5')
                log.message = 'Usuário com backlog cheio.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 5.1: **OK**
            if int(len(user_backlog) or 0) < int(user.backlog_limit or 9999) or \
                    int(len(user_backlog) or 0) < int(app_settings.agent_backlog_limit or 9999):
                print('Condition: 5.1')
                pass

            # TODO Condition 6: **OK**
            if int(tickets_in_the_last_hour or 0) > int(user.hourly_ticket_assignment_limit or 9999) or \
                    int(tickets_in_the_last_hour or 0) > int(app_settings.hourly_ticket_assignment_limit or 9999):
                print('Condition: 6')
                log.message = 'Usuário atingiu o limite de tickets atribuídos na hora corrente.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 6.1: **OK**
            if int(tickets_in_the_last_hour or 0) < int(user.hourly_ticket_assignment_limit or 9999) or \
                    int(tickets_in_the_last_hour or 0) < int(app_settings.hourly_ticket_assignment_limit or 9999):
                print('Condition: 6.1')
                pass

            # TODO Condition 7: **OK**
            if int(tickets_today or 0) > int(user.daily_ticket_assignment_limit or 9999) or \
                    int(tickets_today or 0) > int(app_settings.daily_ticket_assignment_limit or 9999):
                print('Condition: 7')
                UsersQueue.remove_user_from_queue(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 1,
                    "Você foi removido da fila de agentes! Motivo: você atingiu seu limite diário de tickets 😎"
                )
                log.message = 'Usuário atingiu o limite diário de tickets atribuídos.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 7.1: **OK**
            if int(tickets_today or 0) < int(user.daily_ticket_assignment_limit or 9999) or \
                    int(tickets_today or 0) < int(app_settings.daily_ticket_assignment_limit or 9999):
                print('Condition: 7.1')
                pass

            # TODO Condition 8: **OK**
            if not is_user_in_working_hours:
                print('Condition: 8')
                UsersQueue.remove_user_from_queue(db_session, user.id)
                Notifications.create_notification(
                    db_session, user.id, 1,
                    "Você foi removido da fila de agentes! Motivo: você está fora do seu horário de operação 🕗"
                )
                log.message = 'Usuário não está mais em horário de trabalho.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 9: **OK**
            if 'contestacao_jnj' in ticket.ticket_tags and user.jnj_contestation_user:
                print('Condition: 9')
                assign_ticket_response = zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                if assign_ticket_response.status_code == 200:
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
                else:
                    log.message = f'Ocorreu um erro ao atribuir ticket no Zendesk! ' \
                                  f'{str(assign_ticket_response.status_code)} ' \
                                  f'{str(assign_ticket_response.reason)} - ' \
                                  f'{str(assign_ticket_response.text)}'
                    AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                    db_session.commit()
                    break
            # TODO Condition 10: **OK**
            if 'contestacao_jnj' in ticket.ticket_tags and not user.jnj_contestation_user:
                print('Condition: 10')
                log.message = 'Ticket é de contestação, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 11: **OK**
            if 'categoriza_ticket_homologacao_jnj' in ticket.ticket_tags and user.jnj_homologation_user:
                print('Condition: 11')
                assign_ticket_response = zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                if assign_ticket_response.status_code == 200:
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
                else:
                    log.message = f'Ocorreu um erro ao atribuir ticket no Zendesk! ' \
                                  f'{str(assign_ticket_response.status_code)} ' \
                                  f'{str(assign_ticket_response.reason)} - ' \
                                  f'{str(assign_ticket_response.text)}'
                    AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                    db_session.commit()
                    break
            # TODO Condition 12: **OK**
            if 'categoriza_ticket_homologacao_jnj' in ticket.ticket_tags and not user.jnj_homologation_user:
                print('Condition: 12')
                log.message = 'Ticket é de homologação, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 13: **OK**
            if 'cliente_sem_acesso_wpp' in ticket.ticket_tags and user.chatbot_no_service_user:
                print('Condition: 13')
                assign_ticket_response = zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                if assign_ticket_response.status_code == 200:
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
                else:
                    log.message = f'Ocorreu um erro ao atribuir ticket no Zendesk! ' \
                                  f'{str(assign_ticket_response.status_code)} ' \
                                  f'{str(assign_ticket_response.reason)} - ' \
                                  f'{str(assign_ticket_response.text)}'
                    AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                    db_session.commit()
                    break
            # TODO Condition 14: **OK**
            if 'cliente_sem_acesso_wpp' in ticket.ticket_tags and not user.chatbot_no_service_user:
                print('Condition: 14')
                log.message = 'Ticket é de Chatbot sem acesso, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 15:
            if 'rock_stars' in ticket.ticket_tags and not user.rock_star_user:
                print('Condition: 15')
                log.message = 'Ticket é Rock Stars, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 16:
            if any(tag in national_ticket_tags for tag in ticket_tags) and user.latam_user == 1:
                print('Condition: 16')
                log.message = 'Ticket é Nacional, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 17:
            if not any(tag in national_ticket_tags for tag in ticket_tags) and \
                    'pais_' in ticket.ticket_tags and user.latam_user == 0:
                print('Condition: 17')
                log.message = 'Ticket é Internacional, mas o usuário não atende este tipo de ticket.'
                AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                queue_user = UsersQueue.get_next_user_in_queue(db_session, queue_user.users_id)
                db_session.commit()
                continue

            # TODO Condition 18:
            if 'pais_' not in str(ticket.ticket_tags) and (user.latam_user == 0 or user.latam_user == 2):
                print('Condition: 18')
                assign_ticket_response = zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                if assign_ticket_response.status_code == 200:
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
                else:
                    log.message = f'Ocorreu um erro ao atribuir ticket no Zendesk! ' \
                                  f'{str(assign_ticket_response.status_code)} ' \
                                  f'{str(assign_ticket_response.reason)} - ' \
                                  f'{str(assign_ticket_response.text)}'
                    AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                    db_session.commit()
                    break

            # TODO Condition 19:
            if 'rock_stars' in ticket.ticket_tags and user.rock_star_user and \
                    bool(set(national_ticket_tags) & set(ticket.ticket_tags)) and \
                    (user.latam_user == 0 or user.latam_user == 2):
                print('Condition: 19')
                assign_ticket_response = zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                if assign_ticket_response.status_code == 200:
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
                else:
                    log.message = f'Ocorreu um erro ao atribuir ticket no Zendesk! ' \
                                  f'{str(assign_ticket_response.status_code)} ' \
                                  f'{str(assign_ticket_response.reason)} - ' \
                                  f'{str(assign_ticket_response.text)}'
                    AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                    db_session.commit()
                    break
            # TODO Condition 20:
            if 'rock_stars' in ticket.ticket_tags and user.rock_star_user and \
                    not bool(set(national_ticket_tags) & set(ticket.ticket_tags)) and \
                    user.latam_user == 1:
                print('Condition: 20')
                assign_ticket_response = zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                if assign_ticket_response.status_code == 200:
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
                else:
                    log.message = f'Ocorreu um erro ao atribuir ticket no Zendesk! ' \
                                  f'{str(assign_ticket_response.status_code)} ' \
                                  f'{str(assign_ticket_response.reason)} - ' \
                                  f'{str(assign_ticket_response.text)}'
                    AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                    db_session.commit()
                    break

            # TODO Condition 21:
            if any(tag in national_ticket_tags for tag in ticket_tags) and \
                    (user.latam_user == 0 or user.latam_user == 2):
                print('Condition: 21')
                assign_ticket_response = zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                if assign_ticket_response.status_code == 200:
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
                else:
                    log.message = f'Ocorreu um erro ao atribuir ticket no Zendesk! ' \
                                  f'{str(assign_ticket_response.status_code)} ' \
                                  f'{str(assign_ticket_response.reason)} - ' \
                                  f'{str(assign_ticket_response.text)}'
                    AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                    db_session.commit()
                    break

            # TODO Condition 22:
            if not any(tag not in national_ticket_tags for tag in ticket_tags) \
                    and user.latam_user == 1 or user.latam_user == 2:
                assign_ticket_response = zendesk_assign_ticket(ticket.ticket_id, user.zendesk_user_id)
                if assign_ticket_response.status_code == 200:
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
                else:
                    log.message = f'Ocorreu um erro ao atribuir ticket no Zendesk! ' \
                                  f'{str(assign_ticket_response.status_code)} ' \
                                  f'{str(assign_ticket_response.reason)} - ' \
                                  f'{str(assign_ticket_response.text)}'
                    AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), user.id)
                    db_session.commit()
                    break

    if not entire_queue:
        log1 = Log(
            None, None, None, None, None, None, None, None, None,
            ticket.id, ticket.ticket_tags, 'Não há usuários na fila.')
        AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log1), None)

        log2 = Log(
            None, None, None, None, None, None, None, None, None,
            ticket.id, ticket.ticket_tags, 'Fim do ciclo de distribuição.')
        AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log2), None)

        db_session.commit()

    else:
        log.message = 'Fim do ciclo de distribuição.'
        AssignedTicketsLog.insert_new_log(db_session, ticket.id, Log.create_log(log), None)
        db_session.commit()

    print('Fim do ciclo de distribuição.')

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

    if api_response.status_code == 429:
        time.sleep(int(api_response.headers['retry-after']))
        api_response = requests.put(api_url, json=request_json, headers=generate_zendesk_headers())

    response_text = str(api_response.text)
    formatted_response_text = response_text.replace('"', '').replace('{', '').replace('}', '') \
        .replace(',', ', ').replace(':', ': ').replace('[', '').replace(']', '')

    response = ZendeskAPIResponse(api_response.status_code, api_response.reason, formatted_response_text)

    return response
