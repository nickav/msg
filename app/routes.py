from app import app, db
from models import User, Message
from flask import g, request, redirect, jsonify, render_template, abort, make_response
from IPython import embed
from sqlalchemy.sql import text, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime

# Force URLs to not end with a slash
@app.before_request
def strip_trailing_slash():
    if request.url != request.url_root and request.url[-1] == '/':
        return redirect(request.url[:-1], code=301)

# Render API documentation
@app.route('/')
def index():
    return render_template('index.html', title='Messaging API')

#
# Users
#
@app.route('/users', methods=['GET'])
def users_index():
    """
    List All Users 

    :returns: an Array of `Users <#users>`_

    **Example Request**:

    * `/users </users>`_
    """
    users = User.query.all()
    results = [user.to_json() for user in users]
    # for security reasons, must return a dictionary and not a top-level array
    return jsonify(users = results)

@app.route('/users', methods=['POST'])
def users_create():
    """
    Create a New User

    :param str name: the username. Must be unique and consist solely of lowercase letters, numbers and underscores
    :param str password: the password. Must be at least 8 characters long
    :param optional full_name: the full name of the user. For example, "John Doe"
    :raises 400: if any required parameters are omitted or an error occurs
    
    :returns: the user_id of the user created
    """
    name, password = require_params('name', 'password')
    full_name = request.form.get('full_name') or name

    if len(password) < 8:
        return jsonify(error = "Password must be at least 8 characters long."), 400

    user = User(name, password, full_name)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError, e:
        return jsonify(error = "A user with username '" + name + "' already exists!"), 409
    except SQLAlchemyError, e:
        return jsonify(error = str(e)), 400
    return jsonify(message = "User '%r' created successfully" % (user.name), user_id = user.id)

@app.route('/users/login', methods=['POST'])
def users_authenticate():
    """
    Login a user

    Verifies there is a valid username and password on the messaging server.

    :param str name: the username
    :param str password: the password
    :raises 400: if the login credentials are invalid or username/password is empty
    
    :returns: the `user object <#users>`_ on the messaging server
    """
    name, password = require_params('name', 'password')

    user = User.query.filter_by(name=name).first()
    if (user and user.check_password(password)):
        return jsonify(user.to_json())

    return jsonify(error = "Invalid username or password."), 400

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """
    Show a User

    :param int user_id: the integer id of the user
    :returns: a User object
    :raises 404: if the User could not be found

    **Example Requests**:

    * `/users/1 </users/1>`_
    * `/users/2 </users/2>`_

    **Example Response**:

    .. sourcecode:: json

        {
            "created_time": "Tue, 25 Aug 2015 18:30:27 GMT",
            "id": 1,
            "name": "nick",
            "full_name": "Nick Aversano",
            "received_messages": [],
            "sent_messages": []
        }

    """
    user = find_user(user_id)
    result = user.to_json()
    result['sent_messages'] = [m.to_json() for m in user.sent_messages]
    result['received_messages'] = [m.to_json() for m in user.received_messages]
    return jsonify(result)

@app.route('/users/<list:user_ids>')
def users_bulk(user_ids):
    """
    Show Multiple Users

    **Example Requests**:

    * `/users/1,2 </users/1,2>`_
    * `/users/1,2,3,4,5,6 </users/1,2,3,4,5,6>`_

    :param list user_ids: a comma-separated list of user ids
    :returns: an Array of `Users <#users>`_
    """
    # sanitize
    user_ids = int_list(user_ids)
    results = db.session.query(User).filter(User.id.in_((user_ids))).all()
    if (len(results) == 0):
        results = db.session.query(User).filter(User.name.in_((user_ids))).all()
    results = [result.to_json() for result in results]
    return jsonify(users=results)

@app.route('/users/<int:user_id>/conversations')
def users_conversations(user_id):
    """
    Show All Conversations a User Has
    
    :param int user_id: the user_id
    :returns: an Array of conversations this user has with other users (or herself) ordered by most recent conversations
    :raises 404: if the user could not be found

    **Example Requests**:

    * `/users/1/conversations </users/1/conversations>`_
    * `/users/2/conversations </users/2/conversations>`_

    **Example Response**:

    .. sourcecode:: json

        {
            "conversations": [
                {
                    "last_message": "hi",
                    "full_name": "Tak Yeon Lee",
                    "read": true,
                    "sent_time": "2015-10-14 14:10:52.953327",
                    "user_id": 3
                },
                {
                    "last_message": "awesome, sounds good. see you Wednesday",
                    "full_name": "Nick Aversano",
                    "read": true,
                    "sent_time": "2015-10-14 14:10:52.953083",
                    "user_id": 1
                }
            ]
        }
    """
    # verify user exists
    find_user(user_id)

    conn = db.session.connection()
    sql = text("""SELECT from_id, to_id, content, sent_time, read_time,
                         u1.full_name as from_full_name, u2.full_name as to_full_name
                from messages
                LEFT JOIN users AS u1 ON u1.id = from_id
                LEFT JOIN users AS u2 ON u2.id = to_id
                WHERE to_id = :id OR from_id = :id
                GROUP BY from_id, to_id
                ORDER BY sent_time DESC""")
    results = conn.execute(sql, id=user_id).fetchall()

    seen = set()
    conversations = []
    for result in results:
        uid = int(result['from_id'] if result['from_id'] != user_id else result['to_id'])

        # make sure we only list each conversation once
        if (uid in seen):
            continue

        # add the latest message as a conversation
        full_name = (result['from_full_name'] if result['from_id'] != user_id else result['to_full_name'])
        read = (result['from_id'] == user_id or not result['read_time'] is None)
        conversation = {
                "user_id": uid,
                "full_name": full_name,
                "last_message": result['content'],
                "read": read,
                "sent_time": result['sent_time']
        }
        conversations.append(conversation)
        seen.add(uid)

    return jsonify(conversations = conversations)

@app.route('/users/<int:user_id>/conversations/<int:with_user_id>')
def users_conversations_with_user(user_id, with_user_id):
    """
    `Show a Conversation Between Two Users </users/1/conversations/2>`_

    Shows all the messages sent between the two users `user_id` and `with_user_id` (can be empty if the users have not sent each other messages yet).

    :param int user_id: the first user_id
    :param int with_user_id: the second user_id
    :returns: an Array of `Messages <#id5>`_

    **Example Requests**:

    * `/users/1/conversations/2 </users/1/conversations/2>`_
    * `/users/2/conversations/3 </users/2/conversations/3>`_

    """
    # verify users exist
    find_user(user_id)
    find_user(with_user_id)

    conn = db.session.connection()
    sql = text("""SELECT * from messages
                WHERE (to_id = :id AND from_id = :other_id)
                   OR (to_id = :other_id AND from_id = :id)
                ORDER BY sent_time ASC""")
    results = db.session.query(Message).from_statement(sql).params(id=user_id, other_id=with_user_id).all()
    
    if not results:
        return jsonify(messages = list())

    # update the read_time for messages sent to user_id
    # because this endpoint is public, we don't actually know who is reading this message
    # but for simplicity, mark it as read anyway
    for message in results:
        if (message.to_id == user_id and not message.is_read()):
            message.mark_read()

    if db.session.dirty:
        db.session.commit()

    messages = [message.to_json() for message in results] 
    return jsonify(messages = messages)

#
# Messages
#
@app.route('/messages', methods=['GET'])
def messages():
    """
    Get All Messages

    Gets all messages sent on this server.

    :returns: an Array of `Messages <#id5>`_

    **Example Request**:

    * `/messages </messages>`_
    """
    messages = Message.query.all()
    results = [message.to_json() for message in messages]
    return jsonify(messages = results)

@app.route('/messages', methods=['POST'])
def messages_create():
    """
    Create a New Message

    :param int from_id: the User id the message is being sent from 
    :param int to_id: the User id to send to
    :param str content: the message
    :param str password: the password for user with id from_id
    :raises 400: if any of the above parameters are omitted, if the password is invalid or no user exists with from_id and to_id
    
    :returns: the user_id of the user created
    """
    from_id, to_id, content, password = require_params('from_id', 'to_id', 'content', 'password')

    # authenticate user
    user = find_user(from_id)
    if not user.check_password(password):
        return jsonify(error = "Invalid password"), 400

    # check if to_id exists
    # TODO add FK constraint on Messages model and use try catch below
    find_user(to_id)

    message = Message(from_id, to_id, content)
    db.session.add(message)
    db.session.commit()
    return jsonify(message = "Message created successfully", message_id=message.id)

@app.route('/messages/<int:message_id>')
def message(message_id):
    """
    Show a Message

    :param int message_id: the integer id of the message
    :returns: a Message object
    :raises 404: if the Message could not be found

    **Example Requests**:

    * `/messages/1 </messages/1>`_
    * `/messages/2 </messages/2>`_

    **Example Response**:

    .. sourcecode:: json

        {
            "content": "hey!",
            "delivered_time": null,
            "from_id": 1,
            "id": 1,
            "read_time": null,
            "sent_time": "Tue, 25 Aug 2015 18:30:27 GMT",
            "to_id": 2
        }
    """
    message = Message.query.get(message_id)
    if message is None:
        return jsonify(error = "Could not find a message with id = %r" % (message_id)), 404

    return jsonify(message.to_json())

@app.route('/messages/<list:message_ids>')
def messages_bulk(message_ids):
    """
    Show Multiple Messages

    :param list message_ids: a comma-separated list of message ids

    :returns: an Array of `Messages <#id5>`_

    **Example Requests**:

    * `/messages/1,2 </messages/1,2>`_
    * `/messages/1,2,3,4 </messages/1,2,3,4>`_
    * `/messages/2, </messages/2,>`_ - force array response with trailing comma
    """
    # sanitize
    message_ids = int_list(message_ids)

    results = db.session.query(Message).filter(Message.id.in_((message_ids))).all()
    results = [result.to_json() for result in results]
    return jsonify(messages=results)

# Gets a user or aborts app with 404 if not found
def find_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(make_response(jsonify(error = "Could not find a user with id = %r" % (user_id)), 404))
    return user

# Given a list of strings, returns a list of corresponding integers
def int_list(ids):
    try:
        ids = [int(id) for id in ids]
    except ValueError, e:
        pass
    return ids

# Checks if each string in params is defined on request.form or aborts the application
# Returns a list of values for each parameter keys
def require_params(*params):
    missing = list()
    for param in params:
        if request.form.get(param) is None:
            missing.append(param)

        yield request.form.get(param)

    if missing:
        s = ('' if (len(missing) < 2) else 's')
        error_msg = "Missing " + str(len(missing)) + " parameter" + s + "."
        abort(make_response(jsonify(error = error_msg, missing_parameters = missing), 400))

