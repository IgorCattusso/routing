from models import AssignedTicketsLog
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
#     a = UserBacklog.get_user_backlog(db_session, 13)
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
