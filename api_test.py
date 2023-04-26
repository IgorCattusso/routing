from models import Users, ZendeskUsers, UsersQueue
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, delete, update, insert
import datetime
from sqlalchemy import create_engine
from config import url_object
from datetime import datetime

engine = create_engine(url_object)


'''
zendesk_endpoint_url = 'api/v2/search.json'
zendesk_search_query = 'query=type:ticket status:new'
api_url = API_BASE_URL + zendesk_endpoint_url + "?" + zendesk_search_query

# Autenticação
concatenate = USERNAME + '/token:' + ZENDESK_API_KEY

concatenate_bytes = concatenate.encode('ascii')
base64_bytes = base64.b64encode(concatenate_bytes)
base64_string = base64_bytes.decode('ascii')

# Montando Headers
headers = {'Authorization': 'Basic ' + base64_string}

# Enviando request e armazenando response em uma variável
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
# api_url = API_BASE_URL + zendesk_endpoint_url
#
# api_response = requests.get(api_url, headers=generate_zendesk_headers())
#
# data = api_response.json()
#
# results = data['group_memberships']
#
# inserted_users_and_groups = []
#
# for user in results:
#     test = match_false_true(user['default'])
#     print(type(user['default']))

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
# stmt = select(ZendeskUserBacklog.ticket_id)
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
#     user = User.get_user(session, 'igor.cattusso@involves.com')
#     print(str(user.User.id))
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
#         for user in users_ahead_of_current_user:
#             print('users_ahead_of_current_user: ' + str(user.id))
#
#         last_user_in_the_queue = session.execute(
#             select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).order_by(UsersQueue.position.desc())
#         ).first()
#         print('last_user_in_the_queue: ' + str(last_user_in_the_queue.id))
#
#         ''' Get the users ahead of the current user one position down '''
#         for user in users_ahead_of_current_user:
#             session.execute(
#                 update(UsersQueue),
#                 [
#                     {'id': user.id, 'position': user.position - 1, 'updated_at': datetime.now()}
#                 ],
#             )
#             session.commit()
#
#         ''' Get current user to the end of the queue '''
#         if current_user.position != last_user_in_the_queue.position:
#             session.execute(
#                 update(UsersQueue),
#                 [
#                     {'id': current_user.id, 'position': last_user_in_the_queue.position, 'updated_at': datetime.now()}
#                 ],
#             )
#             session.commit()
