from flask import Flask

import auth

def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(auth.blueprint)

app = Flask(__name__)
register_blueprints(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'