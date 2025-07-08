from datetime import datetime
from core.control.database import db

class Message(db.Model):
    __tablename__ = "messages"

    id        = db.Column(db.Integer, primary_key=True)
    sender    = db.Column(db.String(80),  nullable=False)
    receiver  = db.Column(db.String(80),  nullable=False)
    content   = db.Column(db.Text,        nullable=False)
    timestamp = db.Column(db.DateTime,    default=datetime.utcnow, index=True)

    def __repr__(self) -> str:           # For debugging
        preview = (self.content[:17] + "…") if len(self.content) > 20 else self.content
        return f"<Message {self.sender}→{self.receiver} '{preview}'>"
