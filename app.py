from flask import Flask
import config
import auth
import db
def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(auth.blueprint)

app = Flask(__name__)
register_blueprints(app)
app.config.from_object(config)
app.teardown_appcontext(db.close_database_connection)

@app.route('/')
def hello_world():
    return 'Hello, World!'
