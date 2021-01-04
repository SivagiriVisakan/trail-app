from flask import Flask, render_template, g, request, flash
from flask_bcrypt import Bcrypt, generate_password_hash

import auth
import api
import config
import db
import organisation
import os

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

# Create the upload folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/profile', methods=['GET','POST'])
@auth.login_required
def profile():

	user = g.user
	username = user["username"]
	db_conn = db.get_database_connection()

	with db_conn.cursor() as cursor:
		sql = 'SELECT * FROM `user` WHERE `username`=%s'
		cursor.execute(sql, (username, ))
		profile = cursor.fetchone()

	if request.method == "GET":
			
		return render_template('profile.html',profile=profile)

	elif request.method == "POST":

		email = request.form.get("email", None)

		first_name = request.form.get("first_name", None)

		last_name = request.form.get("last_name", None)

		password = request.form.get("password", None)

		if email and first_name and last_name  and password:
			password_hash = generate_password_hash(password)
			with db_conn.cursor() as cursor:
				sql = 'UPDATE `user` SET `email`=%s, `first_name`=%s, `last_name`=%s, `password`=%s WHERE `user`.`username`=%s'
				cursor.execute(sql, (email, first_name, last_name, password_hash, username, ))
				db_conn.commit()
			return render_template('profile.html',profile=profile)

		else:
			if not email:
				flash("Enter email", "danger")
			if not first_name:
				flash("Enter first_name", "danger")
			if not last_name:
				flash("Enter last_name", "danger")
			if not password:
				flash("Enter password", "danger")
			return render_template('profile.html',profile=profile)