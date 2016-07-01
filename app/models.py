from app import db
from datetime import datetime
from collections import OrderedDict
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.security import generate_password_hash, check_password_hash
import re

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
    full_name = db.Column(db.String(50))
    created_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    received_messages = db.relationship('Message', backref='receiver', foreign_keys='Message.to_id')
    sent_messages = db.relationship('Message', backref='sender', foreign_keys='Message.from_id')

    def __init__(self, name, password, full_name=None):
        # sanitize string, forcing lower-alphanumeric
        self.name = re.sub(r'[^0-9a-zA-Z_]+', '', name.lower())
        self.set_password(password)
        self.full_name = full_name or name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User name:%r full_name:%r>' % (self.name, self.full_name)

    def to_json(self):
        return { 'id': self.id, 'name': self.name, 'full_name': self.full_name, 'created_time': self.created_time }

class Message(db.Model, Base):
    from_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.String(256))
    sent_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    read_time = db.Column(db.DateTime(timezone=True))

    def __init__(self, from_id, to_id, content=None):
        self.from_id = from_id
        self.to_id = to_id
        self.content = content

    def mark_read(self, commit=False):
        self.read_time = datetime.utcnow()
        if commit:
            db.session.commit()

    def is_read(self):
        return self.read_time != None

    def __repr__(self):
        trimmed_content = (self.content[:20] + '...') if len(self.content) > 20 else self.content
        return '<Message id:%r content:%r>' % (self.id, self.content)
