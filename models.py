from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, create_engine, delete, update, insert
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
import datetime
from config import url_object

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
        with Session(engine) as session:
            result = session.execute(stmt)
            for row in result:
                zendesk_users_id = row[0]
                if zendesk_users_id:
                    return zendesk_users_id
            return 'null'


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
    def get_form_fields(session, form_id):
        all_fields = session.execute(
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
    def insert_one_locale(session, routes_id, zendesk_locales_id):
        new_ticket_locale = RouteTicketLocales(
            routes_id=int(routes_id),
            zendesk_locales_id=int(zendesk_locales_id),
        )
        try:
            session.add(new_ticket_locale)
            return True
        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def select_all_locales_in_a_route(session, routes_id):
        existing_record = session.execute(
            select(RouteTicketLocales.zendesk_locales_id)
            .where(RouteTicketLocales.routes_id == routes_id)
        ).all()
        if existing_record:
            return existing_record
        else:
            return None

    @staticmethod
    def check_existing_locale_in_route(session, routes_id, zendesk_locales_id):
        existing_record = session.execute(
            select(RouteTicketLocales)
            .where(RouteTicketLocales.routes_id == routes_id)
            .where(RouteTicketLocales.zendesk_locales_id == zendesk_locales_id)
        ).first()
        if existing_record:
            return True
        else:
            return False

    @staticmethod
    def delete_list_of_locales_in_route(session, routes_id, list_of_zendesk_locales_ids):
        try:
            session.execute(
                delete(RouteTicketLocales)
                .where(RouteTicketLocales.routes_id == routes_id)
                .where(RouteTicketLocales.zendesk_locales_id.in_(list_of_zendesk_locales_ids))
            )
            return True
        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_all_locales_in_route(session, routes_id):
        try:
            session.execute(
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
    def insert_one_group(session, routes_id, zendesk_groups_id):
        new_ticket_group = RouteTicketGroups(
            routes_id=int(routes_id),
            zendesk_groups_id=int(zendesk_groups_id),
        )
        try:
            session.add(new_ticket_group)
            return True
        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def insert_list_of_groups(session, routes_id, list_of_zendesk_groups_ids):
        try:
            for group in list_of_zendesk_groups_ids:
                session.execute(
                    insert(RouteTicketGroups), [
                        {'routes_id': routes_id, 'zendesk_groups_id': group}
                    ]
                )
            return True
        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def select_all_groups_in_a_route(session, routes_id):
        existing_record = session.execute(
            select(RouteTicketGroups.zendesk_groups_id)
            .where(RouteTicketGroups.routes_id == routes_id)
        ).all()
        if existing_record:
            return existing_record
        else:
            return None

    @staticmethod
    def check_existing_group_in_route(session, routes_id, zendesk_groups_id):
        existing_record = session.execute(
            select(RouteTicketGroups)
            .where(RouteTicketGroups.routes_id == routes_id)
            .where(RouteTicketGroups.zendesk_groups_id == zendesk_groups_id)
        ).first()
        if existing_record:
            return True
        else:
            return False

    @staticmethod
    def delete_list_of_groups_in_route(session, routes_id, list_of_zendesk_groups_ids):
        try:
            session.execute(
                delete(RouteTicketGroups)
                .where(RouteTicketGroups.routes_id == routes_id)
                .where(RouteTicketGroups.zendesk_groups_id.in_(list_of_zendesk_groups_ids))
            )
            return True
        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_all_groups_in_route(session, routes_id):
        try:
            session.execute(
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
    def insert_one_tag(session, routes_id, zendesk_tags_id):
        new_ticket_tag = RouteTicketTags(
            routes_id=int(routes_id),
            zendesk_tags_id=int(zendesk_tags_id),
        )
        try:
            session.add(new_ticket_tag)
            return True
        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def select_all_tags_in_a_route(session, routes_id):
        existing_record = session.execute(
            select(RouteTicketTags.zendesk_tags_id)
            .where(RouteTicketTags.routes_id == routes_id)
        ).all()
        if existing_record:
            return existing_record
        else:
            return None

    @staticmethod
    def check_existing_tag_in_route(session, routes_id, zendesk_tags_id):
        existing_record = session.execute(
            select(RouteTicketTags)
            .where(RouteTicketTags.routes_id == routes_id)
            .where(RouteTicketTags.zendesk_tags_id == zendesk_tags_id)
        ).first()
        if existing_record:
            return True
        else:
            return False

    @staticmethod
    def delete_list_of_tags_in_route(session, routes_id, list_of_zendesk_tags_ids):
        try:
            session.execute(
                delete(RouteTicketTags)
                .where(RouteTicketTags.routes_id == routes_id)
                .where(RouteTicketTags.zendesk_tags_id.in_(list_of_zendesk_tags_ids))
            )
            return True
        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def delete_all_tags_in_route(session, routes_id):
        try:
            session.execute(
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
    def get_settings(session):
        try:
            all_settings = session.execute(
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
    def update_settings(session, use_routes, routing_model, agent_backlog_limit,
                        daily_assignment_limit, hourly_assignment_limit):
        try:
            session.execute(
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
    def get_schedules(session):
        try:
            all_schedules = session.execute(
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
    def get_schedule(session, schedule_id):
        try:
            schedule = session.execute(
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
    def insert_schedule_hour(session, schedule_id, hour, start_or_end):
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
            session.execute(
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
    def update_schedule_hours(session, schedule_id, start_time, end_time):
        start_parsed_week_day = int(ZendeskSchedules.get_week_day(start_time))
        end_parsed_week_day = int(ZendeskSchedules.get_week_day(end_time))

        start_parsed_hour = ZendeskSchedules.get_hour(start_time)
        end_parsed_hour = ZendeskSchedules.get_hour(end_time)

        start_week_day_column = ZendeskSchedules.get_starting_hour_column(start_parsed_week_day)
        end_week_day_column = ZendeskSchedules.get_ending_hour_column(end_parsed_week_day)

        try:
            session.execute(
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
    def insert_schedule(session, zendesk_schedule_id, schedule_name, schedule_timezone):
        try:
            session.execute(
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
    def get_id_from_zendesk_schedule_id(session, zendesk_schedule_id):
        try:
            schedule_id = session.execute(
                select(ZendeskSchedules.id).where(ZendeskSchedules.zendesk_schedule_id == zendesk_schedule_id)
            ).scalar()
            return schedule_id
        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'

    @staticmethod
    def check_for_existing_schedule(session, zendesk_schedule_id):
        try:
            schedule_id = session.execute(
                select(ZendeskSchedules.id).where(ZendeskSchedules.zendesk_schedule_id == zendesk_schedule_id)
            ).first()
            if schedule_id:
                return True
            else:
                return False
        except (IntegrityError, FlushError) as error:
            error_info = error.orig.args
            return f'There was an error: {error_info}'
