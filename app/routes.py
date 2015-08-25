from app import app, db
from models import User
from flask import request, jsonify, render_template
from IPython import embed

@app.route('/')
def index():
    return render_template('index.html')

#
# Users
#
@app.route('/users', methods=['GET', 'POST'])
def users_index():
    if request.method == 'GET':
        users = User.query.all()
        results = [user.to_json() for user in users]
        # for security reasons, must return a dictionary and not a top-level array
        return jsonify(users = results)
    elif request.method == 'POST':
        name = request.form['name']
        nickname = request.form['nickname']
        user = User(name, nickname)
        db.session.add(user)
        db.session.commit()
        return jsonify(message = "user added")

@app.route('/users/<int:user_id>')
def users_show(user_id):
    user = User.query.get(user_id)
    if user == None:
        return jsonify(error = "Could not find a user with id = %r" % (user_id)), 404
    return user

@app.route('/users/<int:user_id>/conversations')
def users_messages(user_id):
    pass

@app.route('/users/<int:user_id>/conversations/<int:with_user_id>')
def users_messages_with_user(user_id, with_user_id):
    pass

#
# Messages
#
@app.route('/messages')
def messages():
    return "hello, world!"

@app.route('/messages/<int:id>')
def message(id):
    return "hello, " + str(id)
