from models import Notifications, ZendeskTickets, AssignedTickets, GeneralSettings, \
                   UsersQueue, Users, UserBacklog, AssignedTicketsLog
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
        'Novo ticket! #' + str(next_ticket.ticket_id) + ' - ' + str(next_ticket.subject),
        next_ticket.ticket_id,
    )
    db_session.commit()
    assigned_ticket = True
    return assigned_ticket


@app.route('/assign-ticket')
def assign_ticket_route():

    count = 0
    ticket = None
    recipient_user_for_ticket = None
    user = None
    settings = None
    assigned_ticket = False
    next_user_on_queue = 0
    next_user = 1

    with Session(engine) as db_session:
        ticket = ZendeskTickets.get_next_ticket_to_be_assigned(db_session)  # ticket that will be assigned
        recipient_user_for_ticket = get_recipient_user_for_ticket()  # get the next user that can receive ticket
        if recipient_user_for_ticket:
            user = Users.get_user(db_session, recipient_user_for_ticket.users_id)  # create an object with the user info
        settings = GeneralSettings.get_settings(db_session)

    if not ticket:
        flash('Não há nenhum ticket para ser distribuído!')
        return internal_render_template('home.html')

    if not recipient_user_for_ticket:
        AssignedTicketsLog.insert_new_log(
            db_session,
            ticket.id,
            'Não há nenhum agente para receber o próximo ticket!'
        )
        db_session.commit()
        flash('Não há nenhum agente para receber o próximo ticket!')
        return internal_render_template('home.html')

    if not settings:
        AssignedTicketsLog.insert_new_log(
            db_session,
            ticket.id,
            'Não há configurações definidas para poder realizar a atribuição'
        )
        db_session.commit()
        flash('Não há configurações definidas!')
        return internal_render_template('home.html')

    print(f'user.id before loop: {str(user.id)}')
    print(f'next_user_on_queue before loop: {str(next_user_on_queue)}')

    while not assigned_ticket:

        print(f'entering while for the {count + 1} time')
        count += 1

        if next_user:

            print(f'user.id after loop: {str(user.id)}')
            print(f'next_user_on_queue after loop: {str(next_user_on_queue)}')

            if user.id != next_user_on_queue:

                print(f'user.id after if: {str(user.id)}')
                print(f'next_user_on_queue after if: {str(next_user_on_queue)}')

                if ticket and user and settings:
                    with Session(engine) as db_session:

                        log = Log(
                            recipient_user_for_ticket.id,
                            recipient_user_for_ticket.position,
                            recipient_user_for_ticket.users_id,
                            user.name,
                            user.active,
                            user.deleted,
                            user.authenticated,
                            user.routing_status,
                            user.latam_user,
                            ticket.ticket_id,
                            ticket.tag_pais,
                            ''
                        )

                        if user.deleted:
                            print('if 1')
                            log.message = 'Usuário está excluído! O usuário foi excluído da fila e ' \
                                          'o próximo usuário disponível será encontrado.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            UsersQueue.remove_user_from_queue(db_session, user.id)
                            UsersQueue.delete_user_from_queue(db_session, user.id)

                            db_session.commit()

                            next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                            if next_user:
                                user = Users.get_user(db_session, next_user.users_id)

                        elif not user.active or user.routing_status == 0:
                            print('if 2')
                            log.message = 'Usuário está inativo ou offline! O usuário foi removido da fila ' \
                                          'e o próximo usuário disponível será encontrado.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            UsersQueue.remove_user_from_queue(db_session, user.id)

                            db_session.commit()

                            next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                            if next_user:
                                user = Users.get_user(db_session, next_user.users_id)

                        elif user.routing_status == 2:
                            print('if 3')
                            log.message = 'Usuário está no status ausente! ' \
                                          'O próximo usuário disponível será encontrado.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            db_session.commit()

                            next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                            if next_user:
                                user = Users.get_user(db_session, next_user.users_id)

                        elif not UserBacklog.get_agent_backlog_count(db_session, user.id) < settings.agent_backlog_limit:
                            print('if 4')
                            log.message = 'Usuário possui mais tickets em análise que o máximo configurado! ' \
                                          'O próximo usuário disponível será encontrado.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            db_session.commit()

                            next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                            if next_user:
                                user = Users.get_user(db_session, next_user.users_id)

                        elif not AssignedTickets.get_user_assigned_ticket_count_on_the_last_hour(db_session, user.id) \
                                < settings.hourly_assignment_limit:
                            print('if 5')
                            log.message = 'Usuário já recebeu mais tickets na última hora que o máximo configurado! ' \
                                          'O usuário foi enviado para o final da fila e o próximo usuário disponível ' \
                                          'será encontrado.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            db_session.commit()

                            next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                            if next_user:
                                user = Users.get_user(db_session, next_user.users_id)

                        elif not AssignedTickets.get_user_assigned_ticket_count_at_today(db_session, user.id) \
                                < settings.daily_assignment_limit:
                            print('if 6')
                            log.message = 'Usuário já recebeu mais tickets no dia que o máximo configurado! ' \
                                          'O usuário foi removido da fila e o próximo usuário disponível ' \
                                          'será encontrado.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            UsersQueue.remove_user_from_queue(db_session, user.id)
                            Notifications.create_notification(db_session, user.id, 1, 'Você foi removido da fila!')

                            db_session.commit()

                            next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                            if next_user:
                                user = Users.get_user(db_session, next_user.users_id)

                        elif not Users.is_user_on_working_hours(db_session, user.id):
                            print('if 7 - OK')
                            log.message = 'Usuário não está mais em horário de trabalho! ' \
                                          'O usuário foi removido da fila e o próximo usuário disponível ' \
                                          'será encontrado.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            UsersQueue.remove_user_from_queue(db_session, user.id)
                            Notifications.create_notification(db_session, user.id, 1, 'Você foi removido da fila!')

                            db_session.commit()

                            next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                            if next_user:
                                user = Users.get_user(db_session, next_user.users_id)

                        elif not ticket.tag_pais == 'pais_brasil' and user.latam_user == 0:
                            print('if 8')
                            log.message = 'Ticket é LATAM, mas o usuário não! ' \
                                          'O próximo usuário disponível será encontrado.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            db_session.commit()

                            next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                            if next_user:
                                user = Users.get_user(db_session, next_user.users_id)

                        elif not ticket.tag_pais == 'pais_brasil' and user.latam_user == 1 or user.latam_user == 2:
                            print('if 9')
                            log.message = 'Ticket é Brasil e o usuário está configurado como LATAM SIM ou AMBOS. ' \
                                          'O ticket foi atribuído ao usuário. ' \
                                          'O usuário foi enviado ao final da fila e próximo ticket será distribuído.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            assign_ticket(db_session, ticket, user)

                            db_session.commit()

                            flash('success')
                            return internal_render_template('home.html')

                        elif ticket.tag_pais == 'pais_brasil' and user.latam_user == 1:
                            print('if 10')
                            log.message = 'Ticket é Brasil e o usuário está configurado como LATAM SIM. ' \
                                          'O usuário foi enviado ao final da fila e próximo ticket será distribuído.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            db_session.commit()

                            next_user = UsersQueue.get_next_user_in_queue(db_session, user.id)
                            if next_user:
                                user = Users.get_user(db_session, next_user.users_id)

                        elif ticket.tag_pais == 'pais_brasil' and user.latam_user == 0 or user.latam_user == 2:
                            print('if 11')
                            log.message = 'Ticket é Brasil e o usuário está configurado como LATAM NÃO ou AMBOS. ' \
                                          'O ticket foi atribuído ao usuário. ' \
                                          'O usuário foi enviado ao final da fila e próximo ticket será distribuído.'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            db_session.commit()

                            assign_ticket(db_session, ticket, user)

                            flash('success')
                            return internal_render_template('home.html')

                        else:
                            print('else 12')
                            log.message = 'algo de errado não está certo'
                            AssignedTicketsLog.insert_new_log(
                                db_session,
                                ticket.id,
                                log.create_log(),
                                user.id,
                            )

                            db_session.commit()

                            return internal_render_template('home.html')

                else:
                    log.message = 'Não há nenhum agente disponível para receber o ticket'
                    AssignedTicketsLog.insert_new_log(
                        db_session,
                        ticket.id,
                        log.create_log(),
                        user.id,
                    )

                    db_session.commit()

                    flash('Não há nenhum agente disponível para receber o ticket')
                    break

        else:
            break

    flash('Não há nenhum ticket para ser distribuído')
    return internal_render_template('home.html')


def get_recipient_user_for_ticket():
    with Session(engine) as db_session:
        routing_model = GeneralSettings.get_settings(db_session)

    if routing_model.routing_model == 1:
        with Session(engine) as db_session:
            recipient_user_for_ticket = UsersQueue.get_first_user_in_queue(db_session)

        return recipient_user_for_ticket


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
