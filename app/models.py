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
    created_time = db.Column(db.DateTime(timezone=True), default=datetime.now())

    def __init__(self, name=None, nickname=None):
        self.name = name
        self.nickname = nickname

    def __repr__(self):
        return '<User name:%r nickname:%r>' % (self.name, self.nickname)

class Message(db.Model, Base):
    content = db.Column(db.String(256))
    sent_time = db.Column(db.DateTime(timezone=True), default=datetime.now())
    delivered_time = db.Column(db.DateTime(timezone=True))
    received_time = db.Column(db.DateTime(timezone=True))
    read = db.Boolean()
    #from_user = db.relationship("User", backref=db.backref('users', order_by=id))
    #to_user = db.relationship("User", backref=db.backref('users', order_by=id))

    def __init__(self, content=None):
        self.content = content

    def __repr(self):
        trimmed_content = (self.content[:20] + '...') if len(self.content) > 20 else self.content
        return '<Message %r>' % (self.content)
