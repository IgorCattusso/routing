from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, aliased
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, engine, create_engine, exists
from sqlalchemy.sql import func
import datetime
from config import url_object
from models import *

engine = create_engine(url_object)

session = Session(engine)


# zendesk_endpoint_url = 'api/v2/search.json'
# zendesk_search_query = 'query=type:ticket status:new'
# api_url = API_BASE_URL + zendesk_endpoint_url + "?" + zendesk_search_query
#
# # Autenticação
# concatenate = USERNAME + '/token:' + ZENDESK_API_KEY
#
# concatenate_bytes = concatenate.encode('ascii')
# base64_bytes = base64.b64encode(concatenate_bytes)
# base64_string = base64_bytes.decode('ascii')
#
# # Montando Headers
# headers = {'Authorization': 'Basic ' + base64_string}
#
# # Enviando request e armazenando response em uma variável
# api_response = requests.get(api_url, headers=headers).json()
#
# # print(str(json.dumps(response, sort_keys=False, indent=4, ensure_ascii=False)))
#
# print(api_response)
# print(type(api_response))
#
# results = api_response['results']
# print(results)
# print(type(results))
#
# created_at_formatted = results[1]['created_at'].replace('T', ' ').replace('Z', '')
# print(created_at_formatted)
#
#
#
# api_response_as_str = str(api_response['results']) + ","
# api_response_as_str = api_response_as_str[:-1]
#
# print(type(api_response_as_str))
#
# print("------------------")
# print("Replacing required data...")
# result = api_response_as_str.replace("'", '"')
# result = result.replace("None", '"None"')
# result = result.replace("False", '"False"')
# result = result.replace("True", '"True"')
#
# print("Replacing completed!")
# print("------------------")
# print("Data after replacement: " + result)
# print("------------------")
#
#
#
# zendesk_default_user_group(11490525550747)


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

# zendesk_endpoint_url = '/api/v2/ticket_fields/11490658989083/options'
# api_url = API_BASE_URL + zendesk_endpoint_url
# api_response = requests.get(api_url, headers=generate_zendesk_headers())
# if api_response.status_code == 404:
#     print('test')



# new_route_recipient_type = RouteRecipientType(
#     routes_id=58,
#     recipient_type=0,
# )
#
# exists = session.query(
#     exists().where(RouteRecipientType.routes_id == new_route_recipient_type.routes_id and
#                    RouteRecipientType.recipient_type == new_route_recipient_type.recipient_type)
# ).scalar()
#
# # insert the row if it does not exist
# if exists:
#     print('b')

# data = {
#     'recipient_users': [1, 2, 3, 4, 5],
#     'test': 'test'
# }
#
# data2 = data['recipient_users']
#
# print(data2)
#
# list_of_selected_users = [user for user in data['recipient_users']]


# list_of_recipient_users_in_database = session.execute(
#                         select(RouteRecipientUsers.zendesk_users_id)
#                         .where(RouteRecipientUsers.routes_id==58)
#                     ).all()
# a_list = []
# for user in list_of_recipient_users_in_database:
#     a_list.append(user[0])
# print((a_list))

list_of_recipient_users_in_database = [362, 363, 364]
list_of_received_recipient_users = [362, 363, 364]

print(list(set(list_of_recipient_users_in_database)-set(list_of_received_recipient_users)))