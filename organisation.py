import json 
import datetime 

from flask import Blueprint, request, render_template, flash, g

import db
from utils import check_missing_keys
import auth
from werkzeug.utils import secure_filename
import os
import app

blueprint = Blueprint('organisation', __name__, url_prefix='/organisation')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blueprint.route('')
@auth.login_required
def organisation():
	return render_template('organisation/organisation.html', user=g.user)


@blueprint.route('/<string:slug>')
@auth.login_required
def view_organisation():
	return redirect(url_for('organisation/view_organisation.html'))

def get_slug(slug):
	db_conn = db.get_database_connection()
	with db_conn.cursor() as cursor:
		sql = 'SELECT * FROM `workspace` WHERE `slug`=%s'
		cursor.execute(sql, (slug, ))
		result = cursor.fetchone()
		return result


@blueprint.route('/new_organisation',methods=["GET","POST"])
@auth.login_required
def new_organisation():
	if request.method == "GET":
		return render_template('organisation/new_organisation.html')

	elif request.method == "POST":

		slug = request.form.get("slug", None)
		if len(slug) > 15:
			flash("slug should not exceed 15 characters", "danger")
			return render_template('organisation/new_organisation.html')

		name = request.form.get("name", None)
		if len(name) > 15:
			flash("name should not exceed 15 characters", "danger")
			return render_template('organisation/new_organisation.html')

		if 'logo' not in request.files:
			flash("No file part", "danger")
			return render_template('organisation/new_organisation.html')

		logo = request.files['logo']

		if slug and name and logo.filename:
			_slug = get_slug(slug)
			if _slug is not None:
				flash("Slug already exists","danger")
				return render_template('organisation/new_organisation.html')
			else:
				if logo.filename and allowed_file(logo.filename):
					filename = secure_filename(logo.filename)
					logo.save(os.path.join(app.app.config['UPLOAD_FOLDER'], filename))
					db_conn = db.get_database_connection()
					with db_conn.cursor() as cursor:
						cursor.execute("INSERT INTO `workspace`(`slug`,`name`,`logo`) Values (%s, %s, %s)", (slug, name, filename))
						db_conn.commit()
						return redirect(url_for('auth.my_details'))
				else:
					flash("logo is not a image", "danger")
					return render_template('organisation/new_organisation.html')
		else:
			if not slug:
				flash("Enter slug", "danger")
			if not name:
				flash("Enter name", "danger")
			if not logo.filename:
				flash("Select file", "danger")

			return render_template('organisation/new_organisation.html')
