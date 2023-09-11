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

    if is_app_in_working_hours:
        with Session(engine) as db_session:
            general_settings = GeneralSettings.get_settings(db_session)
            all_routing_views = RoutingViews.get_all_valid_routing_views(db_session)
            users_queue = UsersQueue.get_users_in_queue(db_session)

        get_tickets_from_all_views()
        users_backlog = get_users_backlog()

        for routing_view in all_routing_views:
            if RoutingViews.is_view_in_working_hours(db_session, routing_view.id):
                routing_view_unassigned_tickets = get_view_unassigned_tickets(routing_view.id)

                for each_tuple in routing_view_unassigned_tickets:
                    for each_ticket in each_tuple:
                        for each_queue_user in users_queue:
                            user = Users.get_user(db_session, each_queue_user.users_id)
                            ticket = ZendeskTickets.get_ticket_by_id(db_session, each_ticket)
                            log = TicketAssignmentLog(
                                user.id,
                                user.name,
                                user.active,
                                user.deleted,
                                user.authenticated,
                                user.routing_status,
                                each_queue_user.id,
                                each_queue_user.position,
                                ticket.ticket_id,
                                False,
                                None,
                                None,
                                True,
                                routing_view.id,
                                routing_view.name,
                                None
                            )

                            log.message = 'test'

                            print(log)

                            AssignedTicketsLog.insert_new_log(db_session, ticket.id, log.create_log_json())
                            db_session.commit()

                            return str(log.create_log_json())


                            print(users_backlog[user.id])
                            print(user.id)
                            print(user.active)
                            print(user.deleted)
                            print(user.authenticated)
                            print(user.routing_status)
                            print(user.zendesk_users_id)
                            print(user.backlog_limit)
                            print(user.hourly_ticket_assignment_limit)
                            print(user.daily_ticket_assignment_limit)










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

    return unassigned_tickets


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


def assign_ticket(ticket):
    print(ticket.id)


