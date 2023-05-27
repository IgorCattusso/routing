from app import app, engine
from models import ZendeskUsers, ZendeskGroups, ZendeskGroupMemberships, ZendeskLocales, ZendeskTicketForms, \
    ZendeskTags, Routes, ZendeskSchedules, GeneralSettings, AssignedTicketsLog
from sqlalchemy import select, desc, case, func
from sqlalchemy.orm import Session
from flask import session, redirect, request
import time
from flask_login import login_required
from models import Users
from helpers import internal_render_template
from views_logs import logs_as_list


@app.route('/')
@login_required
def home():
    time.sleep(.35)
    return internal_render_template('home.html')


@app.route('/zendesk-users')
@login_required
def zendesk_users():
    stmt = select(ZendeskUsers).order_by(ZendeskUsers.name)
    with Session(engine) as db_session:
        user_list = db_session.execute(stmt).all()

    time.sleep(.35)
    return internal_render_template('zendesk-users.html', users=user_list)


@app.route('/zendesk-groups')
@login_required
def zendesk_groups():
    stmt = select(ZendeskGroups.id, ZendeskGroups.zendesk_group_id, ZendeskGroups.name,
                  func.count(ZendeskGroupMemberships.zendesk_users_id).label('count')) \
        .join(ZendeskGroupMemberships, isouter=True) \
        .group_by(ZendeskGroups.id, ZendeskGroups.name) \
        .order_by(desc('count'))
    with Session(engine) as db_session:
        group_list = db_session.execute(stmt).all()

    time.sleep(.35)
    return internal_render_template('zendesk-groups.html', groups=group_list)


@app.route('/zendesk-locales')
@login_required
def zendesk_locales():
    stmt = select(ZendeskLocales.id,
                  ZendeskLocales.zendesk_locale_id,
                  ZendeskLocales.locale,
                  ZendeskLocales.name,
                  case(
                      (ZendeskLocales.default == 1, 'Sim'),
                      (ZendeskLocales.default == 0, 'Não'),
                      else_='')
                  .label('default'))
    with Session(engine) as db_session:
        all_zendesk_locales = db_session.execute(stmt).all()

    time.sleep(.35)
    return internal_render_template('zendesk-locales.html', locales=all_zendesk_locales)


@app.route('/zendesk-tags')
@login_required
def zendesk_tags():
    stmt = select(ZendeskTags.id, ZendeskTags.tag)

    with Session(engine) as db_session:
        all_zendesk_tags = db_session.execute(stmt).all()

    time.sleep(.35)
    return internal_render_template('zendesk-tags.html', tags=all_zendesk_tags)


@app.route('/zendesk-ticket-forms')
@login_required
def zendesk_ticket_forms():
    stmt = select(ZendeskTicketForms.id,
                  ZendeskTicketForms.zendesk_ticket_form_id,
                  ZendeskTicketForms.name,
                  case(
                      (ZendeskTicketForms.default == 1, 'Sim'),
                      (ZendeskTicketForms.default == 0, 'Não'),
                      else_='')
                  .label('default'))

    with Session(engine) as db_session:
        zendesk_ticket_forms = db_session.execute(stmt).all()

    time.sleep(.35)
    return internal_render_template('zendesk-ticket-forms.html', ticket_forms=zendesk_ticket_forms)


@app.route('/routes')
@login_required
def routes():
    stmt = select(Routes.id, Routes.name,
                  case(
                      (Routes.active == 1, 'Sim'),
                      (Routes.active == 0, 'Não'),
                      else_='')
                  .label('active')) \
                  .where(Routes.deleted == 0)
    with Session(engine) as db_session:
        app_routes = db_session.execute(stmt).all()

    time.sleep(.35)
    return internal_render_template('routes.html', routes=app_routes)


@app.route('/routing-settings')
@login_required
def routing_settings():
    with Session(engine) as db_session:
        all_settings = GeneralSettings.get_settings(db_session)
        all_schedules = ZendeskSchedules.get_schedules(db_session)
        schedule_name = ZendeskSchedules.get_zendesk_schedule_name_by_id(db_session, all_settings.zendesk_schedules_id)

    time.sleep(.35)
    return internal_render_template(
        'routing-settings.html',
        use_routes=all_settings.use_routes,
        routing_model=all_settings.routing_model,
        agent_backlog_limit=all_settings.agent_backlog_limit,
        daily_assignment_limit=all_settings.daily_assignment_limit,
        hourly_assignment_limit=all_settings.hourly_assignment_limit,
        zendesk_schedules_id=all_settings.zendesk_schedules_id,
        all_schedules=all_schedules,
        selected_schedule_name=schedule_name[0],
    )


@app.route('/zendesk-schedules')
@login_required
def zendesk_schedules():
    with Session(engine) as db_session:
        all_schedules = ZendeskSchedules.get_schedules(db_session)

    time.sleep(.35)
    return internal_render_template('zendesk-schedules.html', schedules=all_schedules)


@app.route('/change-status')
@login_required
def change_user_status():

    with Session(engine) as db_session:
        user_status = Users.get_user_status(db_session, session['_user_id'])

        if user_status == 1:
            new_user_status = 2
        elif user_status == 2:
            new_user_status = 1
        else:
            new_user_status = 0

        session['routing_status'] = new_user_status
        Users.change_routing_status(db_session, session['_user_id'], new_user_status)
        db_session.commit()

    time.sleep(.35)

    return redirect(request.referrer)


@app.route('/users')
@login_required
def users():
    with Session(engine) as db_session:
        all_users = Users.get_all_users(db_session)

    time.sleep(.35)

    return internal_render_template('users.html', all_users=all_users)


@app.route('/logs')
@login_required
def logs():
    with Session(engine) as db_session:
        last_ten_logs = AssignedTicketsLog.get_last_ten_logs(db_session)
        log_users = Users.get_all_users(db_session)

    list_of_logs = logs_as_list(last_ten_logs)

    return internal_render_template('logs.html', list_of_logs=list_of_logs, users=log_users)
