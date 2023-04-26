from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, delete, update, insert
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
import datetime
from sqlalchemy import create_engine
from config import url_object
from datetime import datetime

engine = create_engine(url_object)


class Base(DeclarativeBase):
    pass


class ZendeskTickets(Base):
    __tablename__ = "zendesk_tickets"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(nullable=False)
    subject: Mapped[str] = mapped_column(String(150), nullable=False)
    channel: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f'{self.id}, {self.ticket_id}, {self.subject}, {self.channel}, {self.created_at}'


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
    def get_zendesk_users_id(user_id):
        stmt = select(ZendeskUsers.id).where(ZendeskUsers.zendesk_user_id == user_id)
        with Session(engine) as db_session:
            result = db_session.execute(stmt)
            for row in result:
                zendesk_users_id = row[0]
                if zendesk_users_id:
                    return zendesk_users_id
            return 'null'

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


class AssignedTickets(Base):
    __tablename__ = "assigned_tickets"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_tickets_id: Mapped[int] = mapped_column(ForeignKey("zendesk_tickets.id"))
    zendesk_users_id: Mapped[int] = mapped_column(ForeignKey("zendesk_users.id"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_tickets_id}, {self.zendesk_users_id}, {self.assigned_at}'


class ZendeskUserBacklog(Base):
    __tablename__ = "zendesk_user_backlog"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_users_id: Mapped[int] = mapped_column(ForeignKey("zendesk_users.id"))
    ticket_id: Mapped[int] = mapped_column(nullable=False)
    ticket_status: Mapped[str] = mapped_column(String(100), nullable=False)
    ticket_level: Mapped[str] = mapped_column(String(100))

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_users_id}, {self.ticket_id}, ' \
               f'{self.ticket_status}, {self.ticket_level}'


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
    recipient_type: Mapped[int] = mapped_column(nullable=False)  # 0 = user | 1 = group

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
    use_routes: Mapped[bool] = mapped_column(Boolean, nullable=False)
    routing_model: Mapped[int] = mapped_column(nullable=False)
    agent_backlog_limit: Mapped[int] = mapped_column(nullable=False)
    daily_assignment_limit: Mapped[int] = mapped_column(nullable=False)
    hourly_assignment_limit: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.use_routes}, {self.routing_model}, ' \
               f'{self.agent_backlog_limit}, {self.daily_assignment_limit}'

    @staticmethod
    def get_settings(db_session):
        try:
            all_settings = db_session.execute(
                select(
                    GeneralSettings.use_routes,
                    GeneralSettings.routing_model,
                    GeneralSettings.agent_backlog_limit,
                    GeneralSettings.daily_assignment_limit,
                    GeneralSettings.hourly_assignment_limit,
                )
            ).all()
            return all_settings

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def update_settings(db_session, use_routes, routing_model, agent_backlog_limit,
                        daily_assignment_limit, hourly_assignment_limit):
        try:
            db_session.execute(
                update(GeneralSettings)
                .values(
                    use_routes=use_routes,
                    routing_model=routing_model,
                    agent_backlog_limit=agent_backlog_limit,
                    daily_assignment_limit=daily_assignment_limit,
                    hourly_assignment_limit=hourly_assignment_limit,
                )
            )
            return True

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
            ).first()
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
                    {"id": schedule_id, start_week_day_column: start_parsed_hour, end_week_day_column: end_parsed_hour}
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
        hour = f'{hour:02d}:{minute:02d}'
        return hour

    @staticmethod
    def insert_schedule(db_session, zendesk_schedule_id, schedule_name, schedule_timezone):
        try:
            db_session.execute(
                insert(ZendeskSchedules)
                .values(zendesk_schedule_id=zendesk_schedule_id,
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
                select(ZendeskSchedules).where(ZendeskSchedules.zendesk_schedule_id == zendesk_schedule_id)
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
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    authenticated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    routing_status: Mapped[int] = mapped_column(nullable=False)  # 0 = offline | 1 = online | 2 = away
    zendesk_users_id: Mapped[int] = mapped_column(ForeignKey('zendesk_users.id'))
    zendesk_schedules_id: Mapped[int] = mapped_column(ForeignKey('zendesk_schedules.id'))
    latam_user: Mapped[int] = mapped_column(nullable=False)  # 0 = no | 1 = yes | 2 = both

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
                    ZendeskUsers.zendesk_user_id,
                    Users.name,
                    Users.email,
                    Users.active,
                    Users.zendesk_users_id,
                    Users.zendesk_schedules_id,
                    Users.latam_user,
                ).where(Users.id == user_id)
                .join(ZendeskUsers, isouter=True)
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
    def insert_new_user(db_session, name, email, active, zendesk_users_id, zendesk_schedules_id, latam_user):
        new_user = Users(
            name=name,
            email=email,
            password='',
            active=active,
            deleted=False,
            authenticated=0,
            routing_status=0,
            zendesk_users_id=zendesk_users_id,
            zendesk_schedules_id=zendesk_schedules_id,
            latam_user=latam_user,
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
    def update_user(db_session, user_id, name, email, active, zendesk_users_id, zendesk_schedules_id, latam_user):
        try:
            db_session.execute(
                update(Users), [{
                    'id': user_id,
                    'name': name,
                    'email': email,
                    'active': active,
                    'zendesk_users_id': zendesk_users_id,
                    'zendesk_schedules_id': zendesk_schedules_id,
                    'latam_user': latam_user,
                }],
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
    type: Mapped[int] = mapped_column(nullable=False)  # 0 = new_ticket
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received: Mapped[bool] = mapped_column(Boolean, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    @staticmethod
    def get_next_pending_user_notification(db_session, user_id):
        try:
            notification = db_session.execute(
                select(
                    Notifications.id,
                    Notifications.type,
                    Notifications.content,
                    Notifications.url,
                ).where(Notifications.users_id == user_id)
                 .where(Notifications.sent == 0)
                 .order_by(Notifications.id)
            ).first()
            return notification

        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def create_notification(db_session, user_id, notification_type, content):
        new_notification = Notifications(
            users_id=user_id,
            type=notification_type,
            content=content,
            # created_at → Not needed, since the server has a default as func.now()
            sent=False,
            received=False,
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


class UsersQueue(Base):
    __tablename__ = 'users_queue'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    users_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)  # 0 = not in queue
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @staticmethod
    def is_user_alread_in_queue(db_session, users_id):
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
            print('current_user: ' + str(current_user))

            if current_user:
                users_ahead_of_current_user = db_session.execute(
                    select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).where(
                        UsersQueue.position > current_user.position)
                ).all()
                for user in users_ahead_of_current_user:
                    print('users_ahead_of_current_user: ' + str(user.id))

                last_user_in_the_queue = db_session.execute(
                    select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).order_by(UsersQueue.position.desc())
                ).first()
                print('last_user_in_the_queue: ' + str(last_user_in_the_queue.id))

                ''' Get the users ahead of the current user one position down '''
                for user in users_ahead_of_current_user:
                    if user.position != 1:
                        db_session.execute(
                            update(UsersQueue), [{
                                'id': user.id,
                                'position': user.position - 1,
                                'updated_at': datetime.now(),
                            }],
                        )

                ''' Get current user to the end of the queue '''
                if current_user.position != last_user_in_the_queue.position and last_user_in_the_queue.position != 0:
                    db_session.execute(
                        update(UsersQueue), [{
                            'id': current_user.id,
                            'position': last_user_in_the_queue.position + 1,
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
            print('current_user: ' + str(current_user))

            if current_user:
                last_user_in_the_queue = db_session.execute(
                    select(UsersQueue.id, UsersQueue.users_id, UsersQueue.position).order_by(UsersQueue.position.desc())
                ).first()
                print('last_user_in_the_queue: ' + str(last_user_in_the_queue.id))

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
