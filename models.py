from app import db
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean


class Base(DeclarativeBase):
    pass


class ZendeskTickets(Base):
    __tablename__ = "zendesk_tickets"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

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


class ZendeskGroups(Base):
    __tablename__ = "zendesk_groups"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_group_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __repr__(self) -> str:
        return f'{self.zendesk_group_id}, {self.name}'


class ZendeskGroupMemberships(Base):
    __tablename__ = "zendesk_group_memberships"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    zendesk_user_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    zendesk_group_id: Mapped[int] = mapped_column(nullable=False)
    group_id: Mapped[int] = mapped_column(nullable=False)
    default: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_user_id}, {self.group_id}, {self.default}'


class AssignedTickets(Base):
    __tablename__ = "assigned_tickets"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zendesk_tickets_id = db.Column(db.Integer, nullable=False)
    zendesk_users_id = db.Column(db.Integer, nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}, {self.zendesk_tickets_id}, {self.zendesk_users_id}, {self.assigned_at}'
