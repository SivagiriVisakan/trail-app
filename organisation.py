import json 
import datetime 

from flask import Blueprint, request, render_template, flash, g, send_from_directory, redirect, url_for

from functools import wraps
import db
from utils import check_missing_keys
import auth
from werkzeug.utils import secure_filename
import os
import app
import uuid


blueprint = Blueprint('organisation', __name__, url_prefix='/')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_organisation(slug, username):
	db_conn = db.get_database_connection()
	with db_conn.cursor() as cursor:
		sql = 'SELECT u.username, w.logo, w.name as wname, p.project_id, p.name as pname \
				 FROM user u LEFT JOIN belongs_to b on u.username = b.username \
					 LEFT JOIN organisation w on b.slug = w.slug LEFT JOIN project p on w.slug = p.slug \
						WHERE u.username=%s and b.slug=%s';
		cursor.execute(sql, (username, slug, ))
		result = cursor.fetchall()

	return result
	

@blueprint.route('', methods=['GET'])
@auth.login_required
def organisation():
	#TODO: Do conditional rendering here (or somewhere) based on user's authencation state
	#		i.e if he is logged in, show organisations list, else show a landing page.
	user = g.user
	username = user["username"]

	response = {}
	result = {}

	db_conn = db.get_database_connection()
	with db_conn.cursor() as cursor:
		sql = 'SELECT slug FROM belongs_to WHERE username=%s';
		cursor.execute(sql, (username, ))
		records = cursor.fetchall()

	if records is None:
		empty = "True"
	else:
		empty = "False"

	for row in records:
		if row is not None:
			result[row["slug"]] = get_organisation(row["slug"], username)

	for slug, details in result.items():
		project_id_name = []
		for element in details:
			project_id_name.append(element["project_id"])
		response[slug] = project_id_name

	return render_template('organisation/organisation.html', user=user, response=response, empty=empty)


@blueprint.route('/uploads/<filename>')
def upload_file(filename):
	return send_from_directory(app.app.config['UPLOAD_FOLDER'], filename)


@blueprint.route('/<string:slug>',methods=["GET","POST"])
@auth.login_required
@auth.check_valid_org_and_project
def view_organisation(slug):

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

	if request.method == "GET":
		return render_template('organisation/view_organisation.html', user=user, organisation=organisation,show_results=True)	

	elif request.method == "POST":
		
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
						sql = 'SELECT username FROM belongs_to WHERE slug=%s';
						cursor.execute(sql, (slug, ))
						result = cursor.fetchall()
					_member = []
					for rows in result:
						if rows is not None:
							_member.append(rows["username"])
					organisation["members"] = _member
					return render_template('organisation/view_organisation.html',user=user,organisation=organisation, show_results=True)


			else:
				flash("username does not exist","danger")
				return render_template('organisation/view_organisation.html', user=user, organisation=organisation, show_results=True)

		else:
			flash("Enter username","danger")
			return render_template('organisation/view_organisation.html', user=user, organisation=organisation, show_results=True)

@blueprint.route('/<string:slug>/remove_member/<string:member_name>', methods=['GET'])
@auth.login_required
@auth.check_valid_org_and_project
def remove_member(slug, member_name):
	if request.method == "GET":
		user = g.user
		db_conn = db.get_database_connection()
		with db_conn.cursor() as cursor:
			sql = 'SELECT `role` FROM `belongs_to` WHERE `username`=%s and `slug`=%s'
			cursor.execute(sql, (member_name, slug, ))
			result = cursor.fetchone()
		if result["role"] == 'Admin':
			flash("You can't remove a admin","danger")
			return redirect(url_for('organisation.view_organisation',slug=slug))
		with db_conn.cursor() as cursor:
			sql = 'DELETE FROM `belongs_to` WHERE `username`=%s and `slug`=%s'
			cursor.execute(sql, (member_name, slug, ))
			db_conn.commit()

		return redirect(url_for('organisation.view_organisation',slug=slug))

def get_slug(slug):
	db_conn = db.get_database_connection()
	with db_conn.cursor() as cursor:
		sql = 'SELECT * FROM `organisation` WHERE `slug`=%s'
		cursor.execute(sql, (slug, ))
		result = cursor.fetchone()
		return result

def set_active_org_project(organisation, project=None):
	if not "active_organisation" in g:
		g.active_organisation = {}
	g.active_organisation = organisation
	g.active_project = project

@blueprint.route('/<string:organisation_slug>/testing')
@auth.login_required
def testing(organisation_slug):
	set_active_org_project(organisation_slug)
	return render_template('test_side.html')

@blueprint.route('/<string:slug>/edit', methods=['GET','POST'])
@auth.login_required
@auth.check_valid_org_and_project
def edit_organisation(slug):

	set_active_org_project(slug)

	db_conn = db.get_database_connection()
	with db_conn.cursor() as cursor:
		sql = 'SELECT * FROM `organisation` WHERE `slug`=%s'
		cursor.execute(sql, (slug, ))
		response = cursor.fetchone()

	if request.method == "GET":
		return render_template('organisation/edit_organisation.html', organisation=response)

	elif request.method == "POST":
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





@blueprint.route('/<string:slug>/project/new', methods=['GET','POST'])
@auth.login_required
@auth.check_valid_org_and_project
def new_project(slug):
	if request.method == "GET":
		return render_template('organisation/new_project.html',slug=slug)

	elif request.method == "POST":

		project_id = request.form.get("project_id", None)

		if project_id == "new" or project_id == "project":
			flash("project_id is not applicable", "danger")
			return render_template('organisation/new_project.html')

		name = request.form.get("name", None)


		description = request.form.get("description", None)

		if project_id and name and description:
			db_conn = db.get_database_connection()
			with db_conn.cursor() as cursor:
				sql = 'SELECT `slug`, `project_id` FROM `project` WHERE `slug`=%s and `project_id`=%s'
				cursor.execute(sql, (slug, project_id, ))
				result = cursor.fetchone()

			if result is not None:
				flash("project already exist in the organisation", "danger")
				return render_template('organisation/new_project.html')

			with db_conn.cursor() as cursor:
				sql = 'SELECT `project_id` FROM `project` WHERE `project_id`=%s'
				cursor.execute(sql, (project_id, ))
				result = cursor.fetchone()

			if result is not None:
				flash("project_id already exist", "danger")
				return render_template('organisation/new_project.html')

			while True:
				api_key = uuid.uuid4()
				api_key = api_key.hex
				with db_conn.cursor() as cursor:
					sql = 'SELECT `api_key` FROM `project` WHERE `api_key`=%s'
					cursor.execute(sql, (api_key, ))
					result = cursor.fetchone()
				if result is None:
					break

			with db_conn.cursor() as cursor:
				cursor.execute("INSERT INTO `project`(`slug`,`project_id`,`name`,`description`,`api_key`) \
					Values (%s, %s, %s, %s, %s)", (slug, project_id, name, description, api_key))
				db_conn.commit()
				return redirect(url_for('organisation.view_project',slug=slug,project_id=project_id))

		else:
			if not project_id:
				flash("Enter project_id", "danger")
			if not name:
				flash("Enter name", "danger")
			if not description:
				flash("Enter description", "danger")

			return render_template('organisation/new_project.html')


@blueprint.route('/<string:slug>/project/<string:project_id>/get-api', methods=["GET"])
@auth.login_required
@auth.check_valid_org_and_project
def get_api(slug, project_id):
	if request.method == "GET":
		response = {}
		db_conn = db.get_database_connection()
		while True:
			api_key = uuid.uuid4()
			api_key = api_key.hex
			with db_conn.cursor() as cursor:
				sql = 'SELECT `api_key` FROM `project` WHERE `api_key`=%s'
				cursor.execute(sql, (api_key, ))
				result = cursor.fetchone()
			if result is None:
				with db_conn.cursor() as cursor:
					sql = 'UPDATE `project` SET `api_key`=%s WHERE `project`.`project_id`=%s'
					cursor.execute(sql, (api_key, project_id, ))
					db_conn.commit()
				break
		return redirect(url_for('organisation.view_project', slug=slug, project_id=project_id))


@blueprint.route('/new',methods=["GET","POST"])
@auth.login_required
def new_organisation():

	user = g.user
	username = user["username"]

	if request.method == "GET":
		return render_template('organisation/new_organisation.html')

	elif request.method == "POST":

		slug = request.form.get("slug", None)

		name = request.form.get("name", None)


		if 'logo' not in request.files:
			flash("No file part", "danger")
			return render_template('organisation/new_organisation.html')

		logo = request.files['logo']

		role = "Admin"

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

@blueprint.route('/<string:organisation>/project/<string:project_id>/dashboard/')
@auth.login_required
@auth.check_valid_org_and_project
def project_dashboard(organisation, project_id):
	set_active_org_project(organisation, project_id)
	return render_template('projects/home_dashboard.html', 
							template_context={"project_id": project_id, "organisation": organisation})



# The import is being done here and not at the top for the time being, because the 
# SessionDashboard imports a function from this module to it.
# Ideally, it should be moved into a seperate file and this import moved to the top 
from views.dashboard.session import SessionDashboard
from views.dashboard.event import EventDashboard
from views.project import ViewProject, EditProject


blueprint.add_url_rule('/<string:slug>/project/<string:project_id>/',
                 view_func=ViewProject.as_view('view_project'), methods=['GET',])

blueprint.add_url_rule('/<string:slug>/project/<string:project_id>/edit',
                 view_func=EditProject.as_view('edit_project'), methods=['GET', 'POST'])

blueprint.add_url_rule('/<string:organisation>/project/<string:project_id>/events/',
                 view_func=EventDashboard.as_view('project_events_dashboard'), methods=['GET',])


blueprint.add_url_rule('/<string:organisation>/project/<string:project_id>/sessions/',
                 view_func=SessionDashboard.as_view('project_sessions_dashboard'), methods=['GET',])
