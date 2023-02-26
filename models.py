from app import db


class ZendeskTickets(db.Model):
    __tablename__ = "zendesk_tickets"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, ticket_id, subject, channel, created_at):
        self.ticket_id = ticket_id
        self.subject = subject
        self.channel = channel
        self.created_at = created_at

    def __repr__(self):
        return f'{self.id}, {self.ticket_id}, {self.subject}, {self.channel}, {self.created_at}'


class ZendeskUsers(db.Model):
    __tablename__ = "zendesk_users"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zendesk_user_id = db.Column(db.BigInteger, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    suspended = db.Column(db.Boolean, nullable=False)

    def __init__(self, zendesk_user_id, name, email, suspended):
        self.zendesk_user_id = zendesk_user_id
        self.name = name
        self.email = email
        self.suspended = suspended

    def __repr__(self):
        return f'{self.id}, {self.zendesk_user_id}, {self.name}, {self.email}, {self.suspended}'


class ZendeskGroups(db.Model):
    __tablename__ = "zendesk_groups"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zendesk_group_id = db.Column(db.BigInteger, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, zendesk_group_id, name):
        self.zendesk_group_id = zendesk_group_id
        self.name = name

    def __repr__(self):
        return f'{self.zendesk_group_id}, {self.name}'


class ZendeskGroupMemberships(db.Model):
    __tablename__ = "zendesk_group_memberships"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zendesk_user_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.BigInteger, nullable=False)
    zendesk_group_id = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.BigInteger, nullable=False)
    default = db.Column(db.Boolean, nullable=False)

    def __init__(self, zendesk_user_id, user_id, zendesk_group_id, group_id, default):
        self.zendesk_user_id = zendesk_user_id
        self.user_id = user_id
        self.zendesk_group_id = zendesk_group_id
        self.group_id = group_id
        self.default = default

    def __repr__(self):
        return f'{self.id}, {self.zendesk_user_id}, {self.group_id}, {self.default}'


class AssignedTickets(db.Model):
    __tablename__ = "assigned_tickets"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zendesk_tickets_id = db.Column(db.Integer, nullable=False)
    zendesk_users_id = db.Column(db.Integer, nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, zendesk_tickets_id, zendesk_users_id, assigned_at):
        self.zendesk_tickets_id = zendesk_tickets_id
        self.zendesk_users_id = zendesk_users_id
        self.assigned_at = assigned_at

    def __repr__(self):
        return f'{self.id}, {self.zendesk_tickets_id}, {self.zendesk_users_id}, {self.assigned_at}'
