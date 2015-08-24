from app import app, api
from flask import render_template
from app.controllers import Message, User

@app.route('/')
def index():
    return render_template('index.html')

api.add_resource(Message, '/messages')
api.add_resource(User, '/users')
