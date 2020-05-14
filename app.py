from flask import Flask, render_template
from flask_bcrypt import Bcrypt

import auth
import api
import config
import db
import organisation
import os

UPLOAD_FOLDER = 'static/uploads'


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(auth.blueprint)
    app.register_blueprint(api.blueprint)
    app.register_blueprint(organisation.blueprint)

def register_extensions(app):
    """Register Flask extensions."""
    bcrypt = Bcrypt(app)
    return None


app = Flask(__name__)
register_blueprints(app)
register_extensions(app)
app.config.from_object(config)
app.teardown_appcontext(db.close_database_connection)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
