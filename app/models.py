from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    nickname = db.Column(db.String(50))
    created_time = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User name:%r, nickname:%r>' % (self.name, self.nickname)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(256))
    sent_time = db.Column(db.DateTime(timezone=True), default=datetime.now())
    delivered_time = db.Column(db.DateTime(timezone=True))
    received_time = db.Column(db.DateTime(timezone=True))
    read = db.Boolean()
    from_user = db.relationship("User", backref=db.backref('users', order_by=id))
    to_user = db.relationship("User", backref=db.backref('users', order_by=id))

    def __init__(self, content=None):
        self.content = content

    def __repr(self):
        trimmed_content = (self.content[:20] + '...') if len(self.content) > 20 else self.content
        return '<Message %r>' % (self.content)
