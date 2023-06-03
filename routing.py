from models import Notifications, ZendeskTickets, AssignedTickets, GeneralSettings, \
                   UsersQueue, Users, UserBacklog, AssignedTicketsLog
from config import ZENDESK_BASE_URL
import requests
from helpers import generate_zendesk_headers, internal_render_template
from app import app, engine, csrf
from sqlalchemy.orm import Session
from flask import flash, request
import time
from flask_login import login_required
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, delete, update, insert, and_, or_
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from config import url_object, ZENDESK_BASE_URL
import uuid
import threading


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
            "created_at": <datetime>
        }
    """

    ticket_data_as_json = request.get_json()

    assignment_request = assign_ticket(ticket_data_as_json)

# @scheduler.scheduled_job('interval', id='get_tickets_to_be_assigned', minutes=1)
def assign_next_pending_ticket():
    with Session(engine) as db_session:
        is_currently_hour_working_hours = GeneralSettings.is_currently_hour_working_hours(db_session)


def assign_ticket(ticket_data_as_json):
    with Session(engine) as db_session:
        general_settings = GeneralSettings.get_settings(db_session)
        ZendeskTickets.insert_new_ticket(db_session, ticket_data_as_json)
        db_session.commit()

    with queue_threading:
        if general_settings.routing_model == 0:
            assign_ticket_least_active(ticket_data_as_json)
        elif general_settings.routing_model == 1:
            assign_ticket_round_robin(ticket_data_as_json)
        else:
            raise Exception('Modo de distribuição não configurado!')

        queue_threading.notify_all()


def assign_ticket_round_robin(ticket_data_as_json):


    return 'success'


def assign_ticket_least_active(ticket_data_as_json):
    pass


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
