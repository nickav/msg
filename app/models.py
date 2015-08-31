from app import db
from datetime import datetime
from collections import OrderedDict
from sqlalchemy.ext.declarative import declared_attr

"""
    Base class gives all inheriting db.Models:
    a default __tablename__, id Column, and to_json method.
"""
class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    id = db.Column(db.Integer, primary_key=True)

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class User(db.Model, Base):
    name = db.Column(db.String(50), unique=True)
    nickname = db.Column(db.String(50))
    created_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    received_messages = db.relationship('Message', backref='receiver', foreign_keys='Message.to_id')
    sent_messages = db.relationship('Message', backref='sender', foreign_keys='Message.from_id')

    def __init__(self, name, nickname=None):
        self.name = name.lower()
        if nickname is None:
            nickname = name
        self.nickname = nickname

    def __repr__(self):
        return '<User name:%r nickname:%r>' % (self.name, self.nickname)

class Message(db.Model, Base):
    from_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.String(256))
    created_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    delivered_time = db.Column(db.DateTime(timezone=True))
    read_time = db.Column(db.DateTime(timezone=True))
    read = db.Boolean()

    def __init__(self, from_id, to_id, content=None):
        self.from_id = from_id
        self.to_id = to_id
        self.content = content

    def mark_read(commit=False):
        read = True
        read_time = datetime.now()
        if commit:
            db.session.commit()

    def __repr__(self):
        trimmed_content = (self.content[:20] + '...') if len(self.content) > 20 else self.content
        return '<Message %r>' % (self.content)
