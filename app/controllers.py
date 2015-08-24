from flask import render_template
from flask_restful import Resource

class Message(Resource):
    def get(self):
        return "hello, world"

class User(Resource):
    def get(self):
        return render_template('index.html')
