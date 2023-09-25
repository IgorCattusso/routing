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
        return

    print('onix')
    with Session(engine) as db_session:
        general_settings = GeneralSettings.get_settings(db_session)
        all_routing_views = RoutingViews.get_all_valid_routing_views(db_session)
        users_queue = UsersQueue.get_users_in_queue(db_session)

    get_tickets_from_all_views()
    users_backlog = get_users_backlog()

    for routing_view in all_routing_views:
        print('charmander')

        if RoutingViews.is_view_in_working_hours(db_session, routing_view.id):
            print('squirtle')

            routing_view_unassigned_tickets = get_view_unassigned_tickets(routing_view.id)

            if routing_view_unassigned_tickets:
                print('bulbassaur')
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


def get_view_unassigned_tickets(routing_view_id):
    with Session(engine) as db_session:
        zendesk_view_id = db_session.execute(
            select(RoutingViews.zendesk_views_id)
            .where(RoutingViews.id == routing_view_id)
        ).scalar()

        unassigned_tickets = db_session.execute(
            select(ZendeskTickets.id)
            .select_from(join(
                ZendeskTickets,
                AssignedTickets,
                AssignedTickets.zendesk_tickets_id == ZendeskTickets.id,
                isouter=True
            ))
            .join(ZendeskViewsTickets)
            .where(AssignedTickets.id == None)
            .where(ZendeskViewsTickets.zendesk_views_id == zendesk_view_id)
        ).all()

    unassigned_tickets_list = [ticket for each_tuple in unassigned_tickets for ticket in each_tuple]

    return unassigned_tickets_list


def get_users_backlog():
    zendesk_endpoint_url = 'api/v2/search.json?page=1'
    zendesk_search_query = 'query=type:ticket status:open status:pending'

    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url + '&' + zendesk_search_query

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    backlog = {}

    while next_url:
        for ticket in api_response['results']:
            if ticket['assignee_id']:
                assignee_id = ticket['assignee_id']
                with Session(engine) as db_session:
                    zendesk_users_id = ZendeskUsers.get_zendesk_users_id(db_session, assignee_id)
                    user = Users.get_user_from_zendesk_users_id(db_session, zendesk_users_id)
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


