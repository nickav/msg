#!/usr/bin/env python
import sys

from flask import *
from app import *
from app.models import *

if db.session.query(User).count() != 0:
    print "Database already seeded!"
    sys.exit(1)

# Users
users = [
    ['nick', 'Nick Aversano'],
    ['ben', 'Ben Bederson'],
    ['tak', 'Tak Yeon Lee'],
    ['halley', 'Halley Weitzman'],
    ['cem', 'Cem Karan'],
    ['andrej', 'Andrej Rasevic'],
]

# create all users
for user in users:
    password = user[0] + 'password'
    user = User(user[0], password, user[1])
    db.session.add(user)

# Messages
messages = [
    # nick & ben
    [1, 2, 'hello!'],
    [2, 1, 'what\'s up?'],
    [1, 2, 'not much, just working on the Messaging API for the thrid credit...'],
    [2, 1, 'awesome, sounds good. see you Wednesday'],
    # ben & tak
    [2, 3, 'hey tak!'],
    [3, 2, 'hi'],
    # tak & nick
    [3, 1, 'how are things going?'],
    [1, 3, 'things are going well!'],
]

# create all messsages
for message in messages:
    m = Message(message[0], message[1], message[2])
    db.session.add(m)

db.session.commit()

print "Seeds created successfully."
