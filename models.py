from app import db


class ZendeskTickets(db.Model):
    __tablename__ = "zendesk_tickets"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<ticket_id %r' % self.ticket_id


class ZendeskUsers(db.Model):
    __tablename__ = "zendesk_users"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zendesk_user_id = db.Column(db.BigInteger, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    suspended = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<name %r' % self.name


class ZendeskGroupMemberships(db.Model):
    __tablename__ = "zendesk_group_memberships"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zendesk_user_id = db.Column(db.BigInteger, nullable=False)
    group_id = db.Column(db.BigInteger, nullable=False)
    default = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<user_id %r' % self.zendesk_user_id
