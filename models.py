from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, engine, create_engine, delete, update, insert
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


