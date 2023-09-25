import base64
from app import engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, aliased
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, delete, update, insert, and_, or_
from sqlalchemy.sql import func, alias
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from datetime import datetime, timedelta, date, time
from sqlalchemy import create_engine
from config import url_object, ZENDESK_BASE_URL
import json
import ast
from dotenv import *
import os
from models import GeneralSettings, Users, ZendeskTickets
import requests
from helpers import generate_zendesk_headers
import re

'''
zendesk_endpoint_url = 'api/v2/search.json'
zendesk_search_query = 'query=type:ticket status:new'
api_url = ZENDESK_BASE_URL + zendesk_endpoint_url + "?" + zendesk_search_query

# Autenticação
concatenate = USERNAME + '/token:' + ZENDESK_API_KEY

concatenate_bytes = concatenate.encode('ascii')
base64_bytes = base64.b64encode(concatenate_bytes)
base64_string = base64_bytes.decode('ascii')

# Montando Headers
headers = {'Authorization': 'Basic ' + base64_string}

# Enviando request e armazenando response msg uma variável
api_response = requests.get(api_url, headers=headers).json()

# print(str(json.dumps(response, sort_keys=False, indent=4, ensure_ascii=False)))

print(api_response)
print(type(api_response))

results = api_response['results']
print(results)
print(type(results))

created_at_formatted = results[1]['created_at'].replace('T', ' ').replace('Z', '')
print(created_at_formatted)
'''

'''
api_response_as_str = str(api_response['results']) + ","
api_response_as_str = api_response_as_str[:-1]

print(type(api_response_as_str))

print("------------------")
print("Replacing required data...")
result = api_response_as_str.replace("'", '"')
result = result.replace("None", '"None"')
result = result.replace("False", '"False"')
result = result.replace("True", '"True"')

print("Replacing completed!")
print("------------------")
print("Data after replacement: " + result)
print("------------------")
'''

'''
zendesk_default_user_group(11490525550747)
'''


#
# zendesk_endpoint_url = '/api/v2/group_memberships'
# api_url = ZENDESK_BASE_URL + zendesk_endpoint_url
#
# api_response = requests.get(api_url, headers=generate_zendesk_headers())
#
# data = api_response.json()
#
# results = data['group_memberships']
#
# inserted_users_and_groups = []
#
# for users in results:
#     test = match_false_true(users['default'])
#     print(type(users['default']))

# get_zendesk_users_id('11490525550747')

# stmt = select(ZendeskUsers.id).where(ZendeskUsers.zendesk_user_id == 'null')
# print(str(stmt))
# with Session(engine) as session:
#     db_user_id = session.execute(stmt)
#     a = db_user_id.first()
#     print(a[0])

#

# from models import ZendeskUsers

# def get_zendesk_users_id(user_id):
#     stmt = select(ZendeskUsers.id).where(ZendeskUsers.zendesk_user_id == user_id)
#     with Session(engine) as session:
#         result = session.execute(stmt)
#         for row in result:
#             zendesk_users_id = row
#             # return zendesk_users_id
#             if zendesk_users_id:
#                 return zendesk_users_id[0]
#             else:
#                 return 'null'
#
# print(str(get_zendesk_users_id(11490551144219)))

# list = []
# stmt = select(UserBacklog.ticket_id)
# with Session(engine) as session:
#     a = session.execute(stmt).all()
#     for row in a:
#         list.append(row[0])
#     print(list)

# a = get_ticket_requester_locale(11490553014427)
# print(str(a))

# ,
#
#
# with Session(engine) as session:
#     stmt = select(ZendeskGroups.id, ZendeskGroups.name, func.count(ZendeskGroupMemberships.zendesk_user_id)
#                   .label('count')).join(ZendeskGroupMemberships, isouter=True).group_by(ZendeskGroups.id, ZendeskGroups.name)
#     print(str(stmt))
#     groups = session.execute(stmt).all()
#     for row in groups:
#         print(f'{str(row.id)}, {str(row.name)}, {str(row.count)}')
#


#
# with Session(engine) as session:
#     with session.begin():
#         test = RouteTicketLocales.check_existing(session, 64, 1)
#
# print(test)

# list = [1, 2, 3]
#
# with Session(engine) as session:
#     with session.begin():
#         test = delete(RouteTicketLocales).where(RouteTicketLocales.routes_id == 64).where(RouteTicketLocales.zendesk_locales_id.in_(list))
#         session.execute(test)

# routes_id = 64
# list_of_zendesk_groups_ids = [557, 558, 559, 560]
#
# for group in list_of_zendesk_groups_ids:
#     insert_dict = {'routes_id': routes_id, 'zendesk_groups_id': group}
#
# print(insert_dict)
#
# with Session(engine) as session:
#     try:
#         session.execute(
#             insert(RouteTicketGroups), [
#                 insert_dict
#             ]
#         )
#         session.commit()
#         print('yay')
#     except (IntegrityError, FlushError) as error:
#         error_info = error.orig.args
#         print(f'There was an error: {error_info}')
#
#
# def get_week_day(minutes):
#     days = ['1', '2', '3', '4', '5', '6', '7']
#     day_index = minutes // 1440
#     day = days[day_index % 7]
#     return day
#
#
# def get_hour(minutes):
#     hour = (minutes // 60) % 24
#     minute = minutes % 60
#     hour = f'{hour:02d}:{minute:02d}'
#     return hour
#
#
# def get_starting_hour_column(argument):
#     switcher = {
#         1: "sunday_start",
#         2: "monday_start",
#         3: "tuesday_start",
#         4: "wednesday_start",
#         5: "thursday_start",
#         6: "friday_start",
#         7: "saturday_start",
#     }
#     return switcher.get(argument, "Invalid input")
#
#
# def get_ending_hour_column(argument):
#     switcher = {
#         1: "sunday_end",
#         2: "monday_end",
#         3: "tuesday_end",
#         4: "wednesday_end",
#         5: "thursday_end",
#         6: "friday_end",
#         7: "saturday_end",
#     }
#     return switcher.get(argument, "Invalid input")
#
#
# get_week_day(4800)
# get_hour(4800)
#
# # a = switch_case(int(get_week_day(4800)))
# # print(a)
# # week_day = int(get_week_day(4800))
# # week_day_column = switch_case(week_day)
# # hour = get_hour(4800)
# #
# # print(str(getattr(ZendeskSchedules, week_day_column)))
#
# with Session(engine) as session:
#     week_day = int(get_week_day(4800))
#     week_day_column = switch_case(week_day)
#     hour = get_hour(4800)
#     schedule_id = 1
#
#     session.execute(
#         update(ZendeskSchedules),
#         [
#             {"id": schedule_id, week_day_column: hour}
#         ],
#     )
#
#     session.commit()
#
#
# with Session(engine) as session:
#     ZendeskSchedules.update_day_schedule(session, 1, 4080, 'dasdasdasdas')
#     session.commit()

# with Session(engine) as session:
#     a = ZendeskSchedules.get_schedule(session, 35)
#
#     times_list = []
#
#     for item in a:
#         if type(item) == timedelta:
#             dt = datetime(1, 1, 1, 0, 0) + item
#             times_list.append(dt.strftime("%H:%M:%S"))
#         elif not item:
#             times_list.append(item)
#
#     print(times_list)
#
# with Session(engine) as session:
#     users = User.get_user(session, 'igor.cattusso@involves.com')
#     print(str(users.User.id))
#
# a = User.get_id(1)
# print(a)
#
# b = User.is_authenticated('igor.cattusso@involves.com', 1111)
# print(b)

# with Session(engine) as session:
#     a = ZendeskUsers.get_zendesk_users(session)
#
# for row in a:
#     print(str(row.id))


#
# current_user_position = session.execute(
#     select(UsersQueue.position).where(UsersQueue.users_id == users_id)
# ).scalar()
# print(current_user_position)
#
# current_user_id = session.execute(
#     select(UsersQueue.id).where(UsersQueue.users_id == users_id)
# ).scalar()
# print(current_user_id)
#
# ids_of_positions_to_be_updated = session.execute(
#     select(UsersQueue.id).where(UsersQueue.position > current_user_position)
# ).all()
# print(ids_of_positions_to_be_updated)
#
# for id in ids_of_positions_to_be_updated:
#     print(id)
#     position = session.execute(select(UsersQueue.position).where(UsersQueue.id == id[0])).scalar()
#     session.execute(
#         update(UsersQueue),
#         [
#             {'id': id[0], 'position': position - 1, 'updated_at': datetime.now()}
#         ],
#     )
#     session.commit()
#
# last_position_on_queue = session.execute(
#     select(UsersQueue.position).order_by(UsersQueue.position.desc())
# ).scalar()
#
# print(last_position_on_queue)
#
# print(str(last_position_on_queue) + ' ' + str(current_user_position))
# if last_position_on_queue != current_user_position:
#     session.execute(
#         update(UsersQueue),
#         [
#             {'id': current_user_id, 'position': last_position_on_queue + 1, 'updated_at': datetime.now()}
#         ],
#     )
#     session.commit()

# users_id = 17
#
# with Session(engine) as session:
#     current_user = session.execute(
#         select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).where(UsersQueue.users_id == users_id)
#     ).first()
#     print('current_user: ' + str(current_user))
#
#     if current_user:
#         users_ahead_of_current_user = session.execute(
#             select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).where(UsersQueue.position > current_user.position)
#         ).all()
#         for users in users_ahead_of_current_user:
#             print('users_ahead_of_current_user: ' + str(users.id))
#
#         last_user_in_the_queue = session.execute(
#             select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).order_by(UsersQueue.position.desc())
#         ).first()
#         print('last_user_in_the_queue: ' + str(last_user_in_the_queue.id))
#
#         ''' Get the users ahead of the current users one position down '''
#         for users in users_ahead_of_current_user:
#             session.execute(
#                 update(UsersQueue),
#                 [
#                     {'id': users.id, 'position': users.position - 1, 'updated_at': datetime.now()}
#                 ],
#             )
#             session.commit()
#
#         ''' Get current users to the end of the queue '''
#         if current_user.position != last_user_in_the_queue.position:
#             session.execute(
#                 update(UsersQueue),
#                 [
#                     {'id': current_user.id, 'position': last_user_in_the_queue.position, 'updated_at': datetime.now()}
#                 ],
#             )
#             session.commit()

# with Session(engine) as db_session:
#     UsersQueue.delete_user_from_queue(db_session, 16)
#     db_session.commit()

#
# with Session(engine) as db_session:
#     a = UserBacklog.get_users_backlog(db_session, 13)
#     b = UserBacklog.get_agent_backlog_count(db_session, 13)
#
# print(str(a))
# print(b)
#
# print(datetime.now)

# def test(db_session, users_id):
#     working_hours = db_session.execute(
#         select(
#             Users.zendesk_schedules_id,
#             ZendeskSchedules.saturday_start,
#             ZendeskSchedules.saturday_end,
#         ).where(Users.id == users_id)
#         .join(ZendeskSchedules, Users.zendesk_schedules_id == ZendeskSchedules.id)
#     ).first()
#
#     return working_hours
#
#
# current_time = datetime.now().time()
# midnight_time = datetime.combine(datetime.today(), time.min).time()
#
# delta_time = \
#     datetime.combine(date.today(), current_time) - \
#     datetime.combine(date.today(), midnight_time)
#
# with Session(engine) as db_session:
#     a = AssignedTickets.get_user_assigned_ticket_count_at_today(db_session, 13)
#     b = Users.is_user_on_working_hours(db_session, 13)
#     print(b)
#     #
# a = test(db_session, 13)
# print(a[1])
# print(a[2])
# print(delta_time)
#
# c = a[1] + delta_time
#
# if a[1] <= delta_time <= a[2]:
#     print('a')
# else:
#     print('b')
#
# print(c)

# a = 0
# b = 1
# c = 2
#
# if a == 0 and b == 4 or c == 3:
#     print('hey')
#
# with Session(engine) as db_session:
#     stmt = (
#         select(
#             ZendeskTickets.id,
#             ZendeskTickets.ticket_id,
#             ZendeskTickets.subject,
#             ZendeskTickets.channel,
#             ZendeskTickets.created_at,
#             ZendeskTickets.tag_pais,
#         )
#         .join(AssignedTickets, isouter=True)
#         .where(ZendeskTickets.channel != 'chat')
#         .where(ZendeskTickets.channel != 'whatsapp')
#         .where(ZendeskTickets.channel != 'api')
#         .where(AssignedTickets.zendesk_tickets_id == None)
#         .order_by(ZendeskTickets.id)
#     )
#
#     print(str(stmt))

# zendesk_tickets_id
# users_id
# final_date
# initial_date

# with Session(engine) as db_session:
#     a = AssignedTicketsLog.get_logs(db_session, initial_date='2023-04-30 00:00:00', final_date='2023-04-30 20:56:00')
#     for row in a:
#         print(str(row))
#
# test = "{'queue_id': 32, 'queue_position': 1, 'user_id': 13, 'user_name': 'Igor Cattusso', 'user_active': True, " \
#        "'user_deleted': False, 'user_authenticated': True, 'user_status': 1, 'user_latam': 0, 'ticket_id': 30, " \
#        "'tag_pais': 'pais_brasil', 'message': 'Ticket é Brasil e o usuário está configurado como LATAM NÃO ou AMBOS. " \
#        "O ticket foi atribuído ao usuário. O usuário foi enviado ao final da fila e próximo ticket será distribuído.'}"
#
# # test2 = '{"queue_id": 32, "queue_position": 1, "user_id": 13, "user_name": "Igor Cattusso", "user_active": True, ' \
# #         '"user_deleted": False, "user_authenticated": True, "user_status": 1, "user_latam": 0, "ticket_id": 30, ' \
# #         '"tag_pais": "pais_brasil", "message": "Ticket é Brasil e o usuário está configurado como LATAM NÃO ou AMBOS. ' \
# #         'O ticket foi atribuído ao usuário. O usuário foi enviado ao final da fila e próximo ticket será distribuído."}'
#
# print(test)
# print(type(test))
#
#
# # result = json.loads(test2)
#
# result = ast.literal_eval(test)
#
# print(type(result))
# print(result)

# with Session(engine) as db_session:
#        a = AssignedTicketsLog.get_last_ten_logs(db_session)
#
# for b in a:
#        print(str(b))


# from dotenv import load_dotenv
# import os
# from email.message import EmailMessage
# from email.headerregistry import Address
# import ssl
# import smtplib
# from email.utils import make_msgid
#
# load_dotenv()
#
# email_sender = str(os.getenv('GMAIL_ACCOUNT_EMAIL'))
# email_password = str(os.getenv('GMAIL_APP_PASSWORD'))
# email_recipient = 'igor.cattusso@involves.com'
#
# subject = 'Definição de nova senha'
# body = """
# Segue link para redefinição de senha: aaa.aaa.com
# """
#
# asparagus_cid = make_msgid()
#
# msg = EmailMessage()
# msg['From'] = Address('Zendesk Routing', domain=email_sender)
# msg['To'] = email_recipient
# msg['Subject'] = subject
# msg.set_content(body)
#
# msg.add_alternative("""\
# <html lang="pt_BR">
#     <head>
#         <title>Redefinição de senha</title>
#     </head>
#     <body style="background-color:#040C26;padding:50px;text-align:center;font-family:Arial,Helvetica,sans-serif;font-size:14px">
#         <div style="background-color:white;padding:50px;text-align:left;width:20%;margin:auto;border-radius:30px">
#             <div style="text-align:center">
#                 <img src="cid:{asparagus_cid}" />
#             </div>
#             <br>
#             <div style="text-align:center">
#                 <h2>Olá, {user_name}!</h2>
#                 <br>
#                 <p>Segue o link para redefinição da sua senha 🤘</p>
#             </div>
#             <br>
#             <div style="text-align:center;margin-top:50px">
#                 <a href="{password_reset_link}" class="link"><button style="padding:20px 60px;border-radius:40px;border:none;cursor:pointer;background-color:#040C26;color:white;font-weight:bold;font-size:16px">Redefinir senha</button></a>
#             </div>
#         </div>
#     </body>
# </html>
# """.format(asparagus_cid=asparagus_cid[1:-1], user_name='Igor Cattusso', password_reset_link=''), subtype='html')
#
# with open("static/img/favicon.png", 'rb') as img:
#     msg.get_payload()[1].add_related(img.read(), 'image', 'png', cid=asparagus_cid)
#
# context = ssl.create_default_context()
#
# with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
#     smtp.login(email_sender, email_password)
#     smtp.send_message(msg)

# with Session(engine) as db_session:
#     test = GeneralSettings.is_currently_hour_working_hours(db_session)
#     teste = Users.is_user_on_working_hours(db_session, 13)
#
# print(test)
# print(teste)

# def teste1():
#     with Session(engine) as db_session:
#         new_ticket = ZendeskTickets(
#             ticket_id=76,
#             ticket_subject='Conversa com Web User 6ee012033ccfa8dffccf31e4',
#             ticket_channel='Web',
#             ticket_tags=bytes('always_unbabel team_automatico testetag ticket_publico', 'utf-8'),
#         )
#         db_session.add(new_ticket)
#
#         teste2()
#
#         db_session.commit()
#
#
# def teste2():
#     with Session(engine) as db_session:
#         new_ticket = ZendeskTickets(
#             ticket_id=77,
#             ticket_subject='Conversa com Web User 6ee012033ccfa8dffccf31e4',
#             ticket_channel='Web',
#             ticket_tags=bytes('always_unbabel team_automatico testetag ticket_publico', 'utf-8'),
#         )
#
#         db_session.add(new_ticket)
#         db_session.commit()
#
#
# teste1()


# national_ticket_tags = ['pais_brasil', 'pais_franca']
# ticket_tags = "agente_light enterprise indústria pais_franca produto_ri " \
#               "motivo_ajuda_nao_consigo_acessar_uma_funcionalidade_mas_consigo_manter_o_fluxo_das_atividades " \
#               "com_fit tier_1 contrato_ativo"
# ticket_tags_list = ticket_tags.split()
#
# print(set(ticket_tags))
# print(set(national_ticket_tags))
#
# if 'pais_' in ticket_tags:
#     print('Hey-oh')
#
# if any(tag in national_ticket_tags for tag in ticket_tags):
#     print('Hey')


# def zendesk_assign_ticket_test(ticket_id, zendesk_user_id):
#     zendesk_endpoint_url = f'/api/v2/tickets/{ticket_id}'
#     api_url = ZENDESK_BASE_URL + zendesk_endpoint_url
#
#     assign_ticket_json = \
#         {
#             "ticket": {
#                 "status": "open",
#                 "assignee_id": zendesk_user_id
#             }
#         }
#
#     request_json = assign_ticket_json
#     api_response = requests.put(api_url, json=request_json, headers=generate_zendesk_headers())
#
#     # print(f'api_response.apparent_encoding: {api_response.apparent_encoding}')
#     # print(f'api_response.content: {api_response.content}')
#     # print(f'api_response.cookies: {api_response.cookies}')
#     # print(f'api_response.elapsed: {api_response.elapsed}')
#     # print(f'api_response.encoding: {api_response.encoding}')
#     # print(f'api_response.headers: {api_response.headers}')
#     # print(f'api_response.history: {api_response.history}')
#     # print(f'api_response.is_permanent_redirect: {api_response.is_permanent_redirect}')
#     # print(f'api_response.json(): {api_response.json()}')
#     # print(f'api_response.links: {api_response.links}')
#     # print(f'api_response.next: {api_response.next}')
#     # print(f'api_response.ok: {api_response.ok}')
#     # print(f'api_response.raise_for_status(): {api_response.raise_for_status()}')
#     # print(f'api_response.reason: {api_response.reason}')
#     # print(f'api_response.request: {api_response.request}')
#     # print(f'api_response.status_code: {api_response.status_code}')
#     # print(f'api_response.text: {api_response.text}')
#     # print(f'api_response.url: {api_response.url}')
#
#     return str(api_response.status_code) + ' ' + str(api_response.reason) + ' - ' + str(api_response.text)
#
# api_return = zendesk_assign_ticket_test(99, 11490525550747)
#
# print(api_return)
#

# def get_webhook_invocation_attempts():
#     webhook_id = '01H2Y133W3QNZVMBYFVW8H9MQT'
#     api_url = f'https://agilepromoter.zendesk.com/api/v2/webhooks/{webhook_id}/invocations'
#
#     zendesk_api_key = 'm5NAEH0rYvhBSdttLTNgdpB2t6BriAxRJMG6Nyj4' # token revogado
#     concatenate = 'igor.cattusso@involves.com' + '/token:' + zendesk_api_key
#     concatenate_bytes = concatenate.encode('ascii')
#     base64_bytes = base64.b64encode(concatenate_bytes)
#     base64_string = base64_bytes.decode('ascii')
#     headers = {'Authorization': 'Basic ' + base64_string}
#
#     api_response = requests.get(api_url, headers=headers).json()
#
#     next_url = api_url
#
#     all_requests = []
#
#     while_counter = 0
#     for_counter = 0
#
#     while next_url:
#         print(f'Beginning of While {while_counter}')
#         while_counter += 1
#         api_response = requests.get(next_url, headers=headers).json()
#         for invocation in api_response['invocations']:
#             print(f'Beginning of For {for_counter}')
#             invocation_url = f'https://agilepromoter.zendesk.com/api/v2/webhooks/{webhook_id}/invocations/{invocation["id"]}/attempts'
#             invocation_api_response = requests.get(invocation_url, headers=headers).json()
#             all_requests.append(invocation_api_response['attempts'][0]['request']['payload'])
#             print(f'End of For {for_counter}')
#             for_counter += 1
#
#         if api_response['meta']['has_more']:
#             next_url = api_response['links']['next']
#         else:
#             next_url = False
#
#         print(f'End of While {while_counter}')
#         print(next_url)
#         for_counter = 0
#
#     print(all_requests)
#
#
# # get_webhook_invocation_attempts()
#
# ticket = {
#     "ticket_id": "114398",
#     "ticket_subject": "Promotora bloqueada no Involves",
#     "ticket_channel": "E-mail",
#     "ticket_tags": "advanced alimentos alimentos__bebidas bebidas com_fit contrato_ativo indústria pais_brasil "
#                    "plantao_nao prospect rock_stars team_automatico ticket_publico tier_0"
# }
#
# json_string = str(ticket)
#
# # Define a regular expression pattern to match the double quotes within "ticket_subject"
# pattern = r'"([^"]*)"'
#
# # Replace the double quotes with single quotes within the "ticket_subject" value using the regular expression
# json_string_fixed = re.sub(pattern, r"'\1'", json_string)
#
# # Parse the fixed JSON
# data = json.loads(json_string_fixed)
#
# # Access the ticket_subject value
# ticket_subject = data['ticket_subject']
#
# print(ticket_subject)

tickets = [
    {
        "ticket_id": "113",
        "ticket_subject": "Reportar pesquisa",
        "ticket_channel": "Web Widget",
        "ticket_tags": "advanced agência contrato_ativo motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_involves_stage team_automatico ticket_publico tier_6 web_widget"
    },
    {
        "ticket_id": "112",
        "ticket_subject": "Promotora bloqueada no Involves",
        "ticket_channel": "E-mail",
        "ticket_tags": "advanced alimentos alimentos__bebidas bebidas com_fit contrato_ativo indústria pais_brasil plantao_nao prospect rock_stars team_automatico ticket_publico tier_0"
    },
    {
        "ticket_id": "110",
        "ticket_subject": "Atualização Web e Mobile",
        "ticket_channel": "Formulário web",
        "ticket_tags": "admitido advanced area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_solicitacao cliente com_fit contrato_ativo cuidados_pessoais indústria lider_de_projeto modulo_processo_de_atualizacao_agendamento/atualizacao_em_massa_funcao_atualizacao_web___mobile motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao plataforma_web português produto_involves_stage team_backstage ticket_publico tier_6"
    },
    {
        "ticket_id": "109",
        "ticket_subject": "Atualização",
        "ticket_channel": "Formulário web",
        "ticket_tags": "agência area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_solicitacao com_fit contrato_ativo essential modulo_processo_de_atualizacao_agendamento/atualizacao_em_massa_funcao_atualizacao_web motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao plataforma_web produto_involves_stage team_backstage ticket_publico tier_6"
    },
    {
        "ticket_id": "108",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_involves_stage ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "107",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "106",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_involves_stage ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "105",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "104",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "103",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "102",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "101",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "100",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "99",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "98",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_agrupamento_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "97",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_involves_stage ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "96",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "94",
        "ticket_subject": "Atualização",
        "ticket_channel": "Formulário web",
        "ticket_tags": "agente_light com_fit contrato_ativo enterprise explore indústria motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri rock_stars team_automatico tier_1 usuario_involves"
    },
    {
        "ticket_id": "93",
        "ticket_subject": "Atualização do sistema",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_solicitacao com_fit contrato_ativo indústria modulo_processo_de_atualizacao_agendamento/atualizacao_em_massa_funcao_atualizacao_web___mobile motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao plataforma_web produto_involves_stage team_backstage ticket_publico tier_6"
    },
    {
        "ticket_id": "92",
        "ticket_subject": "Conversa com Guilherme Riguetto Rodrigues",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo pais_brasil plantao_nao team_automatico ticket_chat tier_1 zopim_chat"
    },
    {
        "ticket_id": "91",
        "ticket_subject": "Atualização",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced alimentos__bebidas area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_solicitacao cliente com_fit contrato_ativo distribuidor modulo_processo_de_atualizacao_agendamento/atualizacao_em_massa_funcao_atualizacao_web___mobile motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao plataforma_web produto_involves_stage team_backstage ticket_publico tier_1"
    },
    {
        "ticket_id": "90",
        "ticket_subject": "Lojas sem informação de sortimento no BI de VPL",
        "ticket_channel": "E-mail",
        "ticket_tags": "advanced alimentos alimentos__bebidas bebidas com_fit contrato_ativo indústria pais_brasil plantao_nao prospect rock_stars team_automatico tier_0"
    },
    {
        "ticket_id": "88",
        "ticket_subject": "Conversa com Andreia Cristina",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced cliente com_fit contrato_ativo indústria pais_brasil plantao_nao team_automatico ticket_chat tier_3 utensílios_domésticos zopim_chat"
    },
    {
        "ticket_id": "87",
        "ticket_subject": "Reprocessamento LP",
        "ticket_channel": "Formulário web",
        "ticket_tags": "agente_light com_fit contrato_ativo enterprise indústria motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_involves_stage team_automatico tier_1 usuario_involves"
    },
    {
        "ticket_id": "86",
        "ticket_subject": "Ticket interno - MP COlgate MX",
        "ticket_channel": "Formulario web",
        "ticket_tags": "agente_light agência always_unbabel baixo_fit contrato_ativo enterprise motivo_ajuda_nao_consigo_acessar_uma_funcionalidade_mas_consigo_manter_o_fluxo_das_atividades pais_mexico plantao_nao produto_ri team_automatico tier_2 usuario_involves"
    },
    {
        "ticket_id": "85",
        "ticket_subject": "Conversa com Andreia Cristina",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced cliente com_fit contrato_ativo indústria pais_brasil plantao_nao team_automatico ticket_chat tier_3 utensílios_domésticos zopim_chat"
    },
    {
        "ticket_id": "84",
        "ticket_subject": "Conversa com Lucas Cabral",
        "ticket_channel": "Chat",
        "ticket_tags": "cliente com_fit contrato_ativo enterprise indústria pais_brasil pet_care plantao_nao team_automatico ticket_chat tier_4 zopim_chat"
    },
    {
        "ticket_id": "85",
        "ticket_subject": "Tarea de mantenida 2 aparece un día antes",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced com_fit contrato_ativo indústria motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_mexico plantao_nao produto_involves_stage team_automatico ticket_publico tier_2"
    },
    {
        "ticket_id": "84",
        "ticket_subject": "Reportar Atendimento Avulso e Questões de chamados",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria baixo_fit contrato_ativo motivo_ajuda_nao_consigo_acessar_uma_funcionalidade_mas_consigo_manter_o_fluxo_das_atividades pais_brasil parceiro plantao_nao produto_involves_stage team_automatico ticket_publico tier_5"
    },
    {
        "ticket_id": "83",
        "ticket_subject": "Formulários Inativos aparecendo para consultores",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced baixo_fit contrato_ativo indústria motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_involves_stage team_automatico ticket_publico tier_3"
    },
    {
        "ticket_id": "83",
        "ticket_subject": "Johnson - Pergunta Informativa permitindo resposta do promotor",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_involves_stage team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "82",
        "ticket_subject": "Conversa com Lucas Cabral",
        "ticket_channel": "Chat",
        "ticket_tags": "cliente com_fit contrato_ativo enterprise indústria pais_brasil pet_care plantao_nao team_automatico ticket_chat tier_4 zopim_chat"
    },
    {
        "ticket_id": "81",
        "ticket_subject": "IDs respostas de pesquisas Involves Web x Qlik Sense",
        "ticket_channel": "E-mail",
        "ticket_tags": "advanced cliente com_fit contrato_ativo indústria materiais_para_construção_e_acabamento pais_brasil plantao_nao team_automatico ticket_publico tier_4"
    },
    {
        "ticket_id": "80",
        "ticket_subject": "Promotora não consegue preencher a pesquisa",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_involves_stage team_automatico ticket_publico tier_4"
    },
    {
        "ticket_id": "79",
        "ticket_subject": "Conversa com Giovanna Tagliari",
        "ticket_channel": "Chat",
        "ticket_tags": "contrato_ativo mdm_redirect pais_brasil plantao_nao team_automatico ticket_chat tier_involves zopim_chat"
    },
    {
        "ticket_id": "78",
        "ticket_subject": "Conversa com Lucas Cabral",
        "ticket_channel": "Chat",
        "ticket_tags": "cliente com_fit contrato_ativo enterprise indústria pais_brasil pet_care plantao_nao team_automatico ticket_chat tier_4 zopim_chat"
    },
    {
        "ticket_id": "77",
        "ticket_subject": "Erros Involves",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria baixo_fit cliente inativo motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_involves_stage team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "76",
        "ticket_subject": "Conversa com Carolina Mesquita de Mello",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced automotivo_/_autopeças baixo_fit cliente contrato_ativo indústria pais_brasil plantao_nao team_automatico ticket_chat tier_5 zopim_chat"
    },
    {
        "ticket_id": "75",
        "ticket_subject": "Atendimento Chatbot",
        "ticket_channel": "Serviço Web",
        "ticket_tags": "advanced area_chatbot atendimento_chatbot atendimento_relacionado_produto_nao baixo_fit causa_raiz_chatbot-usuario_sem_acesso cesta_higiene chat_app cliente cliente_sem_acesso_wpp contrato_ativo indústria pais_brasil plantao_nao team_automatico ticket_publico tier_1 ubots"
    },
    {
        "ticket_id": "73",
        "ticket_subject": "Atualização involves",
        "ticket_channel": "Formulário web",
        "ticket_tags": "motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao plantao_nao produto_involves_stage team_automatico ticket_publico"
    },
    {
        "ticket_id": "72",
        "ticket_subject": "Conversa com Zair Perroni",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced baixo_fit cesta_higiene cliente contrato_ativo indústria pais_brasil plantao_nao team_automatico ticket_chat tier_1 zopim_chat"
    },
    {
        "ticket_id": "71",
        "ticket_subject": "Conversa com Lucas Cabral",
        "ticket_channel": "Chat",
        "ticket_tags": "cliente com_fit contrato_ativo enterprise indústria pais_brasil pet_care plantao_nao team_automatico ticket_chat tier_4 zopim_chat"
    },
    {
        "ticket_id": "70",
        "ticket_subject": "Conversa com Marcelo Frazão",
        "ticket_channel": "Chat",
        "ticket_tags": "agente_light contrato_ativo fit_involves involves organização_involves pais_brasil parceiro plantao_nao ramo_negocio_involves software team_automatico ticket_chat tier_involves zopim_chat"
    },
    {
        "ticket_id": "69",
        "ticket_subject": "Conversa com Emanuelly Evellyn de Oliveira",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced agência contrato_ativo pais_brasil plantao_nao team_automatico ticket_chat tier_4 zopim_chat"
    },
    {
        "ticket_id": "68",
        "ticket_subject": "Conversa com leonardo",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced com_fit contrato_ativo distribuidor pais_brasil plantao_nao team_automatico ticket_chat tier_6 zopim_chat"
    },
    {
        "ticket_id": "67",
        "ticket_subject": "Conversa com Leandro Florentino De Andrade",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced alimentos alimentos__bebidas bebidas cliente com_fit contrato_ativo distribuidor pais_brasil plantao_nao team_automatico ticket_chat tier_6 zopim_chat"
    },
    {
        "ticket_id": "65",
        "ticket_subject": "Conversa com Carolina Mesquita de Mello",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced automotivo_/_autopeças baixo_fit cliente contrato_ativo indústria pais_brasil plantao_nao team_automatico ticket_chat tier_5 zopim_chat"
    },
    {
        "ticket_id": "64",
        "ticket_subject": "Conversa com Paulo Henrique",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo pais_brasil plantao_nao team_automatico ticket_chat tier_1 zopim_chat"
    },
    {
        "ticket_id": "63",
        "ticket_subject": "Inativação Justificativas de visitas - WEB",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced alimentos__bebidas cliente com_fit contrato_ativo indústria motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_involves_stage team_automatico ticket_publico tier_6"
    },
    {
        "ticket_id": "62",
        "ticket_subject": "DESLIGAMENTO SISTEMA - PROMOTOR CLT",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced com_fit contrato_ativo indústria motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_involves_stage rock_stars team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "61",
        "ticket_subject": "Conversa com Lays",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced agência com_fit contrato_ativo pais_brasil plantao_nao team_automatico ticket_chat tier_4 zopim_chat"
    },
    {
        "ticket_id": "60",
        "ticket_subject": "RES: [102681] Re: CNPJ - Importação de pontos de venda",
        "ticket_channel": "Ticket fechado",
        "ticket_tags": "advanced alimentos__bebidas area_suporte causa_raiz_duvida cliente com_fit contrato_ativo distribuidor f_funcao_importacoes i_modulo_cadastro_de_pontos_de_venda motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao plataforma_web produto_involves_stage team_automatico ticket_publico tier_6 tier_8"
    },
    {
        "ticket_id": "59",
        "ticket_subject": "Conversa com Luan Santos",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced alimentos__bebidas cliente com_fit contrato_ativo distribuidor pais_brasil plantao_nao team_automatico ticket_chat tier_6 zopim_chat"
    },
    {
        "ticket_id": "58",
        "ticket_subject": "MUDANÇA DE ROTEIRO",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced com_fit contrato_ativo indústria motivo_ajuda_nao_consigo_acessar_meu_sistema_indisponibilidade_geral pais_brasil plantao_nao produto_involves_stage team_automatico ticket_publico tier_3"
    },
    {
        "ticket_id": "57",
        "ticket_subject": "Conversa com Suporte Repor Brasil",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced agência baixo_fit contrato_ativo pais_brasil plantao_nao team_automatico ticket_chat tier_3 zopim_chat"
    },
    {
        "ticket_id": "56",
        "ticket_subject": "Cancelar: Atualização Mês Junho - Painel Presença",
        "ticket_channel": "E-mail",
        "ticket_tags": "advanced cesta_higiene cliente com_fit contrato_ativo cosméticos indústria pais_brasil plantao_nao team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "55",
        "ticket_subject": "Cancelar: Atualização Mês Junho - Painel Presença",
        "ticket_channel": "E-mail",
        "ticket_tags": "advanced cesta_higiene cliente com_fit contrato_ativo cosméticos indústria pais_brasil plantao_nao team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "54",
        "ticket_subject": "Atualização Mês Junho - Painel Presença",
        "ticket_channel": "E-mail",
        "ticket_tags": "advanced cesta_higiene cliente com_fit contrato_ativo cosméticos indústria pais_brasil plantao_nao team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "53",
        "ticket_subject": "Problemas con validación de fotos en la app Cámara.",
        "ticket_channel": "Formulario web",
        "ticket_tags": "agente_light always_unbabel contrato_ativo espanhol fit_involves motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_mexico plantao_nao produto_ri ramo_negocio_involves team_automatico tier_involves usuario_involves"
    },
    {
        "ticket_id": "52",
        "ticket_subject": "Pesquisa ri",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced cesta_higiene cliente com_fit contrato_ativo cosméticos indústria motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_involves_stage team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "51",
        "ticket_subject": "Conversa com Jhoselin Guzman",
        "ticket_channel": "Chat",
        "ticket_tags": "always_unbabel consultoria contrato_ativo enterprise pais_bolivia plantao_nao team_automatico ticket_chat tier_1 zopim_chat"
    },
    {
        "ticket_id": "50",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "49",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "48",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "47",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "46",
        "ticket_subject": "Dúvida sobre pesquisa manual (Ausência de pesquina no painel)",
        "ticket_channel": "E-mail",
        "ticket_tags": "advanced cesta_higiene cliente com_fit contrato_ativo cosméticos indústria pais_brasil plantao_nao team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "45",
        "ticket_subject": "DIVERGENCIAS EM RECONHECIMENTO DE IMAGEM | CARGILL",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_ri team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "44",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "43",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "42",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "41",
        "ticket_subject": "DIVERGENCIAS EM RECONHECIMENTO DE IMAGEM | CARGILL",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_ri team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "40",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao plataforma_web produto_ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "38",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "37",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "35",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "34",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao plataforma_web produto_ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "33",
        "ticket_subject": "Conversa com Caio Leite - Grupo Tagg.",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo pais_brasil plantao_nao team_automatico ticket_chat tier_2 zopim_chat"
    },
    {
        "ticket_id": "32",
        "ticket_subject": "Problemas con la aplicación móvil",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced com_fit contrato_ativo indústria motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_bolivia plantao_nao produto_ri team_automatico ticket_publico tier_2"
    },
    {
        "ticket_id": "31",
        "ticket_subject": "DIVERGENCIAS EM RECONHECIMENTO DE IMAGEM | CARGILL",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_ri team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "30",
        "ticket_subject": "Conversa com Caio Leite - Grupo Tagg.",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo pais_brasil plantao_nao team_automatico ticket_chat tier_2 zopim_chat"
    },
    {
        "ticket_id": "29",
        "ticket_subject": "Planograma - Extrato",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced com_fit contrato_ativo indústria motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_ri rock_stars team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "28",
        "ticket_subject": "Conversa com Amanda Neves",
        "ticket_channel": "Chat",
        "ticket_tags": "agente_light contrato_ativo mdm_redirect pais_brasil plantao_nao team_automatico ticket_chat tier_involves usuario_involves zopim_chat"
    },
    {
        "ticket_id": "27",
        "ticket_subject": "DIVERGENCIAS EM RECONHECIMENTO DE IMAGEM | CARGILL",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_ri team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "26",
        "ticket_subject": "DIVERGENCIAS EM RECONHECIMENTO DE IMAGEM | CARGILL",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_ri team_automatico ticket_publico tier_1"
    },
    {
        "ticket_id": "25",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "24",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "23",
        "ticket_subject": "NESTLÉ PA - PILOTO RI",
        "ticket_channel": "Formulario web",
        "ticket_tags": "agente_light always_unbabel contrato_ativo mdm_redirect motivo_ajuda_tenho_duvidas_sobre_os_meus_dados pais_brasil plantao_nao produto_bi_intelligence team_automatico tier_involves"
    },
    {
        "ticket_id": "22",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "21",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema contestacao_jnj modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade plantao_nao produto_ri ri team_reconhecimento_por_imagem_data_quality ticket_publico"
    },
    {
        "ticket_id": "20",
        "ticket_subject": "Erro na substituição do template granado.",
        "ticket_channel": "Ticket fechado",
        "ticket_tags": "area_suporte causa_raiz_duvida com_fit contrato_ativo enterprise indústria modulo_painel_de_pesquisas_funcao_cadastro/edicao/exclusao motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao plataforma_web produto_involves_stage team_encore ticket_publico tier_5"
    },
    {
        "ticket_id": "19",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema contestacao_jnj modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade plantao_nao produto_ri ri team_reconhecimento_por_imagem_data_quality ticket_publico"
    },
    {
        "ticket_id": "18",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema contestacao_jnj modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade plantao_nao produto_ri ri team_reconhecimento_por_imagem_data_quality ticket_publico"
    },
    {
        "ticket_id": "17",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema contestacao_jnj modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade plantao_nao produto_ri ri team_reconhecimento_por_imagem_data_quality ticket_publico"
    },
    {
        "ticket_id": "16",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "15",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "14",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "13",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao plataforma_web produto_involves_stage rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "10",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "9",
        "ticket_subject": "Problema integração AFD - embelleze",
        "ticket_channel": "Formulário web",
        "ticket_tags": "contrato_ativo mdm_redirect motivo_ajuda_nao_consigo_acessar_meu_sistema_indisponibilidade_geral pais_brasil plantao_nao produto_involves_stage team_automatico tier_involves usuario_involves"
    },
    {
        "ticket_id": "7",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "6",
        "ticket_subject": "Reprocessamento RI > Cargil (20/06)",
        "ticket_channel": "Formulário web",
        "ticket_tags": "agente_light contrato_ativo fit_involves involves motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao organização_involves pais_brasil parceiro plantao_nao produto_ri ramo_negocio_involves software team_automatico tier_involves"
    },
    {
        "ticket_id": "4",
        "ticket_subject": "[Contestação J&J]",
        "ticket_channel": "Formulário web",
        "ticket_tags": "area_suporte atendimento_n1_n2 c_jnj_nao causa_raiz_problema com_fit contestacao_jnj contrato_ativo enterprise indústria modulo_ia_-_homologacao_funcao_identificacao_de_produtos motivo_ajuda_tenho_duvidas_sobre_uma_funcionalidade pais_brasil plantao_nao produto_ri ri rock_stars team_reconhecimento_por_imagem_data_quality ticket_publico tier_1"
    },
    {
        "ticket_id": "2",
        "ticket_subject": "Conversa com Liliane Cruz",
        "ticket_channel": "Chat",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo pais_brasil plantao_nao team_automatico ticket_chat tier_4 zopim_chat"
    },
    {
        "ticket_id": "1",
        "ticket_subject": "SuperCategorias Cargill",
        "ticket_channel": "Formulário web",
        "ticket_tags": "advanced agência agências_e_consultoria cliente com_fit contrato_ativo motivo_ajuda_um_comportamento_do_sistema_esta_impedindo_a_rotina_da_minha_operacao pais_brasil plantao_nao produto_involves_stage team_automatico ticket_publico tier_1"
    }
]

for ticket in tickets:
    api_response = requests.post('http://127.0.0.1:5000/request-ticket-assignment', json=ticket)


# test
