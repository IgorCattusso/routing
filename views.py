from app import app, engine
from models import ZendeskUsers, ZendeskGroups, ZendeskGroupMemberships, ZendeskLocales, ZendeskTicketForms, \
    ZendeskTags, Routes, ZendeskSchedules, GeneralSettings
from sqlalchemy import select, desc, case, func
from sqlalchemy.orm import Session
from flask import render_template, session, redirect, request
import time
from flask_login import login_required
from models import Users


@app.route('/')
def home():
    time.sleep(.35)
    return render_template('home.html')


@app.route('/zendesk-users')
def zendesk_users():
    stmt = select(ZendeskUsers).order_by(ZendeskUsers.name)
    with Session(engine) as db_session:
        user_list = db_session.execute(stmt).all()

    time.sleep(.35)
    return render_template('zendesk-users.html', users=user_list)


@app.route('/zendesk-groups')
def zendesk_groups():
    stmt = select(ZendeskGroups.id, ZendeskGroups.zendesk_group_id, ZendeskGroups.name,
                  func.count(ZendeskGroupMemberships.zendesk_users_id).label('count')) \
        .join(ZendeskGroupMemberships, isouter=True) \
        .group_by(ZendeskGroups.id, ZendeskGroups.name) \
        .order_by(desc('count'))
    with Session(engine) as db_session:
        group_list = db_session.execute(stmt).all()

    time.sleep(.35)
    return render_template('zendesk-groups.html', groups=group_list)


@app.route('/reports')
def reports():
    time.sleep(.35)
    return render_template('reports.html')


@app.route('/zendesk-locales')
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
        zendesk_locales = db_session.execute(stmt).all()

    time.sleep(.35)
    return render_template('zendesk-locales.html', locales=zendesk_locales)


@app.route('/zendesk-tags')
def zendesk_tags():
    stmt = select(ZendeskTags.id, ZendeskTags.tag)

    with Session(engine) as db_session:
        zendesk_tags = db_session.execute(stmt).all()

    time.sleep(.35)
    return render_template('zendesk-tags.html', tags=zendesk_tags)


@app.route('/zendesk-ticket-forms')
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
    return render_template('zendesk-ticket-forms.html', ticket_forms=zendesk_ticket_forms)


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
    return render_template('routes.html', routes=app_routes)


@app.route('/routing-settings')
def routing_settings():
    with Session(engine) as db_session:
        all_settings = GeneralSettings.get_settings(db_session)

    time.sleep(.35)
    for row in all_settings:
        return render_template(
            'routing-settings.html',
            use_routes=row.use_routes,
            routing_model=row.routing_model,
            agent_backlog_limit=row.agent_backlog_limit,
            daily_assignment_limit=row.daily_assignment_limit,
            hourly_assignment_limit=row.hourly_assignment_limit,
        )


@app.route('/zendesk-schedules')
def zendesk_schedules():
    with Session(engine) as db_session:
        all_schedules = ZendeskSchedules.get_schedules(db_session)

    time.sleep(.35)
    return render_template('zendesk-schedules.html', schedules=all_schedules)


@app.route('/change-status')
def change_user_status():

    user_status = session['routing_status']

    if user_status == 1:
        session['routing_status'] = 2
    elif user_status == 2:
        session['routing_status'] = 1
    else:
        session['routing_status'] = 0

    with Session(engine) as db_session:
        Users.change_routing_status(db_session, session['_user_id'], session['routing_status'])
        db_session.commit()

    time.sleep(.35)

    return redirect(request.referrer)


@app.route('/users')
def users():
    with Session(engine) as db_session:
        all_users = Users.get_all_users(db_session)

    time.sleep(.35)

    return render_template('users.html', all_users=all_users)
