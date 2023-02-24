from app import db


class zendesk_tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<ticket_id %r' % self.ticket_id


class zendesk_users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zendesk_user_id = db.Column(db.BigInteger, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    suspended = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<ticket_id %r' % self.name
