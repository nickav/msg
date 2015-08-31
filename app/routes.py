from app import app, db
from models import User, Message
from flask import g, request, redirect, jsonify, render_template
from IPython import embed
from sqlalchemy.sql import text

@app.before_request
def strip_trailing_slash():
    if request.url != request.url_root and request.url[-1] == '/':
        return redirect(request.url[:-1], code=301)

@app.route('/')
def index():
    return render_template('index.html')

#
# Users
#
@app.route('/users', methods=['GET', 'POST'])
def users_index():
    if request.method == 'POST':
        name = request.form['name']
        nickname = request.form.get('nickname')
        if nickname is None:
            nickname = name
        user = User(name, nickname)
        db.session.add(user)
        db.session.commit()
        return jsonify(status = "User created successfully", user_id = user.id)
    else:
        users = User.query.all()
        results = [user.to_json() for user in users]
        # for security reasons, must return a dictionary and not a top-level array
        return jsonify(users = results)

@app.route('/users/<int:user_id>')
def users_show(user_id):
    user = User.query.get(user_id)
    if user == None:
        return jsonify(error = "Could not find a user with id = %r" % (user_id)), 404

    result = user.to_json()
    result['sent_messages'] = [m.to_json() for m in user.sent_messages]
    result['received_messages'] = [m.to_json() for m in user.received_messages]
    return jsonify(result)

@app.route('/users/<list:user_ids>')
def users_bulk(user_ids):
    # sanitize
    user_ids = [int(user_id) for user_id in user_ids]

    results = db.session.query(User).filter(User.id.in_((user_ids))).all()
    results = [result.to_json() for result in results]
    return jsonify(users=results)

@app.route('/users/<int:user_id>/conversations')
def users_messages(user_id):
    conn = db.session.connection()
    sql = text("""SELECT from_id, to_id from messages
                WHERE to_id = :id OR from_id = :id
                GROUP BY from_id, to_id
                ORDER BY created_time DESC""")
    results = conn.execute(sql, id=user_id).fetchall()

    has_convo_with_self = False
    for result in results:
        if result[0] == user_id and result[1] == user_id:
            has_convo_with_self = True

    seen = set()
    seen_add = seen.add
    flatten = [item for sublist in results for item in sublist if not (item in seen or seen_add(item))]
    if not has_convo_with_self:
        flatten.remove(user_id)

    return jsonify(conversation_ids = flatten)

@app.route('/users/<int:user_id>/conversations/<int:with_user_id>')
def users_messages_with_user(user_id, with_user_id):
    conn = db.session.connection()
    sql = text("""SELECT * from messages
                WHERE (to_id = :id AND from_id = :other_id)
                   OR (to_id = :other_id AND from_id = :id)
                GROUP BY from_id, to_id
                ORDER BY created_time DESC""")
    results = db.session.query(Message).from_statement(sql).params(id=user_id, other_id=with_user_id).all()
    messages = [message.to_json() for message in results] 
    return jsonify(messages = messages)

#
# Messages
#
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        from_id = request.form['from_id']
        to_id = request.form['to_id']
        content = request.form['content']
        message = Message(from_id, to_id, content)
        db.session.add(message)
        db.session.commit()
        return jsonify(status = "Message created successfully", message_id=message.id)
    else:
        messages = Message.query.all()
        results = [message.to_json() for message in messages]
        return jsonify(messages = results)

@app.route('/messages/<int:id>')
def message(id):
    message = Message.query.get(id)
    if message is None:
        return jsonify(error = "Could not find a message with id = %r" % (id)), 404

    return jsonify(message.to_json())

