from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_active     = db.Column(db.Boolean,     default=False)
    last_active   = db.Column(db.DateTime,    default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"

class Message(db.Model):
    __tablename__ = "messages"

    id         = db.Column(db.Integer,  primary_key=True)
    sender_id  = db.Column(db.Integer,  db.ForeignKey("user.id"), nullable=False)
    receiver_id= db.Column(db.Integer,  db.ForeignKey("user.id"), nullable=False)
    content    = db.Column(db.Text,     nullable=False)
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    delivered  = db.Column(db.Boolean,  default=False,           index=True)  # NEW

    sender   = db.relationship("User", foreign_keys=[sender_id],   backref="sent_messages")
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref="received_messages")

    def __repr__(self):
        preview = (self.content[:17] + "…") if len(self.content) > 20 else self.content
        return f"<Message {self.sender_id}→{self.receiver_id} '{preview}'>"
