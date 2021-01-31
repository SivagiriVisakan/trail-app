import datetime
import json
import uuid
from functools import wraps

import app
import helpers.db as db
from flask import (Blueprint, g, redirect, render_template, request,
                   send_from_directory, url_for)
from helpers.decorators import check_valid_org_and_project, login_required
from helpers.utils import check_missing_keys
from werkzeug.utils import secure_filename

blueprint = Blueprint('organisation', __name__, url_prefix='/')


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
@login_required
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


@blueprint.route('/<string:slug>/remove_member/<string:member_name>', methods=['GET'])
@login_required
@check_valid_org_and_project
def remove_member(slug, member_name):
	if request.method == "GET":
		user = g.user
		db_conn = db.get_database_connection()

		with db_conn.cursor() as cursor:
			sql = 'DELETE FROM `belongs_to` WHERE `belongs_to`.`username`=%s AND `belongs_to`.`slug`=%s'
			cursor.execute(sql, (member_name, slug, ))
			db_conn.commit()

		return redirect(url_for('organisation.view_organisation',slug=slug))

def set_active_org_project(organisation, project=None):
	if not "active_organisation" in g:
		g.active_organisation = {}
	g.active_organisation = organisation
	g.active_project = project

@blueprint.route('/<string:organisation_slug>/testing')
@login_required
def testing(organisation_slug):
	set_active_org_project(organisation_slug)
	return render_template('test_side.html')


@blueprint.route('/<string:slug>/project/<string:project_id>/get-api', methods=["GET"])
@login_required
@check_valid_org_and_project
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


@blueprint.route('/<string:organisation>/project/<string:project_id>/dashboard/')
@login_required
@check_valid_org_and_project
def project_dashboard(organisation, project_id):
	set_active_org_project(organisation, project_id)
	return render_template('projects/home_dashboard.html', 
							template_context={"project_id": project_id, "organisation": organisation})



from views.dashboard.event import EventDashboard
# The import is being done here and not at the top for the time being, because the 
# SessionDashboard imports a function from this module to it.
# Ideally, it should be moved into a seperate file and this import moved to the top 
from views.dashboard.session import SessionDashboard
from views.organisation import (EditOrganisation, NewOrganisation,
                                ViewOrganisation)
from views.project import EditProject, NewProject, ViewProject

blueprint.add_url_rule('/new/',
				view_func=NewOrganisation.as_view('new_organisation'), methods=['GET','POST'])

blueprint.add_url_rule('/<string:slug>/edit/',
				view_func=EditOrganisation.as_view('edit_organisation'),methods=['GET','POST'])

blueprint.add_url_rule('/<string:slug>/', 
				view_func=ViewOrganisation.as_view('view_organisation'),methods=['GET','POST'])

blueprint.add_url_rule('/<string:slug>/project/<string:project_id>/',
                 view_func=ViewProject.as_view('view_project'), methods=['GET',])

blueprint.add_url_rule('/<string:slug>/project/<string:project_id>/edit',
                 view_func=EditProject.as_view('edit_project'), methods=['GET', 'POST'])

blueprint.add_url_rule('/<string:slug>/project/new',
                 view_func=NewProject.as_view('new_project'), methods=['GET', 'POST'])


blueprint.add_url_rule('/<string:organisation>/project/<string:project_id>/events/',
                 view_func=EventDashboard.as_view('project_events_dashboard'), methods=['GET',])


blueprint.add_url_rule('/<string:organisation>/project/<string:project_id>/sessions/',
                 view_func=SessionDashboard.as_view('project_sessions_dashboard'), methods=['GET',])
