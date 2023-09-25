from config import ZENDESK_BASE_URL, ZENDESK_TICKET_LEVEL_ID
import requests
from models import ZendeskTickets, ZendeskUsers, UserBacklog, Users, ZendeskViewsTickets, ZendeskViews, AssignedTickets
from helpers import generate_zendesk_headers
from app import app, engine
from sqlalchemy import select, update, and_, or_, delete, join
from sqlalchemy.orm import Session
import time
import pytz
from datetime import datetime


def get_tickets_from_a_zendesk_view(zendesk_views_id):
    with Session(engine) as db_session:
        zendesk_view = ZendeskViews.get_view(db_session, zendesk_views_id)

    zendesk_endpoint_url = f'/api/v2/views/{zendesk_view.zendesk_view_id}/tickets.json'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for ticket in api_response['tickets']:
            with Session(engine) as db_session:
                existing_ticket = ZendeskTickets.get_ticket_by_ticket_id(db_session, ticket['id'])
                if not existing_ticket:
                    new_zendesk_ticket = ZendeskTickets(
                        ticket_id=ticket['id'],
                        ticket_channel=ticket['via']['channel'],
                        ticket_subject=ticket['subject'],
                        received_at=datetime.now(tz=pytz.timezone('America/Sao_Paulo'))
                    )
                    ZendeskTickets.insert_new_ticket(db_session, new_zendesk_ticket)
                    db_session.flush()

                    new_view_ticket = ZendeskViewsTickets(
                        zendesk_tickets_id=new_zendesk_ticket.id,
                        zendesk_views_id=zendesk_views_id,
                    )
                    ZendeskViewsTickets.insert_new_ticket_in_view(db_session, new_view_ticket)

                db_session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    return 'success'
