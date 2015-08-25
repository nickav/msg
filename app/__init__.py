# Import flask and template operators
from flask import Flask, Response, render_template
from flask.ext.sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__, static_url_path='')
# Configure flask
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server(error):
    return render_template('500.html'), 500

# Import all models
from app import models
# Build the database (using SQLAlchemy):
db.create_all()

# Set up routes
from app import routes
