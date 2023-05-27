from config import ZENDESK_BASE_URL
import requests
from helpers import generate_zendesk_headers, match_false_true, internal_render_template
from models import ZendeskLocales, ZendeskTicketFields, ZendeskTicketForms, ZendeskTicketFieldsInForms, \
    ZendeskTicketFieldOptions, ZendeskTags, ZendeskSchedules, Notifications
from app import app, engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from flask import flash, redirect, url_for, session
import time
from datetime import datetime, timedelta
from flask_login import login_required


@app.route('/get-zendesk-schedules')
@login_required
def get_zendesk_schedules():
    zendesk_endpoint_url = '/api/v2/business_hours/schedules'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    inserted_schedules = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

    for schedule in api_response['schedules']:
        with Session(engine) as db_session:
            if not ZendeskSchedules.check_for_existing_schedule(db_session, schedule['id']):
                ZendeskSchedules.insert_schedule(db_session, schedule['id'], schedule['name'], schedule['time_zone'])
                db_session.commit()
                inserted_schedules.append(schedule['id'])

            for interval in schedule['intervals']:
                schedule_id = ZendeskSchedules.get_id_from_zendesk_schedule_id(db_session, schedule['id'])
                ZendeskSchedules.update_schedule_hours(
                    db_session,
                    schedule_id,
                    interval['start_time'],
                    interval['end_time']
                )
                db_session.commit()

    time.sleep(.35)

    if inserted_schedules:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                f'Programações inseridas: {inserted_schedules}',
            )
            db_session.commit()
        return redirect(url_for('zendesk_schedules'))
    else:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                f'Não há novas programações para inserir ou alterar!',
            )
            db_session.commit()
        return redirect(url_for('zendesk_schedules'))


@app.route('/zendesk-schedule/<int:schedule_id>')
@login_required
def get_zendesk_schedule_hours(schedule_id):
    with Session(engine) as db_session:
        schedule = ZendeskSchedules.get_schedule(db_session, schedule_id)

    time.sleep(.35)

    times_list = []

    for item in schedule:
        if type(item) == timedelta:
            dt = datetime(1, 1, 1, 0, 0) + item
            times_list.append(dt.strftime("%H:%M:%S"))
        elif not item:
            times_list.append('--:--:--')

    return internal_render_template(
        'zendesk-schedule.html',
        schedule_id=schedule.id,
        schedule_name=schedule.name,
        schedule_timezone=schedule.timezone,
        schedule_times=times_list,
        schedule_times_len=len(times_list),
    )


@app.route('/get-zendesk-locales')
@login_required
def get_zendesk_locales():
    zendesk_endpoint_url = '/api/v2/locales.json?page=1'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    inserted_locales = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for locale in api_response['locales']:
            stmt = select(ZendeskLocales).where(ZendeskLocales.zendesk_locale_id == locale['id'])
            with Session(engine) as db_session:
                query_result = db_session.execute(stmt).first()
                if not query_result:
                    new_locale = ZendeskLocales(zendesk_locale_id=locale['id'],
                                                locale=locale['locale'],
                                                name=locale['name'],
                                                presentation_name=locale['presentation_name'],
                                                default=match_false_true(locale['default']),
                                                )
                    inserted_locales.append(locale['locale'])
                    db_session.add(new_locale)
                    db_session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    if inserted_locales:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                f'Localidades inseridas: {inserted_locales}',
            )
            db_session.commit()
        return redirect(url_for('zendesk_locales'))
    else:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                f'Não há novas localidades para inserir ou alterar!',
            )
            db_session.commit()
        return redirect(url_for('zendesk_locales'))


@app.route('/get-zendesk-ticket-forms')
@login_required
def get_zendesk_ticket_forms():
    """
    Essa rota é um pouco complexa.
    Primeiro, é realizada a inserção dos Campos ativos,
    Em seguida, é realizada a inserção dos Formulários ativos,
    Em seguida, é realizada a inserção do vínculo entre Campos e Formulários, ou seja, quais Campos estão msg quais Forms
    Em seguida, é realizada a inserção das Opções dos Campos. As Opções dos Campos estão relacionadas aos Campos,
       mas não necessitam de uma tabela auxiliar para vinculá-las, visto que uma Opção não estará msg mais de um Campo
    """
    '''
    Inserção dos Campos ativos no zendesk
    '''
    zendesk_endpoint_url = '/api/v2/ticket_fields.json?page=1&active=true'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    inserted_ticket_fields = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for field in api_response['ticket_fields']:
            stmt = select(ZendeskTicketFields).where(ZendeskTicketFields.zendesk_ticket_field_id == field['id'])
            with Session(engine) as db_session:
                query_result = db_session.execute(stmt).first()
                if not query_result:
                    new_ticket_field = ZendeskTicketFields(zendesk_ticket_field_id=field['id'],
                                                           title=field['title'],
                                                           type=field['type'],
                                                           )
                    inserted_ticket_fields.append(field['id'])
                    db_session.add(new_ticket_field)
                    db_session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    '''
    Inserção dos Formulários ativos no zendesk
    '''
    zendesk_endpoint_url = '/api/v2/ticket_forms.json?page=1&active=true'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    inserted_ticket_forms = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for form in api_response['ticket_forms']:
            stmt = select(ZendeskTicketForms).where(ZendeskTicketForms.zendesk_ticket_form_id == form['id'])
            with Session(engine) as db_session:
                query_result = db_session.execute(stmt).first()
                if not query_result:
                    new_ticket_form = ZendeskTicketForms(zendesk_ticket_form_id=form['id'],
                                                         name=form['name'],
                                                         display_name=form['display_name'],
                                                         default=match_false_true(form['default']),
                                                         )
                    inserted_ticket_forms.append(form['id'])
                    db_session.add(new_ticket_form)
                    db_session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    '''
    Inserção do vínculo de Formulários e Campos de Formulários 
    '''
    zendesk_endpoint_url = '/api/v2/ticket_forms.json?page=1&active=true'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    inserted_ticket_fields_in_forms = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for form in api_response['ticket_forms']:
            form_id = form['id']
            for ticket_fields_in_form in form['ticket_field_ids']:
                stmt = \
                    select(ZendeskTicketFieldsInForms) \
                        .join(ZendeskTicketForms) \
                        .join(ZendeskTicketFields) \
                        .where(ZendeskTicketForms.zendesk_ticket_form_id == form_id) \
                        .where(ZendeskTicketFields.zendesk_ticket_field_id == ticket_fields_in_form)

                with Session(engine) as db_session:
                    query_result = db_session.execute(stmt).first()
                    if not query_result:  # TODO: test if the statements below can be made through the query_result var
                        zendesk_ticket_forms_id = \
                            db_session.execute(
                                select(ZendeskTicketForms.id)
                                .where(ZendeskTicketForms.zendesk_ticket_form_id == form_id)).scalar()
                        zendesk_ticket_fields_id = \
                            db_session.execute(
                                select(ZendeskTicketFields.id)
                                .where(ZendeskTicketFields.zendesk_ticket_field_id == ticket_fields_in_form)).scalar()

                        new_ticket_field_in_form = \
                            ZendeskTicketFieldsInForms(zendesk_ticket_forms_id=zendesk_ticket_forms_id,
                                                       zendesk_ticket_fields_id=zendesk_ticket_fields_id,
                                                       )

                        inserted_ticket_fields_in_forms.append(ticket_fields_in_form)
                        db_session.add(new_ticket_field_in_form)
                        db_session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    '''
    Inserção das Opções de Camps ativos no zendesk
    '''
    inserted_ticket_field_options = []

    stmt = select(ZendeskTicketFields.zendesk_ticket_field_id) \
        .join(ZendeskTicketFieldsInForms) \
        .join(ZendeskTicketForms, ZendeskTicketForms.id == ZendeskTicketFieldsInForms.zendesk_ticket_forms_id)
    zendesk_ticket_fields = db_session.execute(stmt)

    for field in zendesk_ticket_fields:
        zendesk_endpoint_url = f'/api/v2/ticket_fields/{field[0]}/options'
        api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

        api_response_code = requests.get(api_url, headers=generate_zendesk_headers())
        api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

        if api_response_code.status_code != 404:
            next_url = api_url
            while next_url:
                for option in api_response['custom_field_options']:
                    stmt = select(ZendeskTicketFieldOptions) \
                        .where(ZendeskTicketFieldOptions.zendesk_ticket_field_option_id == option['id'])
                    with Session(engine) as db_session:
                        query_result = db_session.execute(stmt).first()
                        if not query_result:
                            zendesk_ticket_fields_id = db_session.execute(
                                select(ZendeskTicketFields.id)
                                .where(ZendeskTicketFields.zendesk_ticket_field_id == field[0])).scalar()
                            new_field_option = ZendeskTicketFieldOptions(
                                zendesk_ticket_fields_id=zendesk_ticket_fields_id,
                                zendesk_ticket_field_option_id=option['id'],
                                name=option['name'],
                                value=option['value'],
                                position=option['position'],
                            )
                            inserted_ticket_field_options.append(option['name'])
                            db_session.add(new_field_option)
                            db_session.commit()

                next_url = api_response['next_page']

                if next_url:
                    api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    if inserted_ticket_fields or inserted_ticket_forms or \
            inserted_ticket_fields_in_forms or inserted_ticket_field_options:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                f'Formulários e campos inseridos com sucesso!',
            )
            db_session.commit()
        return redirect(url_for('zendesk_ticket_forms'))
    else:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                f'Não há novos formulários para inserir ou alterar!',
            )
            db_session.commit()
        return redirect(url_for('zendesk_ticket_forms'))


@app.route('/get-zendesk-tags')
@login_required
def get_zendesk_tags():
    zendesk_endpoint_url = '/api/v2/tags.json?page=1'
    api_url = ZENDESK_BASE_URL + zendesk_endpoint_url

    inserted_tags = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for tag in api_response['tags']:
            stmt = select(ZendeskTags).where(ZendeskTags.tag == tag['name'])
            with Session(engine) as db_session:
                query_result = db_session.execute(stmt).first()
                if not query_result:
                    new_tag = ZendeskTags(tag=tag['name'],
                                          )
                    inserted_tags.append(tag['name'])
                    db_session.add(new_tag)
                    db_session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    if inserted_tags:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                f'Tags inseridas: {inserted_tags}',
            )
            db_session.commit()
        return redirect(url_for('zendesk_tags'))
    else:
        user_id = session['_user_id']
        with Session(engine) as db_session:
            Notifications.create_notification(
                db_session,
                user_id,
                1,
                'Não há novas tags para inserir ou alterar!',
            )
            db_session.commit()
        return redirect(url_for('zendesk_tags'))
