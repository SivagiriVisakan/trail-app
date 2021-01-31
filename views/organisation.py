import os

import app
import helpers.db as db
from controllers.organisation import set_active_org_project
from flask import (flash, g, redirect, render_template, request,
                   url_for)
from flask.views import MethodView
from helpers.decorators import check_valid_org_and_project, login_required
from helpers.utils import allowed_file
from werkzeug.utils import secure_filename


class ViewOrganisation(MethodView):
	"""
		This view represents a organisation
	"""

	decorators = [check_valid_org_and_project, login_required]

	def get(self, slug):

		user = g.user
		username = user["username"]

		organisation = {}
		organisation["slug"] = slug

		set_active_org_project(slug)


		db_conn = db.get_database_connection()
		with db_conn.cursor() as cursor:
			sql = 'SELECT name, logo FROM organisation WHERE slug=%s';
			cursor.execute(sql, (slug, ))
			result = cursor.fetchone()

		organisation["logo"] = result["logo"]
		organisation["name"] = result["name"]

		with db_conn.cursor() as cursor:
			sql = 'SELECT username ,role FROM belongs_to WHERE slug=%s';
			cursor.execute(sql, (slug, ))
			result = cursor.fetchall()
		_member = []
		for rows in result:
			if rows is not None:
				_member.append(rows)
		organisation["members"] = _member

		with db_conn.cursor() as cursor:
			sql = 'SELECT project_id FROM project WHERE slug=%s'
			cursor.execute(sql, (slug, ))
			result = cursor.fetchall()

		_projects = []
		for rows in result:
			if rows is not None:
				_projects.append(rows["project_id"])
		organisation["projects"] = _projects

		show_results = True

		with db_conn.cursor() as cursor:
			sql = 'SELECT `role` FROM `belongs_to` WHERE `slug`=%s and `username`=%s'
			cursor.execute(sql, (slug, username, ))
			result = cursor.fetchone()
			if result["role"] == 'Member':
				return render_template('organisation/view_organisation.html', user=user, \
					organisation=organisation, show_results=False)

		
		return render_template('organisation/view_organisation.html', user=user, organisation=organisation,\
			show_results=True)	

	def post(self, slug):

		user = g.user
		username = user["username"]

		organisation = {}
		organisation["slug"] = slug

		set_active_org_project(slug)


		db_conn = db.get_database_connection()
		with db_conn.cursor() as cursor:
			sql = 'SELECT name, logo FROM organisation WHERE slug=%s';
			cursor.execute(sql, (slug, ))
			result = cursor.fetchone()

		organisation["logo"] = result["logo"]
		organisation["name"] = result["name"]

		with db_conn.cursor() as cursor:
			sql = 'SELECT username ,role FROM belongs_to WHERE slug=%s';
			cursor.execute(sql, (slug, ))
			result = cursor.fetchall()
		_member = []
		for rows in result:
			if rows is not None:
				_member.append(rows)
		organisation["members"] = _member

		with db_conn.cursor() as cursor:
			sql = 'SELECT project_id FROM project WHERE slug=%s'
			cursor.execute(sql, (slug, ))
			result = cursor.fetchall()

		_projects = []
		for rows in result:
			if rows is not None:
				_projects.append(rows["project_id"])
		organisation["projects"] = _projects
		
		username = request.form.get("username", None)
		if username:
			_username = db.get_user(username)
			if _username is not None:
				db_conn = db.get_database_connection()
				with db_conn.cursor() as cursor:
					sql = 'SELECT slug, username FROM belongs_to WHERE username=%s and slug=%s'
					cursor.execute(sql, (username, slug, ))
					result = cursor.fetchone()
				if result is not None:
					flash("user is already working in the organisation","danger")
					return render_template('organisation/view_organisation.html', user=user, organisation=organisation,show_results=True)
				else:

					with db_conn.cursor() as cursor:
						cursor.execute("INSERT INTO belongs_to(username,slug,role) Values (%s, %s, %s)", (username,slug,"Member"))
						db_conn.commit()
					with db_conn.cursor() as cursor:
						sql = 'SELECT username, role FROM belongs_to WHERE slug=%s';
						cursor.execute(sql, (slug, ))
						result = cursor.fetchall()
					_member = []
					for rows in result:
						if rows is not None:
							_member.append(rows)
					organisation["members"] = _member
					return render_template('organisation/view_organisation.html',user=user,organisation=organisation, show_results=True)


			else:
				flash("username does not exist","danger")
				return render_template('organisation/view_organisation.html', user=user, organisation=organisation, show_results=True)

		else:
			flash("Enter username","danger")
			return render_template('organisation/view_organisation.html', user=user, organisation=organisation, show_results=True)

class EditOrganisation(MethodView):
	"""
		This method is to edit a organisation
	"""
	decorators = [check_valid_org_and_project, login_required]

	def get(self, slug):
		set_active_org_project(slug)

		db_conn = db.get_database_connection()
		with db_conn.cursor() as cursor:
			sql = 'SELECT * FROM `organisation` WHERE `slug`=%s'
			cursor.execute(sql, (slug, ))
			response = cursor.fetchone()
		return render_template('organisation/edit_organisation.html', organisation=response)

	
	def post(self, slug):
		set_active_org_project(slug)

		db_conn = db.get_database_connection()
		with db_conn.cursor() as cursor:
			sql = 'SELECT * FROM `organisation` WHERE `slug`=%s'
			cursor.execute(sql, (slug, ))
			response = cursor.fetchone()

		name = request.form.get("name", None)
		if 'logo' not in request.files:
			flash("No file part", "danger")
			return render_template('organisation/edit_organisation.html',organisation=response)

		logo = request.files['logo']

		if logo.filename or name:
			with db_conn.cursor() as cursor:
				sql = 'SELECT `logo` FROM `organisation` WHERE `slug`=%s'
				cursor.execute(sql, (slug, ))
				result = cursor.fetchone()
			if not logo.filename:
				logo.filename = result["logo"]

			if result["logo"] == logo.filename:
				with db_conn.cursor() as cursor:
					sql = 'UPDATE `organisation` SET `name`=%s WHERE `organisation`.`slug`=%s'
					cursor.execute(sql, (name, slug, ))
					db_conn.commit()
				return redirect(url_for('organisation.view_organisation',slug=slug))

			else:
				if logo.filename and allowed_file(logo.filename):
					filename = secure_filename(logo.filename)
					logo.save(os.path.join(app.app.config['UPLOAD_FOLDER'], filename))
					with db_conn.cursor() as cursor:
						sql = 'UPDATE `organisation` SET `name`=%s, `logo`=%s \
							WHERE `organisation`.`slug`=%s'
						cursor.execute(sql, (name, filename, slug, ))
						db_conn.commit()
						return redirect(url_for('organisation.view_organisation',slug=slug))
				else:
					flash("logo selected should be a image", "danger")
					return render_template('organisation/edit_orgainsation.html', organisation=response)
		else:
			if not name:
				flash("Enter name", "danger")
			return render_template('organisation/edit_organisation.html', organisation=response)

class NewOrganisation(MethodView):
	"""
		This view is to create new organisation
	"""

	decorators = [login_required]

	def allowed_file(self, filename):
		ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

	def get_slug(self, slug):
		db_conn = db.get_database_connection()
		with db_conn.cursor() as cursor:
			sql = 'SELECT * FROM `organisation` WHERE `slug`=%s'
			cursor.execute(sql, (slug, ))
			result = cursor.fetchone()
			return result

	def get(self):

		user = g.user
		username = user["username"]

		return render_template('organisation/new_organisation.html')

	def post(self):

		user = g.user
		username = user["username"]

		slug = request.form.get("slug", None)

		name = request.form.get("name", None)


		if 'logo' not in request.files:
			flash("No file part", "danger")
			return render_template('organisation/new_organisation.html')

		logo = request.files['logo']

		role = "Admin"

		if slug and name and logo.filename:
			_slug = self.get_slug(slug)
			if _slug is not None:
				flash("Slug already exists","danger")
				return render_template('organisation/new_organisation.html')
			else:
				if logo.filename and self.allowed_file(logo.filename):
					filename = secure_filename(logo.filename)
					logo.save(os.path.join(app.app.config['UPLOAD_FOLDER'], filename))
					db_conn = db.get_database_connection()
					with db_conn.cursor() as cursor:
						cursor.execute("INSERT INTO `organisation`(`slug`,`name`,`logo`) Values (%s, %s, %s)", (slug, name, filename))
						db_conn.commit()
						cursor.execute("INSERT INTO `belongs_to`(`slug`, `username`, `role`) \
							Values (%s, %s, %s)", (slug, username, role))
						db_conn.commit()
						return redirect(url_for('organisation.organisation'))
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
