from config import ZENDESK_BASE_URL
import requests
from models import ZendeskTickets, ZendeskUsers, UserBacklog, Users, ZendeskViewsTickets, ZendeskViews, RoutingViews, \
    AssignedTickets, GeneralSettings, UsersQueue, AssignedTicketsLog
from helpers import generate_zendesk_headers, TicketAssignmentLog
from app import app, engine
from sqlalchemy import select, update, and_, or_, delete, join
from sqlalchemy.orm import Session
import time
import pytz
from datetime import datetime
from zendesk_tickets import get_tickets_from_a_zendesk_view
from scheduler import scheduler


# @scheduler.scheduled_job("interval", minutes=2)
@app.route('/routing-views/run-views')
def run_views():
    with Session(engine) as db_session:
        is_app_in_working_hours = GeneralSettings.is_currently_hour_working_hours(db_session)

    if not is_app_in_working_hours:
        print('pikachu')
        return "Outside of app working hours"

    print('onix')
    
    with Session(engine) as db_session:
        general_settings = GeneralSettings.get_settings(db_session)
        all_routing_views = RoutingViews.get_all_valid_routing_views(db_session)
        users_queue = UsersQueue.get_users_in_queue(db_session)

    get_tickets_from_all_views()
    users_backlog = get_users_backlog()

    for routing_view in all_routing_views:
        print('charmander')

        if not RoutingViews.is_view_in_working_hours(db_session, routing_view.id):
            print('squirtle')
            continue

        with Session(engine) as db_session:
            routing_view_unassigned_tickets = ZendeskViewsTickets.get_view_unassigned_tickets(db_session, routing_view.id)

        if not routing_view_unassigned_tickets:
            print('bulbassaur')
            continue
            
        with Session(engine) as db_session:
            user = UsersQueue.get_first_user_in_queue(db_session)

        print(has_user_exceeded_its_backlog_limit(users_backlog, user.users_id))
        print(has_user_exceeded_routing_backlog_limit(users_backlog, user.users_id))
















    return 'success'


@app.route('/routing-views/get-tickets-from-all-views')
def get_tickets_from_all_views():
    with Session(engine) as db_session:
        all_routing_views = RoutingViews.get_all_routing_views(db_session)

        for view in all_routing_views:
            if view.active and not view.deleted:
                zendesk_views = ZendeskViews.get_view(db_session, view.zendesk_views_id)

                get_tickets_from_a_zendesk_view(zendesk_views.id)

    return 'success'


def get_users_backlog():
    zendesk_endpoint_url = 'api/v2/search.json?page=1'
    zendesk_search_query = 'query=type:ticket status:open'

    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url + '&' + zendesk_search_query

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    backlog = {}

    while next_url:
        for ticket in api_response['results']:
            if not ticket['assignee_id']:
                continue
            
            assignee_id = ticket['assignee_id']
            
            with Session(engine) as db_session:
                zendesk_users_id = ZendeskUsers.get_zendesk_users_id(db_session, assignee_id)
                user = Users.get_user_from_zendesk_users_id(db_session, zendesk_users_id)
            
            if not zendesk_users_id or not user:
                continue
            
            if user.id in backlog:
                backlog[user.id] += 1
            else:
                backlog[user.id] = 1

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    return backlog


def has_user_exceeded_its_backlog_limit(users_backlog, user_id):
    with Session(engine) as db_session:
        user = Users.get_user(db_session, user_id)

    if user_id in users_backlog:
        user_backlog_size = users_backlog[user_id]
    else:
        return False

    if user.backlog_limit and user_backlog_size >= user.backlog_limit:
        return True
    elif user.backlog_limit and user_backlog_size < user.backlog_limit:
        return False

    return False


def has_user_exceeded_routing_backlog_limit(users_backlog, user_id):
    with Session(engine) as db_session:
        general_settings = GeneralSettings.get_settings(db_session)

    if user_id in users_backlog:
        user_backlog_size = users_backlog[user_id]
    else:
        return False

    if general_settings.backlog_limit and user_backlog_size >= general_settings.backlog_limit:
        return True
    elif general_settings.backlog_limit and user_backlog_size < general_settings.backlog_limit:
        return False

    return False


def assign_ticket(ticket):
    print(ticket.id)


