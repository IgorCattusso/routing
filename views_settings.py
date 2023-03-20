from views import *
from helpers import *
from config import *
from app import app
from models import *
from sqlalchemy import create_engine, select, case, desc
from sqlalchemy.orm import Session
from flask import render_template, flash, redirect, url_for
import time

engine = create_engine(url_object)


@app.route('/get-locales')
def get_locales():
    zendesk_endpoint_url = '/api/v2/locales.json?page=1'
    api_url = API_BASE_URL + zendesk_endpoint_url

    inserted_locales = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for locale in api_response['locales']:
            stmt = select(ZendeskLocales).where(ZendeskLocales.zendesk_locale_id == locale['id'])
            with Session(engine) as session:
                query_result = session.execute(stmt).first()
                if not query_result:
                    new_locale = ZendeskLocales(zendesk_locale_id=locale['id'],
                                                locale=locale['locale'],
                                                name=locale['name'],
                                                presentation_name=locale['presentation_name'],
                                                default=match_false_true(locale['default']))
                    inserted_locales.append(locale['locale'])
                    session.add(new_locale)
                    session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    time.sleep(.35)

    if inserted_locales:
        flash(f'Localidades inseridas: {str(inserted_locales)}')
        return redirect(url_for('locales'))
    else:
        flash(f'Nenhuma localidade inserida!')
        return redirect(url_for('locales'))


@app.route('/get-ticket-forms')
def get_ticket_forms():
    """
    Essa rota é um pouco complexa.
    Primeiro, é realizada a inserção dos Campos ativos,
    Em seguida, é realizada a inserção dos Formulários ativos,
    Em seguida, é realizada a inserção do vínculo entre Campos e Formulários, ou seja, quais Campos estão em quais Forms
    Em seguida, é realizada a inserção das Opções dos Campos. As Opções dos Campos estão relacionadas aos Campos,
       mas não necessitam de uma tabela auxiliar para vinculá-las, visto que uma Opção não estará em mais de um Campo
    """
    '''
    Inserção dos Campos ativos no zendesk
    '''
    zendesk_endpoint_url = '/api/v2/ticket_fields.json?page=1&active=true'
    api_url = API_BASE_URL + zendesk_endpoint_url

    inserted_ticket_fields = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for field in api_response['ticket_fields']:
            stmt = select(ZendeskTicketFields).where(ZendeskTicketFields.zendesk_ticket_field_id == field['id'])
            with Session(engine) as session:
                query_result = session.execute(stmt).first()
                if not query_result:
                    new_ticket_field = ZendeskTicketFields(zendesk_ticket_field_id=field['id'],
                                                           title=field['title'],
                                                           type=field['type'])
                    inserted_ticket_fields.append(field['id'])
                    session.add(new_ticket_field)
                    session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    '''
    Inserção dos Formulários ativos no zendesk
    '''
    zendesk_endpoint_url = '/api/v2/ticket_forms.json?page=1&active=true'
    api_url = API_BASE_URL + zendesk_endpoint_url

    inserted_ticket_forms = []

    api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()
    next_url = api_url

    while next_url:
        for form in api_response['ticket_forms']:
            stmt = select(ZendeskTicketForms).where(ZendeskTicketForms.zendesk_ticket_form_id == form['id'])
            with Session(engine) as session:
                query_result = session.execute(stmt).first()
                if not query_result:
                    new_ticket_form = ZendeskTicketForms(zendesk_ticket_form_id=form['id'],
                                                         name=form['name'],
                                                         display_name=form['display_name'],
                                                         default=match_false_true(form['default']))
                    inserted_ticket_forms.append(form['id'])
                    session.add(new_ticket_form)
                    session.commit()

        next_url = api_response['next_page']

        if next_url:
            api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    '''
    Inserção do vínculo de Formulários e Campos de Formulários 
    '''
    zendesk_endpoint_url = '/api/v2/ticket_forms.json?page=1&active=true'
    api_url = API_BASE_URL + zendesk_endpoint_url

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

                with Session(engine) as session:
                    query_result = session.execute(stmt).first()
                    if not query_result:  # TODO: test if the statements below can be made through the query_result var
                        zendesk_ticket_forms_id = \
                            session.execute(
                                select(ZendeskTicketForms.id)
                                .where(ZendeskTicketForms.zendesk_ticket_form_id == form_id)).scalar()
                        zendesk_ticket_fields_id = \
                            session.execute(
                                select(ZendeskTicketFields.id)
                                .where(ZendeskTicketFields.zendesk_ticket_field_id == ticket_fields_in_form)).scalar()

                        new_ticket_field_in_form = \
                            ZendeskTicketFieldsInForms(zendesk_ticket_forms_id=zendesk_ticket_forms_id,
                                                       zendesk_ticket_fields_id=zendesk_ticket_fields_id)

                        inserted_ticket_fields_in_forms.append(ticket_fields_in_form)
                        session.add(new_ticket_field_in_form)
                        session.commit()

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
    zendesk_ticket_fields = session.execute(stmt)

    for field in zendesk_ticket_fields:
        zendesk_endpoint_url = f'/api/v2/ticket_fields/{field[0]}/options'
        api_url = API_BASE_URL + zendesk_endpoint_url

        api_response_code = requests.get(api_url, headers=generate_zendesk_headers())
        api_response = requests.get(api_url, headers=generate_zendesk_headers()).json()

        if api_response_code.status_code != 404:
            next_url = api_url
            while next_url:
                for option in api_response['custom_field_options']:
                    stmt = select(ZendeskTicketFieldOptions) \
                          .where(ZendeskTicketFieldOptions.zendesk_ticket_field_option_id == option['id'])
                    with Session(engine) as session:
                        query_result = session.execute(stmt).first()
                        if not query_result:
                            zendesk_ticket_fields_id = session.execute(
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
                            session.add(new_field_option)
                            session.commit()

                next_url = api_response['next_page']

                if next_url:
                    api_response = requests.get(next_url, headers=generate_zendesk_headers()).json()

    if inserted_ticket_fields or inserted_ticket_forms or \
       inserted_ticket_fields_in_forms or inserted_ticket_field_options:
        flash(f'Ticket Fields inseridos: {str(inserted_ticket_fields)};'
              f'Ticket Forms inseridos: {str(inserted_ticket_forms)};'
              f'Ticket Fields in Forms inseridos: {str(inserted_ticket_fields_in_forms)};'
              f'Ticket Fields in Forms inseridos: {str(inserted_ticket_field_options)}')
        return f'Ticket Fields inseridos: {str(inserted_ticket_fields)}<br>' \
               f'Ticket Forms inseridos: {str(inserted_ticket_forms)}<br>' \
               f'Ticket Fields in forms inseridos: {str(inserted_ticket_fields_in_forms)}<br>' \
               f'Ticket Fields options inseridos: {str(inserted_ticket_field_options)}'  # redirect(url_for('settings'))
    else:
        flash(f'Nenhum inserido!')
        return f'Nenhum inserido!'  # redirect(url_for('settings'))

