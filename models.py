from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, Boolean, ForeignKey, DateTime, select, engine, create_engine
from sqlalchemy.sql import func
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


class RouteTicketsTags(Base):
    __tablename__ = "route_tickets_tags"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    routes_id: Mapped[int] = mapped_column(ForeignKey("routes.id"))
    zendesk_tags_id: Mapped[int] = mapped_column(ForeignKey("zendesk_tags.id"))

    def __repr__(self) -> str:
        return f'{self.id}, {self.routes_id}, {self.zendesk_tags_id}'
