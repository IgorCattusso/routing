from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, delete, update, insert, and_, or_, case, Column, \
    JSON
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.dialects.mysql import DATETIME
from datetime import datetime, timedelta, date, time
from sqlalchemy import create_engine
from config import url_object, ZENDESK_BASE_URL
import uuid
from app import bcrypt
import random
import string

engine = create_engine(url_object)


class Base(DeclarativeBase):
    pass


class ZendeskTickets(Base):
    __tablename__ = "zendesk_tickets"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(nullable=False)
    ticket_subject: Mapped[str] = mapped_column(String(150), nullable=False)
    ticket_channel: Mapped[str] = mapped_column(String(150), nullable=False)
    ticket_tags: Mapped[str] = mapped_column(String(21385))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f'{self.id}, {self.ticket_id}, {self.ticket_subject}, {self.ticket_channel}, {self.received_at}'

    @staticmethod
    def get_next_ticket_to_be_assigned(db_session):
        try:
            next_ticket = db_session.execute(
                select(
                    ZendeskTickets.id,
                    ZendeskTickets.ticket_id,
                    ZendeskTickets.ticket_subject,
                    ZendeskTickets.ticket_channel,
                    ZendeskTickets.received_at,
                    ZendeskTickets.ticket_tags,
                )
                .join(AssignedTickets, isouter=True)
                .where(ZendeskTickets.ticket_channel != 'chat')
                .where(ZendeskTickets.ticket_channel != 'whatsapp')
                .where(ZendeskTickets.ticket_channel != 'api')
                .where(AssignedTickets.zendesk_tickets_id == None)
                .order_by(ZendeskTickets.id)
            ).first()
            if next_ticket:
                return next_ticket
            else:
                return None

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_new_ticket(db_session, ticket):
        try:
            new_ticket = db_session.add(ticket)
            return new_ticket

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_ticket_by_ticket_id(db_session, ticket_id):
        try:
            ticket = db_session.execute(
                select(
                    ZendeskTickets.id,
                    ZendeskTickets.ticket_id,
                    ZendeskTickets.ticket_subject,
                    ZendeskTickets.ticket_channel,
                    ZendeskTickets.ticket_tags,
                    ZendeskTickets.received_at,
                ).where(ZendeskTickets.ticket_id == ticket_id)
            ).first()
            if ticket:
                return ticket
            else:
                return None

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_ticket_by_id(db_session, zendesk_tickets_id):
        try:
            ticket = db_session.execute(
                select(
                    ZendeskTickets.id,
                    ZendeskTickets.ticket_id,
                    ZendeskTickets.ticket_subject,
                    ZendeskTickets.ticket_channel,
                    ZendeskTickets.ticket_tags,
                    ZendeskTickets.received_at,
                ).where(ZendeskTickets.id == zendesk_tickets_id)
            ).first()
            if ticket:
                return ticket
            else:
                return None

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class ZendeskUsers(Base):
    __tablename__ = "zendesk_users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_user_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    suspended: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_user_id}, {self.name}, {self.email}, {self.suspended}'

    @staticmethod
    def get_zendesk_users_id(db_session, zendesk_user_id):
        try:
            zendesk_users_id = db_session.execute(
                select(ZendeskUsers.id).where(ZendeskUsers.zendesk_user_id == zendesk_user_id)
            ).scalar()
            return zendesk_users_id

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_zendesk_users(db_session):
        try:
            all_users = db_session.execute(
                select(
                    ZendeskUsers.id,
                    ZendeskUsers.zendesk_user_id,
                    ZendeskUsers.name,
                    ZendeskUsers.email,
                    ZendeskUsers.suspended,
                )
            ).all()
            return all_users

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_valid_zendesk_users(db_session):
        try:
            all_users = db_session.execute(
                select(
                    ZendeskUsers.id,
                    ZendeskUsers.zendesk_user_id,
                    ZendeskUsers.name,
                    ZendeskUsers.email,
                    ZendeskUsers.suspended,
                ).where(ZendeskUsers.suspended == False)
            ).all()
            return all_users

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_zendesk_user_email_by_user_id(db_session, id):
        try:
            user_email = db_session.execute(
                select(
                    ZendeskUsers.email,
                ).where(ZendeskUsers.id == id)
            ).first()
            return user_email

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class ZendeskGroups(Base):
    __tablename__ = "zendesk_groups"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_group_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_group_id}, {self.name}'


class ZendeskGroupMemberships(Base):
    __tablename__ = "zendesk_group_memberships"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_users_id: Mapped[int] = mapped_column(ForeignKey("zendesk_users.id"))
    user_id_on_zendesk: Mapped[int] = mapped_column(nullable=False)
    zendesk_groups_id: Mapped[int] = mapped_column(ForeignKey("zendesk_groups.id"))
    group_id_on_zendesk: Mapped[int] = mapped_column(nullable=False)
    default: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_users_id}, {self.zendesk_groups_id}, {self.default}'

    @staticmethod
    def get_all_groups_and_mebers(db_session):
        try:
            groups_and_members = db_session.execute(
                select(
                    ZendeskGroups.id,
                    ZendeskGroups.name,
                    func.group_concat(ZendeskUsers.name.distinct()).label('users'),
                )
                .join(ZendeskGroupMemberships, ZendeskGroupMemberships.zendesk_groups_id == ZendeskGroups.id)
                .join(ZendeskUsers, ZendeskGroupMemberships.zendesk_users_id == ZendeskUsers.id)
                .group_by(ZendeskGroups.id, ZendeskGroups.name)
            ).all()
            return groups_and_members

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class AssignedTickets(Base):
    __tablename__ = "assigned_tickets"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_tickets_id: Mapped[int] = mapped_column(ForeignKey("zendesk_tickets.id"))
    users_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_tickets_id}, {self.users_id}, {self.assigned_at}'

    @staticmethod
    def user_tickets_in_the_last_hour(db_session, users_id):
        try:
            ticket_count = db_session.execute(
                select(
                    func.count(AssignedTickets.id)
                )
                .where(AssignedTickets.users_id == users_id)
                .where(AssignedTickets.assigned_at <= datetime.now())
                .where(AssignedTickets.assigned_at >= datetime.now() - timedelta(hours=1))
            ).scalar()
            return ticket_count

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def user_tickets_today(db_session, users_id):
        try:
            today = date.today()

            ticket_count = db_session.execute(
                select(
                    func.count(AssignedTickets.id)
                )
                .where(AssignedTickets.users_id == users_id)
                .where(AssignedTickets.assigned_at <= datetime(today.year, today.month, today.day, 23, 59, 59, 999))
                .where(AssignedTickets.assigned_at >= datetime(today.year, today.month, today.day, 00, 00, 00, 000))
            ).scalar()

            return ticket_count

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_new_assigned_ticket(db_session, zendesk_tickets_id, users_id):
        new_assigned_ticket = AssignedTickets(
            zendesk_tickets_id=zendesk_tickets_id,
            users_id=users_id
        )
        try:
            db_session.add(new_assigned_ticket)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class AssignedTicketsLog(Base):
    __tablename__ = "assigned_tickets_log"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_tickets_id: Mapped[int] = mapped_column(ForeignKey("zendesk_tickets.id"))
    users_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    json: Mapped[dict | list] = mapped_column(type_=JSON, nullable=False)
    created_at = Column(DATETIME(fsp=3), server_default=func.now())

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_tickets_id}, {self.zendesk_tickets_id}, {self.json}'

    @staticmethod
    def insert_new_log(db_session, zendesk_tickets_id, json, users_id=None):
        new_log = AssignedTicketsLog(
            zendesk_tickets_id=zendesk_tickets_id,
            users_id=users_id,
            json=json,
        )
        try:
            db_session.add(new_log)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_last_ten_logs(db_session):
        try:
            last_ten_logs = db_session.execute(
                select(
                    AssignedTicketsLog.id,
                    case(
                        (ZendeskTickets.ticket_id == None, '-'),
                        else_=ZendeskTickets.ticket_id
                    ),
                    case(
                        (Users.name == None, '-'),
                        else_=Users.name
                    ),
                    AssignedTicketsLog.json,
                    AssignedTicketsLog.created_at,
                ).join(ZendeskTickets, isouter=True)
                .join(Users, isouter=True)
                .limit(10)
                .order_by(AssignedTicketsLog.id.desc())
            ).all()

            return last_ten_logs

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_logs(db_session, **kwargs):
        try:
            stmt = select(
                AssignedTicketsLog.id,
                case(
                    (ZendeskTickets.ticket_id == None, '-'),
                    else_=ZendeskTickets.ticket_id
                ),
                case(
                    (Users.name == None, '-'),
                    else_=Users.name
                ),
                AssignedTicketsLog.json,
                AssignedTicketsLog.created_at,
            ) \
                .join(ZendeskTickets, isouter=True) \
                .join(Users, isouter=True) \
                .order_by(AssignedTicketsLog.id.desc())

            if kwargs['data']['initial_date']:
                stmt = stmt.where(AssignedTicketsLog.created_at >= kwargs['data']['initial_date'])

            if kwargs['data']['final_date']:
                stmt = stmt.where(AssignedTicketsLog.created_at <= kwargs['data']['final_date'])

            if kwargs['data']['users_id']:
                stmt = stmt.where(AssignedTicketsLog.users_id == kwargs['data']['users_id'])

            if kwargs['data']['zendesk_ticket_id']:
                stmt = stmt.where(ZendeskTickets.ticket_id == kwargs['data']['zendesk_ticket_id'])

            logs_with_filters = db_session.execute(stmt).all()

            return logs_with_filters

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class UserBacklog(Base):
    __tablename__ = "user_backlog"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    users_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    ticket_id: Mapped[int] = mapped_column(nullable=False)
    ticket_status: Mapped[str] = mapped_column(String(100), nullable=False)
    ticket_level: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f'{self.id}, {self.users_id}, {self.ticket_id}, ' \
               f'{self.ticket_status}, {self.ticket_level}'

    @staticmethod
    def get_user_backlog(db_session, users_id):
        try:
            user_backlog = db_session.execute(
                select(
                    UserBacklog.id,
                    UserBacklog.users_id,
                    UserBacklog.ticket_id,
                    UserBacklog.ticket_status,
                    UserBacklog.ticket_level,
                ).where(UserBacklog.users_id == users_id)
            ).all()
            return user_backlog

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_agent_backlog_count(db_session, users_id):
        try:
            user_open_backlog = db_session.execute(
                select(
                    func.count(UserBacklog.id)
                )
                .where(UserBacklog.users_id == users_id)
                .where(
                    and_(
                        or_(
                            UserBacklog.ticket_status == 'open',
                            UserBacklog.ticket_status == '',
                            UserBacklog.ticket_status == None,
                        )
                    )
                )
                .where(
                    and_(
                        or_(
                            UserBacklog.ticket_level == 'atendimento_n1_n2',
                            UserBacklog.ticket_level == '',
                            UserBacklog.ticket_level == None,
                        )
                    )
                )
            ).scalar()

            user_pending_hold_backlog = db_session.execute(
                select(
                    func.count(UserBacklog.id)
                )
                .where(UserBacklog.users_id == users_id)
                .where(
                    and_(
                        or_(
                            UserBacklog.ticket_status == 'pending',
                            UserBacklog.ticket_status == 'hold'
                        )
                    )
                )
                .where(
                    and_(
                        or_(
                            UserBacklog.ticket_level == 'atendimento_n1_n2',
                            UserBacklog.ticket_level == None,
                        )
                    )
                )
            ).scalar()

            user_backlog = int(user_open_backlog) + (int(user_pending_hold_backlog) / 2)

            return user_backlog

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class ZendeskLocales(Base):
    __tablename__ = "zendesk_locales"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_locale_id: Mapped[int] = mapped_column(nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    presentation_name: Mapped[str] = mapped_column(String(100), nullable=False)
    default: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_locale_id}, {self.locale}, ' \
               f'{self.name}, {self.presentation_name}, {self.default}'


class ZendeskTicketForms(Base):
    __tablename__ = "zendesk_ticket_forms"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_ticket_form_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    default: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_ticket_form_id}, {self.name}, ' \
               f'{self.display_name}, {self.default}'


class ZendeskTicketFields(Base):
    __tablename__ = "zendesk_ticket_fields"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_ticket_field_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_ticket_field_id}, {self.title}, {self.type}'


class ZendeskTicketFieldsInForms(Base):
    __tablename__ = "zendesk_ticket_fields_in_forms"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_ticket_forms_id: Mapped[int] = mapped_column(ForeignKey("zendesk_ticket_forms.id"))
    zendesk_ticket_fields_id: Mapped[int] = mapped_column(ForeignKey("zendesk_ticket_fields.id"))

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_ticket_forms_id}, {self.zendesk_ticket_fields_id}'

    @staticmethod
    def get_form_fields(db_session, form_id):
        all_fields = db_session.execute(
            select(
                ZendeskTicketFieldsInForms.id,
                ZendeskTicketFields.title
            ).where(ZendeskTicketFieldsInForms.zendesk_ticket_forms_id == form_id)
            .join(ZendeskTicketFields)
        ).all()

        if all_fields:
            return all_fields
        else:
            return None


class ZendeskTicketFieldOptions(Base):
    __tablename__ = "zendesk_ticket_field_options"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_ticket_fields_id: Mapped[int] = mapped_column(ForeignKey("zendesk_ticket_fields.id"))
    zendesk_ticket_field_option_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_ticket_fields_id}, {self.name}, {self.position}'


class ZendeskTags(Base):
    __tablename__ = "zendesk_tags"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.tag}'


class Routes(Base):
    __tablename__ = "routes"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.name}, {self.active}, {self.deleted}'


class RouteRecipientType(Base):
    __tablename__ = "route_recipient_type"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    routes_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    recipient_type: Mapped[int] = mapped_column(nullable=False)  # 0 = users | 1 = group

    def __repr__(self) -> str:
        return f'{self.id}, {self.routes_id}, {self.recipient_type}'


class RouteRecipientUsers(Base):
    __tablename__ = "route_recipent_users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    routes_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    zendesk_users_id: Mapped[int] = mapped_column(ForeignKey("zendesk_users.id"))

    def __repr__(self) -> str:
        return f'{self.id}, {self.routes_id}, {self.zendesk_users_id}'


class RouteRecipientGroups(Base):
    __tablename__ = "route_recipent_groups"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    routes_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    zendesk_groups_id: Mapped[int] = mapped_column(ForeignKey("zendesk_groups.id"))

    def __repr__(self) -> str:
        return f'{self.id}, {self.routes_id}, {self.zendesk_groups_id}'


class RouteTicketLocales(Base):
    __tablename__ = "route_ticket_locales"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    routes_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    zendesk_locales_id: Mapped[int] = mapped_column(ForeignKey("zendesk_locales.id"))

    def __repr__(self) -> str:
        return f'{self.id}, {self.routes_id}, {self.zendesk_locales_id}'

    @staticmethod
    def insert_one_locale(db_session, routes_id, zendesk_locales_id):
        new_ticket_locale = RouteTicketLocales(
            routes_id=int(routes_id),
            zendesk_locales_id=int(zendesk_locales_id),
        )
        try:
            db_session.add(new_ticket_locale)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def select_all_locales_in_a_route(db_session, routes_id):
        existing_record = db_session.execute(
            select(RouteTicketLocales.zendesk_locales_id)
            .where(RouteTicketLocales.routes_id == routes_id)
        ).all()
        if existing_record:
            return existing_record
        else:
            return None

    @staticmethod
    def check_existing_locale_in_route(db_session, routes_id, zendesk_locales_id):
        existing_record = db_session.execute(
            select(RouteTicketLocales)
            .where(RouteTicketLocales.routes_id == routes_id)
            .where(RouteTicketLocales.zendesk_locales_id == zendesk_locales_id)
        ).first()
        if existing_record:
            return True
        else:
            return False

    @staticmethod
    def delete_list_of_locales_in_route(db_session, routes_id, list_of_zendesk_locales_ids):
        try:
            db_session.execute(
                delete(RouteTicketLocales)
                .where(RouteTicketLocales.routes_id == routes_id)
                .where(RouteTicketLocales.zendesk_locales_id.in_(list_of_zendesk_locales_ids))
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_all_locales_in_route(db_session, routes_id):
        try:
            db_session.execute(
                delete(RouteTicketLocales)
                .where(RouteTicketLocales.routes_id == routes_id)
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class RouteTicketGroups(Base):
    __tablename__ = "route_ticket_groups"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    routes_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    zendesk_groups_id: Mapped[int] = mapped_column(ForeignKey("zendesk_groups.id"))

    def __repr__(self) -> str:
        return f'{self.id}, {self.routes_id}, {self.zendesk_groups_id}'

    @staticmethod
    def insert_one_group(db_session, routes_id, zendesk_groups_id):
        new_ticket_group = RouteTicketGroups(
            routes_id=int(routes_id),
            zendesk_groups_id=int(zendesk_groups_id),
        )
        try:
            db_session.add(new_ticket_group)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_list_of_groups(db_session, routes_id, list_of_zendesk_groups_ids):
        try:
            for group in list_of_zendesk_groups_ids:
                db_session.execute(
                    insert(RouteTicketGroups), [
                        {'routes_id': routes_id, 'zendesk_groups_id': group}
                    ]
                )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def select_all_groups_in_a_route(db_session, routes_id):
        existing_record = db_session.execute(
            select(RouteTicketGroups.zendesk_groups_id)
            .where(RouteTicketGroups.routes_id == routes_id)
        ).all()
        if existing_record:
            return existing_record
        else:
            return None

    @staticmethod
    def check_existing_group_in_route(db_session, routes_id, zendesk_groups_id):
        existing_record = db_session.execute(
            select(RouteTicketGroups)
            .where(RouteTicketGroups.routes_id == routes_id)
            .where(RouteTicketGroups.zendesk_groups_id == zendesk_groups_id)
        ).first()
        if existing_record:
            return True
        else:
            return False

    @staticmethod
    def delete_list_of_groups_in_route(db_session, routes_id, list_of_zendesk_groups_ids):
        try:
            db_session.execute(
                delete(RouteTicketGroups)
                .where(RouteTicketGroups.routes_id == routes_id)
                .where(RouteTicketGroups.zendesk_groups_id.in_(list_of_zendesk_groups_ids))
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_all_groups_in_route(db_session, routes_id):
        try:
            db_session.execute(
                delete(RouteTicketGroups)
                .where(RouteTicketGroups.routes_id == routes_id)
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class RouteTicketTags(Base):
    __tablename__ = "route_ticket_tags"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    routes_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    zendesk_tags_id: Mapped[int] = mapped_column(ForeignKey("zendesk_tags.id"))

    def __repr__(self) -> str:
        return f'{self.id}, {self.routes_id}, {self.zendesk_tags_id}'

    @staticmethod
    def insert_one_tag(db_session, routes_id, zendesk_tags_id):
        new_ticket_tag = RouteTicketTags(
            routes_id=int(routes_id),
            zendesk_tags_id=int(zendesk_tags_id),
        )
        try:
            db_session.add(new_ticket_tag)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def select_all_tags_in_a_route(db_session, routes_id):
        existing_record = db_session.execute(
            select(RouteTicketTags.zendesk_tags_id)
            .where(RouteTicketTags.routes_id == routes_id)
        ).all()
        if existing_record:
            return existing_record
        else:
            return None

    @staticmethod
    def check_existing_tag_in_route(db_session, routes_id, zendesk_tags_id):
        existing_record = db_session.execute(
            select(RouteTicketTags)
            .where(RouteTicketTags.routes_id == routes_id)
            .where(RouteTicketTags.zendesk_tags_id == zendesk_tags_id)
        ).first()
        if existing_record:
            return True
        else:
            return False

    @staticmethod
    def delete_list_of_tags_in_route(db_session, routes_id, list_of_zendesk_tags_ids):
        try:
            db_session.execute(
                delete(RouteTicketTags)
                .where(RouteTicketTags.routes_id == routes_id)
                .where(RouteTicketTags.zendesk_tags_id.in_(list_of_zendesk_tags_ids))
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_all_tags_in_route(db_session, routes_id):
        try:
            db_session.execute(
                delete(RouteTicketTags)
                .where(RouteTicketTags.routes_id == routes_id)
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class GeneralSettings(Base):
    __tablename__ = "general_settings"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    use_routes: Mapped[bool] = mapped_column(Boolean, nullable=False)  # 0 = Zendesk Views | 1 = Routes
    routing_model: Mapped[int] = mapped_column(nullable=False)  # 0 = Least Active | 1 = Round Robin
    agent_backlog_limit: Mapped[int] = mapped_column(nullable=False)
    daily_ticket_assignment_limit: Mapped[int] = mapped_column(nullable=False)
    hourly_ticket_assignment_limit: Mapped[int] = mapped_column(nullable=False)
    zendesk_schedules_id: Mapped[int] = mapped_column(ForeignKey("zendesk_schedules.id"))

    def __repr__(self) -> str:
        return f'{self.id}, {self.use_routes}, {self.routing_model}, ' \
               f'{self.agent_backlog_limit}, {self.daily_ticket_assignment_limit}'

    @staticmethod
    def get_settings(db_session):
        try:
            all_settings = db_session.execute(
                select(
                    GeneralSettings.use_routes,
                    GeneralSettings.routing_model,
                    GeneralSettings.agent_backlog_limit,
                    GeneralSettings.daily_ticket_assignment_limit,
                    GeneralSettings.hourly_ticket_assignment_limit,
                    GeneralSettings.zendesk_schedules_id,
                )
            ).first()
            return all_settings

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def update_settings(db_session, use_routes, routing_model, agent_backlog_limit,
                        daily_ticket_assignment_limit, hourly_ticket_assignment_limit, zendesk_schedules_id):
        try:
            db_session.execute(
                update(GeneralSettings)
                .values(
                    use_routes=use_routes,
                    routing_model=routing_model,
                    agent_backlog_limit=agent_backlog_limit,
                    daily_ticket_assignment_limit=daily_ticket_assignment_limit,
                    hourly_ticket_assignment_limit=hourly_ticket_assignment_limit,
                    zendesk_schedules_id=zendesk_schedules_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def is_currently_hour_working_hours(db_session):
        try:
            current_time = datetime.now().time()
            midnight_time = datetime.combine(datetime.today(), time.min).time()

            delta_time = \
                datetime.combine(date.today(), current_time) - \
                datetime.combine(date.today(), midnight_time)

            app_schedule_id = db_session.execute(
                select(GeneralSettings.zendesk_schedules_id)
            ).scalar()

            if date.today().weekday() == 0:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.monday_start,
                        ZendeskSchedules.monday_end,
                    ).where(ZendeskSchedules.id == app_schedule_id)
                ).first()
                if working_hours.monday_start and working_hours.monday_end:
                    if working_hours.monday_start <= delta_time <= working_hours.monday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 1:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.tuesday_start,
                        ZendeskSchedules.tuesday_end,
                    ).where(ZendeskSchedules.id == app_schedule_id)
                ).first()
                if working_hours.tuesday_start and working_hours.tuesday_end:
                    if working_hours.tuesday_start <= delta_time <= working_hours.tuesday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 2:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.wednesday_start,
                        ZendeskSchedules.wednesday_end,
                    ).where(ZendeskSchedules.id == app_schedule_id)
                ).first()
                if working_hours.wednesday_start and working_hours.wednesday_end:
                    if working_hours.wednesday_start <= delta_time <= working_hours.wednesday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 3:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.thursday_start,
                        ZendeskSchedules.thursday_end,
                    ).where(ZendeskSchedules.id == app_schedule_id)
                ).first()
                if working_hours.thursday_start and working_hours.thursday_end:
                    if working_hours.thursday_start <= delta_time <= working_hours.thursday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 4:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.friday_start,
                        ZendeskSchedules.friday_end,
                    ).where(ZendeskSchedules.id == app_schedule_id)
                ).first()
                if working_hours.friday_start and working_hours.friday_end:
                    if working_hours.friday_start <= delta_time <= working_hours.friday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 5:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.saturday_start,
                        ZendeskSchedules.saturday_end,
                    ).where(ZendeskSchedules.id == app_schedule_id)
                ).first()
                if working_hours.saturday_start and working_hours.saturday_end:
                    if working_hours.saturday_start <= delta_time <= working_hours.saturday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 6:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.sunday_start,
                        ZendeskSchedules.sunday_end,
                    ).where(ZendeskSchedules.id == app_schedule_id)
                ).first()
                if working_hours.sunday_start and working_hours.sunday_end:
                    if working_hours.sunday_start <= delta_time <= working_hours.sunday_end:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return None

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class ZendeskSchedules(Base):
    __tablename__ = "zendesk_schedules"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_schedule_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False)
    sunday_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sunday_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    monday_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    monday_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    tuesday_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    tuesday_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    wednesday_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    wednesday_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    thursday_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    thursday_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    friday_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    friday_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    saturday_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    saturday_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __repr__(self) -> str:
        return f'{self.id}, {self.name}, {self.timezone}'

    @staticmethod
    def get_schedules(db_session):
        try:
            all_schedules = db_session.execute(
                select(ZendeskSchedules.id,
                       ZendeskSchedules.zendesk_schedule_id,
                       ZendeskSchedules.name,
                       ZendeskSchedules.timezone)
            ).all()
            return all_schedules

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_zendesk_schedule_name_by_id(db_session, id):
        try:
            schedule_name = db_session.execute(
                select(
                    ZendeskSchedules.name,
                ).where(ZendeskSchedules.id == id)
            ).scalar()
            return schedule_name

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_schedule(db_session, schedule_id):
        try:
            schedule = db_session.execute(
                select(
                    ZendeskSchedules.id, ZendeskSchedules.name, ZendeskSchedules.timezone,
                    ZendeskSchedules.sunday_start, ZendeskSchedules.sunday_end,
                    ZendeskSchedules.monday_start, ZendeskSchedules.monday_end,
                    ZendeskSchedules.tuesday_start, ZendeskSchedules.tuesday_end,
                    ZendeskSchedules.wednesday_start, ZendeskSchedules.wednesday_end,
                    ZendeskSchedules.thursday_start, ZendeskSchedules.thursday_end,
                    ZendeskSchedules.friday_start, ZendeskSchedules.friday_end,
                    ZendeskSchedules.saturday_start, ZendeskSchedules.saturday_end,
                ).where(ZendeskSchedules.id == schedule_id)
            ).first()
            return schedule

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_schedule_hour(db_session, schedule_id, hour, start_or_end):
        parsed_week_day = int(ZendeskSchedules.get_week_day(hour))
        parsed_hour = ZendeskSchedules.get_hour(hour)
        if start_or_end == 'start_time':
            week_day_column = ZendeskSchedules.get_starting_hour_column(parsed_week_day)
        elif start_or_end == 'end_time':
            week_day_column = ZendeskSchedules.get_ending_hour_column(parsed_week_day)
        else:
            raise ValueError(f'Invalid start_or_end parameter.'
                             f'Expected start_time or end_time, received {str(start_or_end)}')

        try:
            db_session.execute(
                update(ZendeskSchedules),
                [
                    {"id": schedule_id, week_day_column: parsed_hour}
                ],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def update_schedule_hours(db_session, schedule_id, start_time, end_time):
        start_parsed_week_day = int(ZendeskSchedules.get_week_day(start_time))
        end_parsed_week_day = int(ZendeskSchedules.get_week_day(end_time))

        start_parsed_hour = ZendeskSchedules.get_hour(start_time)
        end_parsed_hour = ZendeskSchedules.get_hour(end_time)

        start_week_day_column = ZendeskSchedules.get_starting_hour_column(start_parsed_week_day)
        end_week_day_column = ZendeskSchedules.get_ending_hour_column(end_parsed_week_day)

        try:
            db_session.execute(
                update(ZendeskSchedules),
                [
                    {'id': schedule_id, start_week_day_column: start_parsed_hour, end_week_day_column: end_parsed_hour}
                ],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_starting_hour_column(argument):
        switcher = {
            1: "sunday_start",
            2: "monday_start",
            3: "tuesday_start",
            4: "wednesday_start",
            5: "thursday_start",
            6: "friday_start",
            7: "saturday_start",
        }
        return switcher.get(argument, "Invalid input")

    @staticmethod
    def get_ending_hour_column(argument):
        switcher = {
            1: "sunday_end",
            2: "monday_end",
            3: "tuesday_end",
            4: "wednesday_end",
            5: "thursday_end",
            6: "friday_end",
            7: "saturday_end",
        }
        return switcher.get(argument, "Invalid input")

    @staticmethod
    def get_week_day(minutes):
        days = ['1', '2', '3', '4', '5', '6', '7']
        day_index = minutes // 1440
        day = days[day_index % 7]
        return day

    @staticmethod
    def get_hour(minutes):
        hour = (minutes // 60) % 24
        minute = minutes % 60
        hour = f'{hour:02d}:{minute:02d}:00'
        # a_time = time(hour, minute, 0, 0)
        return hour

    @staticmethod
    def insert_schedule(db_session, zendesk_schedule_id, schedule_name, schedule_timezone):
        try:
            db_session.execute(
                insert(ZendeskSchedules)
                .values(
                    zendesk_schedule_id=zendesk_schedule_id,
                    name=schedule_name,
                    timezone=schedule_timezone,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_id_from_zendesk_schedule_id(db_session, zendesk_schedule_id):
        try:
            schedule_id = db_session.execute(
                select(ZendeskSchedules.id).where(ZendeskSchedules.zendesk_schedule_id == zendesk_schedule_id)
            ).scalar()
            return schedule_id

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def check_for_existing_schedule(db_session, zendesk_schedule_id):
        try:
            schedule_id = db_session.execute(
                select(ZendeskSchedules).where(ZendeskSchedules.zendesk_schedule_id == zendesk_schedule_id)
            ).scalar()
            if schedule_id:
                return True
            else:
                return False

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    password: Mapped[str] = mapped_column(String(500))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    authenticated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    routing_status: Mapped[int] = mapped_column(nullable=False)  # 0 = offline | 1 = online | 2 = away
    zendesk_users_id: Mapped[int] = mapped_column(ForeignKey('zendesk_users.id'))
    zendesk_schedules_id: Mapped[int] = mapped_column(ForeignKey('zendesk_schedules.id'))
    backlog_limit: Mapped[int] = mapped_column(nullable=False)
    hourly_ticket_assignment_limit: Mapped[int] = mapped_column(nullable=False)
    daily_ticket_assignment_limit: Mapped[int] = mapped_column(nullable=False)

    @staticmethod
    def get_all_users(db_session):
        try:
            users = db_session.execute(
                select(
                    Users.id,
                    ZendeskUsers.zendesk_user_id,
                    Users.name,
                    Users.email,
                    Users.routing_status,
                ).join(ZendeskUsers, isouter=True)
                .where(Users.deleted == 0)
            ).all()
            return users

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_user(db_session, user_id):
        try:
            user = db_session.execute(
                select(
                    Users.id,
                    Users.name,
                    Users.email,
                    Users.active,
                    Users.deleted,
                    Users.authenticated,
                    Users.routing_status,  # 0 = offline | 1 = online | 2 = away
                    Users.zendesk_users_id,
                    ZendeskUsers.zendesk_user_id,
                    Users.zendesk_schedules_id,
                    Users.backlog_limit,
                    Users.hourly_ticket_assignment_limit,
                    Users.daily_ticket_assignment_limit,
                ).where(Users.id == user_id)
                .join(ZendeskUsers, isouter=True)
            ).first()
            return user

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_user_profile(db_session, user_id):
        try:
            user = db_session.execute(
                select(
                    Users.id,
                    Users.name,
                    Users.email,
                    Users.password,
                ).where(Users.id == user_id)
            ).first()

            return user

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_user_from_email(db_session, user_email):
        try:
            user = db_session.execute(
                select(
                    Users.id,
                    Users.name,
                    Users.email,
                    Users.active,
                    Users.deleted,
                ).where(Users.email == user_email)
            ).first()
            return user

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def login_user(db_session, user_id):
        try:
            db_session.execute(
                update(Users), [{
                    'id': user_id,
                    'authenticated': 1,
                }],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def logout_user(db_session, user_id):
        try:
            db_session.execute(
                update(Users), [{
                    'id': user_id,
                    'authenticated': 0,
                }],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def change_routing_status(db_session, user_id, routing_status):
        try:
            db_session.execute(
                update(Users), [{
                    'id': user_id,
                    'routing_status': routing_status,
                }],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_user_status(db_session, user_id):
        try:
            status = db_session.execute(
                select(
                    Users.routing_status,  # 0 = offline | 1 = online | 2 = away
                ).where(Users.id == user_id)
            ).scalar()
            return status

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_new_user(db_session, name, email, active, zendesk_users_id, zendesk_schedules_id,
                        backlog_limit, hourly_ticket_assignment_limit, daily_ticket_assignment_limit):
        new_user = Users(
            name=name,
            email=email,
            password=bcrypt.generate_password_hash(
                ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
            ).decode('utf-8'),
            active=active,
            deleted=False,
            authenticated=0,
            routing_status=0,
            zendesk_users_id=zendesk_users_id,
            zendesk_schedules_id=zendesk_schedules_id,
            backlog_limit=backlog_limit,
            hourly_ticket_assignment_limit=hourly_ticket_assignment_limit,
            daily_ticket_assignment_limit=daily_ticket_assignment_limit,
        )
        try:
            db_session.add(new_user)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_user(db_session, user_id):
        try:
            db_session.execute(
                update(Users), [{
                    'id': user_id,
                    'deleted': 1,
                    'authenticated': 0,
                    'routing_status': 0,
                }],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def update_user(db_session, user_id, name, email, active, zendesk_users_id, zendesk_schedules_id,
                    backlog_limit, hourly_ticket_assignment_limit, daily_ticket_assignment_limit):
        try:
            db_session.execute(
                update(Users), [{
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'active': active,
                    'zendesk_users_id': zendesk_users_id,
                    'zendesk_schedules_id': zendesk_schedules_id,
                    'backlog_limit': backlog_limit,
                    'hourly_ticket_assignment_limit': hourly_ticket_assignment_limit,
                    'daily_ticket_assignment_limit': daily_ticket_assignment_limit,
                }],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def update_user_password(db_session, user_id, password):
        try:
            db_session.execute(
                update(Users), [{
                    'id': user_id,
                    'password': password,
                }],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def update_user_name_from_profile(db_session, user_id, name):
        try:
            db_session.execute(
                update(Users), [{
                    'id': user_id,
                    'name': name,
                }],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_user_from_zendesk_users_id(db_session, zendesk_users_id):
        try:
            user = db_session.execute(
                select(
                    Users.id,
                    Users.name,
                    Users.email,
                    Users.active,
                    Users.deleted,
                    Users.authenticated,
                    Users.routing_status,  # 0 = offline | 1 = online | 2 = away
                    Users.zendesk_users_id,
                    Users.zendesk_schedules_id,
                    Users.backlog_limit,
                    Users.hourly_ticket_assignment_limit,
                    Users.daily_ticket_assignment_limit,
                ).where(Users.zendesk_users_id == zendesk_users_id)
            ).first()
            return user

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def is_user_on_working_hours(db_session, users_id):
        try:
            current_time = datetime.now().time()
            midnight_time = datetime.combine(datetime.today(), time.min).time()

            delta_time = \
                datetime.combine(date.today(), current_time) - \
                datetime.combine(date.today(), midnight_time)

            if date.today().weekday() == 0:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.monday_start,
                        ZendeskSchedules.monday_end,
                    ).where(Users.id == users_id)
                    .join(Users)
                ).first()
                if working_hours.monday_start and working_hours.monday_end:
                    if working_hours.monday_start <= delta_time <= working_hours.monday_end:
                        return True
                    else:
                        return False
                else:
                    return True

            elif date.today().weekday() == 1:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.tuesday_start,
                        ZendeskSchedules.tuesday_end,
                    ).where(Users.id == users_id)
                    .join(Users)
                ).first()
                if working_hours.tuesday_start and working_hours.tuesday_end:
                    if working_hours.tuesday_start <= delta_time <= working_hours.tuesday_end:
                        return True
                    else:
                        return False
                else:
                    return True

            elif date.today().weekday() == 2:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.wednesday_start,
                        ZendeskSchedules.wednesday_end,
                    ).where(Users.id == users_id)
                    .join(Users)
                ).first()
                if working_hours.wednesday_start and working_hours.wednesday_end:
                    if working_hours.wednesday_start <= delta_time <= working_hours.wednesday_end:
                        return True
                    else:
                        return False
                else:
                    return True

            elif date.today().weekday() == 3:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.thursday_start,
                        ZendeskSchedules.thursday_end,
                    ).where(Users.id == users_id)
                    .join(Users)
                ).first()
                if working_hours.thursday_start and working_hours.thursday_end:
                    if working_hours.thursday_start <= delta_time <= working_hours.thursday_end:
                        return True
                    else:
                        return False
                else:
                    return True

            elif date.today().weekday() == 4:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.friday_start,
                        ZendeskSchedules.friday_end,
                    ).where(Users.id == users_id)
                    .join(Users)
                ).first()
                if working_hours.friday_start and working_hours.friday_end:
                    if working_hours.friday_start <= delta_time <= working_hours.friday_end:
                        return True
                    else:
                        return False
                else:
                    return True

            elif date.today().weekday() == 5:
                working_hours = db_session.execute(
                    select(
                        Users.zendesk_schedules_id,
                        ZendeskSchedules.saturday_start,
                        ZendeskSchedules.saturday_end,
                    ).where(Users.id == users_id)
                    .join(ZendeskSchedules, Users.zendesk_schedules_id == ZendeskSchedules.id)
                ).first()
                if working_hours.saturday_start and working_hours.saturday_end:
                    if working_hours.saturday_start <= delta_time <= working_hours.saturday_end:
                        return True
                    else:
                        return False
                else:
                    return True

            elif date.today().weekday() == 6:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.sunday_start,
                        ZendeskSchedules.sunday_end,
                    ).where(Users.id == users_id)
                    .join(Users)
                ).first()
                if working_hours.sunday_start and working_hours.sunday_end:
                    if working_hours.sunday_start <= delta_time <= working_hours.sunday_end:
                        return True
                    else:
                        return False
                else:
                    return True
            else:
                return None

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def change_user_status(db_session, user_id):
        try:
            current_status = db_session.execute(
                select(
                    Users.routing_status,  # 0 = offline | 1 = online | 2 = away
                ).where(Users.id == user_id)
            ).scalar()

            if current_status == 1:
                new_status = 2
            elif current_status == 2:
                new_status = 1
            else:
                new_status = current_status

            db_session.execute(
                update(Users)
                .where(Users.id == user_id)
                .values(routing_status=new_status)
            )

            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def disconnect_all_users(db_session):
        try:
            db_session.execute(
                update(Users)
                .values(
                    authenticated=False,
                    routing_status=0,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    users_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    type: Mapped[int] = mapped_column(nullable=False)  # 0 = new_ticket | 1 = system notifications
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received: Mapped[bool] = mapped_column(Boolean, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    read: Mapped[bool] = mapped_column(Boolean, nullable=False)

    @staticmethod
    def get_next_pending_user_notification(db_session, user_id):
        try:
            notification = db_session.execute(
                select(
                    Notifications.id,
                    Notifications.type,
                    Notifications.content,
                    Notifications.url,
                    Notifications.read,
                ).where(Notifications.users_id == user_id)
                .where(Notifications.sent == 0)
                .where(Notifications.read == 0)
                .order_by(Notifications.id)
            ).first()
            return notification

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def create_notification(db_session, user_id, notification_type, content, *ticket_id):
        if len(content) >= 499:
            content = content[:494] + '[...]'

        if ticket_id:
            new_notification = Notifications(
                users_id=user_id,
                type=notification_type,
                content=content,
                url=ZENDESK_BASE_URL + 'agent/tickets/' + str(ticket_id[0]),
                # created_at → Not needed, since the server has a default as func.now()
                sent=False,
                received=False,
                read=False,
            )
        else:
            new_notification = Notifications(
                users_id=user_id,
                type=notification_type,
                content=content,
                # created_at → Not needed, since the server has a default as func.now()
                sent=False,
                received=False,
                read=False,
            )
        try:
            db_session.add(new_notification)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def flag_notification_as_sent(db_session, notification_id):
        try:
            db_session.execute(
                update(Notifications), [{
                    'id': notification_id,
                    'sent': True,
                    'sent_at': datetime.now(),
                }],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def flag_notification_as_received(db_session, notification_id):
        try:
            db_session.execute(
                update(Notifications), [{
                    'id': notification_id,
                    'received': True,
                    'received_at': datetime.now(),
                }],
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def count_user_unread_notifications(db_session, users_id):
        try:
            notifications_count = db_session.execute(
                select(
                    func.count(Notifications.id)
                )
                .where(Notifications.users_id == users_id)
                .where(Notifications.read == False)
            ).scalar()

            return notifications_count

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def flag_notification_as_read(db_session, notification_id):
        try:
            db_session.execute(
                update(Notifications), [{
                    'id': notification_id,
                    'read': True,
                }],
            )

            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def flag_all_notifications_as_read(db_session, users_id):
        try:
            db_session.execute(
                update(Notifications)
                .values(read=True)
                .where(Notifications.users_id == users_id)
                .where(Notifications.read == False)
            )

            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_user_last_hundred_notifications(db_session, users_id):
        try:
            notifications = db_session.execute(
                select(
                    Notifications.id,
                    Notifications.content,
                    Notifications.url,
                    Notifications.read,
                ).where(Notifications.users_id == users_id)
                .order_by(Notifications.id.desc())
            ).all()

            return notifications

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class UsersQueue(Base):
    __tablename__ = 'users_queue'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    users_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)  # 0 = not in queue
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @staticmethod
    def get_users_in_queue(db_session):
        try:
            queue = db_session.execute(
                select(
                    UsersQueue.id,
                    UsersQueue.users_id,
                    UsersQueue.position,
                    UsersQueue.updated_at,
                ).where(UsersQueue.position > 0)
                .order_by(UsersQueue.position.asc())
            ).all()

            return queue

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def does_user_exist_in_queue(db_session, users_id):
        try:
            user = db_session.execute(
                select(UsersQueue.id).where(UsersQueue.users_id == users_id)
            ).scalar()
            if user:
                return True
            else:
                return False

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_new_user_in_queue(db_session, users_id):
        new_user = UsersQueue(
            users_id=users_id,
            position=0,
        )
        try:
            db_session.add(new_user)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def fix_queue_after_removing_or_deleting_user(db_session, current_user):
        users_ahead_of_current_user = db_session.execute(
            select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).where(
                UsersQueue.position > current_user.position)
        ).all()

        for user in users_ahead_of_current_user:
            if user.position != 1:
                db_session.execute(
                    update(UsersQueue), [{
                        'id': user.id,
                        'position': user.position - 1,
                        'updated_at': datetime.now(),
                    }],
                )

    @staticmethod
    def remove_user_from_queue(db_session, users_id):
        try:
            current_user = db_session.execute(
                select(UsersQueue.id, UsersQueue.position).where(UsersQueue.users_id == users_id)
            ).first()

            db_session.execute(
                update(UsersQueue), [{
                    'id': current_user.id,
                    'position': 0,
                    'updated_at': datetime.now(),
                }],
            )

            UsersQueue.fix_queue_after_removing_or_deleting_user(db_session, current_user)

            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def remove_all_users_from_queue(db_session):
        try:
            db_session.execute(
                update(UsersQueue).values(position=0).where(UsersQueue.position > 0)
            )

            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_user_from_queue(db_session, users_id):
        try:
            current_user = db_session.execute(
                select(UsersQueue.id, UsersQueue.position).where(UsersQueue.users_id == users_id)
            ).first()

            db_session.execute(
                delete(UsersQueue).where(UsersQueue.id == current_user.id)
            )

            UsersQueue.fix_queue_after_removing_or_deleting_user(db_session, current_user)

            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def move_user_to_queue_end(db_session, users_id):
        try:
            current_user = db_session.execute(
                select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).where(UsersQueue.users_id == users_id)
            ).first()

            if current_user:
                users_ahead_of_current_user = db_session.execute(
                    select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).where(
                        UsersQueue.position > current_user.position)
                ).all()

                last_user_in_the_queue = db_session.execute(
                    select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).order_by(UsersQueue.position.desc())
                ).first()

                ''' Get the users ahead of the current users one position down '''
                for user in users_ahead_of_current_user:
                    if user.position != 1:
                        db_session.execute(
                            update(UsersQueue), [{
                                'id': user.id,
                                'position': user.position - 1,
                                'updated_at': datetime.now(),
                            }],
                        )

                ''' Get current users to the end of the queue '''
                if current_user.position != last_user_in_the_queue.position and last_user_in_the_queue.position != 0:
                    db_session.execute(
                        update(UsersQueue), [{
                            'id': current_user.id,
                            'position': last_user_in_the_queue.position,
                            'updated_at': datetime.now(),
                        }],
                    )
                elif last_user_in_the_queue.position == 0:
                    db_session.execute(
                        update(UsersQueue), [{
                            'id': current_user.id,
                            'position': 1,
                            'updated_at': datetime.now(),
                        }],
                    )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_user_at_queue_end(db_session, users_id):
        try:
            current_user = db_session.execute(
                select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).where(UsersQueue.users_id == users_id)
            ).first()

            if current_user:
                last_user_in_the_queue = db_session.execute(
                    select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).order_by(UsersQueue.position.desc())
                ).first()

                db_session.execute(
                    update(UsersQueue), [{
                        'id': current_user.id,
                        'position': last_user_in_the_queue.position + 1,
                        'updated_at': datetime.now(),
                    }],
                )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def check_if_user_has_to_be_in_queue(db_session, users_id):
        try:
            user_has_zendesk_link = db_session.execute(
                select(Users.zendesk_users_id).where(Users.id == users_id)
            ).scalar()
            if user_has_zendesk_link:
                return True
            else:
                return False

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_first_user_in_queue(db_session):
        try:
            first_agent_in_queue = db_session.execute(
                select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position)
                .where(UsersQueue.position > 0)
                .order_by(UsersQueue.position.asc())
            ).first()
            if first_agent_in_queue:
                return first_agent_in_queue
            else:
                return None

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_user_position(db_session, users_id):
        try:
            position = db_session.execute(
                select(UsersQueue.position)
                .where(UsersQueue.users_id == users_id)
            ).scalar()
            return position

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_next_user_in_queue(db_session, users_id):
        try:
            current_position = UsersQueue.get_user_position(db_session, users_id)
            next_position = int(current_position) + 1
            next_agent_in_queue = db_session.execute(
                select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position)
                .where(UsersQueue.position == next_position)
            ).first()
            if next_agent_in_queue:
                return next_agent_in_queue
            else:
                return None

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class PasswordResetRequests(Base):
    __tablename__ = 'password_reset_requests'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    users_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    uuid: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False)
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    invalidated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    @staticmethod
    def create_new_request_returning_uuid(db_session, users_id):
        new_request_obj = PasswordResetRequests(
            users_id=users_id,
            uuid=str(uuid.uuid4()),
            used_at=None,
            used=False,
            valid=True,
        )

        try:
            db_session.add(new_request_obj)
            return new_request_obj.uuid

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def is_request_valid(db_session, request_uuid):
        try:
            password_request = db_session.execute(
                select(
                    PasswordResetRequests.id,
                    PasswordResetRequests.users_id,
                    PasswordResetRequests.used,
                    PasswordResetRequests.valid,
                ).where(PasswordResetRequests.uuid == request_uuid)
            ).first()

            return password_request

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def flag_request_as_used(db_session, request_id):
        try:
            db_session.execute(
                update(PasswordResetRequests), [{
                    'id': request_id,
                    'used_at': datetime.now(),
                    'used': True,
                }],
            )

            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def invalidate_other_user_requests(db_session, request_uuid, user_id):
        try:
            db_session.execute(
                update(PasswordResetRequests)
                .values(
                    valid=False,
                    invalidated_at=datetime.now(),
                )
                .where(
                    PasswordResetRequests.uuid != request_uuid,
                    PasswordResetRequests.users_id == user_id,
                    PasswordResetRequests.valid == True,
                )
            )

            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class SchedulerLogs(Base):
    __tablename__ = 'scheduler_logs'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    users_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    uuid: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False)
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    invalidated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    @staticmethod
    def create_new_request_returning_uuid(db_session, users_id):
        new_request_obj = PasswordResetRequests(
            users_id=users_id,
            uuid=str(uuid.uuid4()),
            used_at=None,
            used=False,
            valid=True,
        )

        try:
            db_session.add(new_request_obj)
            return new_request_obj.uuid

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class ZendeskViews(Base):
    __tablename__ = 'zendesk_views'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_view_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)

    @staticmethod
    def get_views(db_session):
        try:
            views = db_session.execute(
                select(
                    ZendeskViews.id,
                    ZendeskViews.zendesk_view_id,
                    ZendeskViews.name,
                    ZendeskViews.active,
                    ZendeskViews.deleted,
                )
            ).all()

            return views

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_all_valid_views(db_session):
        try:
            views = db_session.execute(
                select(
                    ZendeskViews.id,
                    ZendeskViews.zendesk_view_id,
                    ZendeskViews.name,
                    ZendeskViews.active,
                    ZendeskViews.deleted,
                ).where(
                    ZendeskViews.active == True,
                    ZendeskViews.deleted == False,
                )
            ).all()

            return views

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_view(db_session, view_id):
        try:
            view = db_session.execute(
                select(
                    ZendeskViews.id,
                    ZendeskViews.zendesk_view_id,
                    ZendeskViews.name,
                    ZendeskViews.active,
                    ZendeskViews.deleted,
                ).where(
                    ZendeskViews.id == view_id,
                )
            ).first()

            return view

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_view_by_zendesk_id(db_session, zendesk_view_id):
        try:
            view = db_session.execute(
                select(
                    ZendeskViews.id,
                    ZendeskViews.zendesk_view_id,
                    ZendeskViews.name,
                    ZendeskViews.active,
                    ZendeskViews.deleted,
                ).where(
                    ZendeskViews.zendesk_view_id == zendesk_view_id,
                )
            ).first()

            return view

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_new_view(db_session, view):
        try:
            db_session.add(view)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def update_view(db_session, view_id, name, active, deleted):
        try:
            db_session.execute(
                update(ZendeskViews)
                .values(
                    name=name,
                    active=active,
                    deleted=deleted,
                ).where(
                    ZendeskViews.id == view_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_view(db_session, view_id):
        try:
            db_session.execute(
                update(ZendeskViews)
                .values(
                    deleted=True,
                ).where(
                    ZendeskViews.id == view_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class RoutingViews(Base):
    __tablename__ = 'routing_views'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_views_id: Mapped[int] = mapped_column(ForeignKey('zendesk_views.id'))
    zendesk_schedules_id: Mapped[int] = mapped_column(ForeignKey('zendesk_schedules.id'))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)

    @staticmethod
    def get_all_routing_views(db_session):
        try:
            views = db_session.execute(
                select(
                    RoutingViews.id,
                    RoutingViews.zendesk_views_id,
                    RoutingViews.zendesk_schedules_id,
                    RoutingViews.name,
                    RoutingViews.active,
                    RoutingViews.deleted,
                )
            ).all()

            return views

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_all_valid_routing_views(db_session):
        try:
            views = db_session.execute(
                select(
                    RoutingViews.id,
                    RoutingViews.zendesk_views_id,
                    RoutingViews.zendesk_schedules_id,
                    RoutingViews.name,
                    RoutingViews.active,
                    RoutingViews.deleted,
                ).where(
                    RoutingViews.deleted == False
                )
            ).all()

            return views

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_routing_view(db_session, routing_view_id):
        try:
            view = db_session.execute(
                select(
                    RoutingViews.id,
                    RoutingViews.zendesk_views_id,
                    RoutingViews.zendesk_schedules_id,
                    RoutingViews.name,
                    RoutingViews.active,
                    RoutingViews.deleted,
                ).where(
                    RoutingViews.id == routing_view_id,
                )
            ).first()

            return view

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_new_routing_view(db_session, routing_view):
        try:
            new_view = db_session.add(routing_view)
            return new_view

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def update_routing_view(db_session, routing_view_id, zendesk_views_id, zendesk_schedules_id, name, active, deleted):
        try:
            db_session.execute(
                update(RoutingViews)
                .values(
                    zendesk_views_id=zendesk_views_id,
                    zendesk_schedules_id=zendesk_schedules_id,
                    name=name,
                    active=active,
                    deleted=deleted,
                ).where(
                    RoutingViews.id == routing_view_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_routing_view(db_session, routing_view_id):
        try:
            db_session.execute(
                update(RoutingViews)
                .values(
                    deleted=True,
                ).where(
                    RoutingViews.id == routing_view_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def deactivate_routing_view(db_session, routing_view_id):
        try:
            db_session.execute(
                update(RoutingViews)
                .values(
                    active=False,
                ).where(
                    RoutingViews.id == routing_view_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def is_view_in_working_hours(db_session, routing_view_id):
        try:
            current_time = datetime.now().time()
            midnight_time = datetime.combine(datetime.today(), time.min).time()

            delta_time = \
                datetime.combine(date.today(), current_time) - \
                datetime.combine(date.today(), midnight_time)

            view_schedule_id = db_session.execute(
                select(RoutingViews.zendesk_schedules_id).
                where(RoutingViews.id == routing_view_id)
            ).scalar()

            if date.today().weekday() == 0:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.monday_start,
                        ZendeskSchedules.monday_end,
                    ).where(ZendeskSchedules.id == view_schedule_id)
                ).first()
                if working_hours.monday_start and working_hours.monday_end:
                    if working_hours.monday_start <= delta_time <= working_hours.monday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 1:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.tuesday_start,
                        ZendeskSchedules.tuesday_end,
                    ).where(ZendeskSchedules.id == view_schedule_id)
                ).first()
                if working_hours.tuesday_start and working_hours.tuesday_end:
                    if working_hours.tuesday_start <= delta_time <= working_hours.tuesday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 2:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.wednesday_start,
                        ZendeskSchedules.wednesday_end,
                    ).where(ZendeskSchedules.id == view_schedule_id)
                ).first()
                if working_hours.wednesday_start and working_hours.wednesday_end:
                    if working_hours.wednesday_start <= delta_time <= working_hours.wednesday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 3:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.thursday_start,
                        ZendeskSchedules.thursday_end,
                    ).where(ZendeskSchedules.id == view_schedule_id)
                ).first()
                if working_hours.thursday_start and working_hours.thursday_end:
                    if working_hours.thursday_start <= delta_time <= working_hours.thursday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 4:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.friday_start,
                        ZendeskSchedules.friday_end,
                    ).where(ZendeskSchedules.id == view_schedule_id)
                ).first()
                if working_hours.friday_start and working_hours.friday_end:
                    if working_hours.friday_start <= delta_time <= working_hours.friday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 5:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.saturday_start,
                        ZendeskSchedules.saturday_end,
                    ).where(ZendeskSchedules.id == view_schedule_id)
                ).first()
                if working_hours.saturday_start and working_hours.saturday_end:
                    if working_hours.saturday_start <= delta_time <= working_hours.saturday_end:
                        return True
                    else:
                        return False
                else:
                    return False

            elif date.today().weekday() == 6:
                working_hours = db_session.execute(
                    select(
                        ZendeskSchedules.sunday_start,
                        ZendeskSchedules.sunday_end,
                    ).where(ZendeskSchedules.id == view_schedule_id)
                ).first()
                if working_hours.sunday_start and working_hours.sunday_end:
                    if working_hours.sunday_start <= delta_time <= working_hours.sunday_end:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return None

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class RoutingViewsUsers(Base):
    __tablename__ = 'routing_views_users'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    routing_views_id: Mapped[int] = mapped_column(ForeignKey('routing_views.id'))
    users_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    @staticmethod
    def get_view_users(db_session, routing_views_id):
        try:
            view_users = db_session.execute(
                select(
                    RoutingViewsUsers.users_id,
                )
                .where(
                    RoutingViewsUsers.routing_views_id == routing_views_id
                )
            ).all()

            return view_users

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_all_views_and_users(db_session):
        try:
            all_views_and_users = db_session.execute(
                select(
                    RoutingViewsUsers.id,
                    RoutingViewsUsers.routing_views_id,
                    RoutingViewsUsers.users_id,
                )
            ).all()

            return all_views_and_users

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_new_users_in_view(db_session, routing_views_user):
        try:
            db_session.add(routing_views_user)
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_user_from_view(db_session, routing_views_id, users_id):
        try:
            db_session.execute(
                delete(
                    RoutingViewsUsers
                ).where(
                    RoutingViewsUsers.routing_views_id == routing_views_id,
                    RoutingViewsUsers.users_id == users_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_all_users_from_view(db_session, routing_views_id):
        try:
            db_session.execute(
                delete(
                    RoutingViewsUsers
                ).where(
                    RoutingViewsUsers.routing_views_id == routing_views_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class RoutingViewsGroups(Base):
    __tablename__ = 'routing_views_groups'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    routing_views_id: Mapped[int] = mapped_column(ForeignKey('routing_views.id'))
    zendesk_groups_id: Mapped[int] = mapped_column(ForeignKey('zendesk_groups.id'))

    @staticmethod
    def get_view_groups(db_session, routing_views_id):
        try:
            view_groups = db_session.execute(
                select(
                    RoutingViewsGroups.id,
                    RoutingViewsGroups.routing_views_id,
                    RoutingViewsGroups.zendesk_groups_id,
                ).where(
                    RoutingViewsGroups.routing_views_id == routing_views_id
                )
            ).all()

            return view_groups

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def get_all_views_and_groups(db_session):
        try:
            all_views_and_groups = db_session.execute(
                select(
                    RoutingViewsGroups.id,
                    RoutingViewsGroups.routing_views_id,
                    RoutingViewsGroups.zendesk_groups_id,
                )
            ).all()

            return all_views_and_groups

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_new_groups_in_view(db_session, routing_views_group):
        try:
            new_group = db_session.add(routing_views_group)
            return new_group

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_group_from_view(db_session, routing_views_id, groups_id):
        try:
            db_session.execute(
                delete(
                    RoutingViewsGroups
                ).where(
                    RoutingViewsGroups.routing_views_id == routing_views_id,
                    RoutingViewsGroups.zendesk_groups_id == groups_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_all_groups_from_view(db_session, routing_views_id):
        try:
            db_session.execute(
                delete(
                    RoutingViewsGroups
                ).where(
                    RoutingViewsGroups.routing_views_id == routing_views_id,
                )
            )
            return True

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'


class ZendeskViewsTickets(Base):
    __tablename__ = 'zendesk_views_tickets'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_tickets_id: Mapped[int] = mapped_column(ForeignKey('zendesk_tickets.id'))
    zendesk_views_id: Mapped[int] = mapped_column(ForeignKey('zendesk_views.id'))

    @staticmethod
    def get_view_tickets(db_session, zendesk_views_id):
        try:
            view_tickets = db_session.execute(
                select(
                    ZendeskViewsTickets.id,
                    ZendeskViewsTickets.zendesk_tickets_id,
                    ZendeskViewsTickets.zendesk_views_id,
                ).where(
                    ZendeskViewsTickets.zendesk_views_id == zendesk_views_id
                )
            ).all()

            return view_tickets

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_new_ticket_in_view(db_session, new_ticket_in_view):
        try:
            new_ticket = db_session.add(new_ticket_in_view)
            return new_ticket

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'
