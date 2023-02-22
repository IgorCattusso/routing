from app import db


class zendesk_tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<ticket_id %r' % self.ticket_id
