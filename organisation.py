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

def permission_required(f):
	@wraps(f)
	def wrapper(organisation, project_id, *args, **kwargs):
		result = get_slug(organisation)
		if result is not None:
			user = g.user
			username = user["username"]
			db_conn = db.get_database_connection()
			with db_conn.cursor() as cursor:
				sql = 'SELECT username, slug FROM belongs_to WHERE username=%s and slug=%s'
				cursor.execute(sql, (username, organisation))
				records = cursor.fetchone()
			if records is not None:
				with db_conn.cursor() as cursor:
					sql = 'SELECT slug, project_id FROM project WHERE slug=%s and project_id=%s'
					cursor.execute(sql, (organisation, project_id))
					fetch = cursor.fetchone()
				if fetch is not None:
					f(*args, **kwargs)
				else:
					return "slug do not have this project"
			else:
				return "user is not in the working in the organisation"				

		else:
			return "organisation not found...404 page not found"
	return wrapper


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
			response[row["slug"]] = get_organisation(row["slug"], username)
	return render_template('organisation/organisation.html', user=user, response=response, empty=empty)


@blueprint.route('/uploads/<filename>')
def upload_file(filename):
	return send_from_directory(app.app.config['UPLOAD_FOLDER'], filename)


@blueprint.route('/<string:slug>',methods=["GET","POST"])
@auth.login_required
def view_organisation(slug):

	user = g.user
	username = user["username"]

	organisation = {}
	organisation["slug"] = slug


	db_conn = db.get_database_connection()
	with db_conn.cursor() as cursor:
		sql = 'SELECT name, logo FROM organisation WHERE slug=%s';
		cursor.execute(sql, (slug, ))
		result = cursor.fetchone()

	organisation["logo"] = result["logo"]
	organisation["name"] = result["name"]

	with db_conn.cursor() as cursor:
		sql = 'SELECT username FROM belongs_to WHERE slug=%s';
		cursor.execute(sql, (slug, ))
		result = cursor.fetchall()
	_member = []
	for rows in result:
		if rows is not None:
			_member.append(rows["username"])
	organisation["members"] = _member

	show_results = 1

	with db_conn.cursor() as cursor:
		sql = 'SELECT `role` FROM `belongs_to` WHERE `slug`=%s and `username`=%s'
		cursor.execute(sql, (slug, username, ))
		result = cursor.fetchone()
		if result["role"] == 'Member':
			return render_template('organisation/view_organisation.html', user=user, \
				organisation=organisation, show_results=0)

	if request.method == "GET":
		return render_template('organisation/view_organisation.html', user=user, organisation=organisation,show_results=1)	

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
					return render_template('organisation/view_organisation.html', user=user, organisation=organisation,show_results=1)
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
					return render_template('organisation/view_organisation.html',user=user,organisation=organisation, show_results=1)


			else:
				flash("username does not exist","danger")
				return render_template('organisation/view_organisation.html', user=user, organisation=organisation, show_results=1)

		else:
			flash("Enter username","danger")
			return render_template('organisation/view_organisation.html', user=user, organisation=organisation, show_results=1)

@blueprint.route('/<string:slug>/remove_member/<string:member_name>', methods=['GET'])
@auth.login_required
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
			return render_template('organisation/view_organisation.html',user=user,organisation=organisation,show_results=0)
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

@blueprint.route('/<string:slug>/project/<string:project_id>', methods=['GET','POST'])
@auth.login_required
def view_project(slug, project_id):

	if request.method == "GET":
		db_conn = db.get_database_connection()
		with db_conn.cursor() as cursor:
			sql = 'SELECT `session_id` FROM `session` WHERE `project_id`=%s'
			cursor.execute(sql, (project_id, ))
			result = cursor.fetchone()

		if result is not None:
			return redirect(url_for('organisation.project_dashboard',organisation=slug, project_id=project_id))

		with db_conn.cursor() as cursor:
			sql = 'SELECT * FROM `project` WHERE `slug`=%s and `project_id`=%s'
			cursor.execute(sql, (slug, project_id, ))
			result = cursor.fetchone()
			return render_template('organisation/view_project.html', slug=slug, project=result) 

@blueprint.route('/<string:slug>/project/<string:project_id>/edit',methods=['GET', 'POST'])
@auth.login_required
def edit_project(slug, project_id):

	user = g.user
	username = user["username"]

	db_conn = db.get_database_connection()

	with db_conn.cursor() as cursor:
		sql = 'SELECT * from `project` WHERE `project_id`=%s'
		cursor.execute(sql, (project_id, ))
		response = cursor.fetchone()

	if request.method == "GET":
		with db_conn.cursor() as cursor:
			sql = 'SELECT `role` from `belongs_to` WHERE `username`=%s and `slug`=%s'
			cursor.execute(sql, (username, slug, ))
			result = cursor.fetchone()

		if result["role"] == "Admin":
			return render_template('organisation/edit_project.html', slug=slug, project_id=project_id, response=response)
		else:
			return "Sorry you don't have edit access"

	elif request.method == "POST":
		name = request.form.get("name", None)
		description = request.form.get("description", None)
		api_key = request.form.get("api_key", None)

		if name and description and api_key:
			with db_conn.cursor() as cursor:
				sql = 'UPDATE `project` SET `name`=%s, `description`=%s, `api_key`=%s \
					WHERE	`project`.`project_id`=%s'
				cursor.execute(sql, (name, description, api_key, project_id, ))
			return redirect(url_for('organisation.view_project',slug=slug,project_id=project_id))

		else:
			if not name:
				flash("Enter project name", "danger")
			if not description:
				flash("Enter description", "danger")
			if not api_key:
				flash("refresh api-key", "danger")
			return render_template('organisation/edit_project.html')


@blueprint.route('/<string:slug>/project/new', methods=['GET','POST'])
@auth.login_required
def new_project(slug):
	if request.method == "GET":
		return render_template('organisation/new_project.html',slug=slug)

	elif request.method == "POST":

		project_id = request.form.get("project_id", None)
		if len(project_id) > 15:
			flash("project_id should not exceed 15 characters", "danger")
			return render_template('organisation/new_project.html')

		if project_id == "new" or project_id == "project":
			flash("project_id is not applicable", "danger")
			return render_template('organisation/new_project.html')

		name = request.form.get("name", None)
		if len(name) > 15:
			flash("name should not exceed 15 characters", "danger")
			return render_template('organisation/new_project.html')

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


@blueprint.route('/get-api/<string:project_id>', methods=["GET"])
@auth.login_required
def get_api(project_id):
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
				break
		response["api_key"] = api_key
		return response


@blueprint.route('/new',methods=["GET","POST"])
@auth.login_required
def new_organisation():

	user = g.user
	username = user["username"]

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
def project_dashboard(organisation, project_id):
    return render_template('projects/home_dashboard.html', 
							template_context={"project_id": project_id, "organisation": organisation})


# TODO: Restrict access to projects based on user
@blueprint.route('/<string:organisation>/project/<string:project_id>/events/')
@auth.login_required
def project_events_dashboard(organisation, project_id):
    event_type = request.args.get('event_type') or None

    start_timestamp = request.args.get("start_time") or datetime.datetime.now().timestamp()
    start_timestamp = float(start_timestamp)
    start_time = datetime.datetime.utcfromtimestamp(start_timestamp)
    start_time += datetime.timedelta(days=1)

    end_timestamp = request.args.get("end_time") or datetime.datetime.now().timestamp()
    end_timestamp = float(end_timestamp)
    end_time = datetime.datetime.utcfromtimestamp(end_timestamp)
    end_time += datetime.timedelta(days=1)

    if 'start_time' not in request.args or 'end_time' not in request.args:

        return redirect(url_for('organisation.project_events_dashboard', organisation=organisation, project_id=project_id,
                            start_time=start_timestamp, end_time=end_timestamp, event_type=event_type))
    db_conn = db.get_database_connection()
    events_list = []
    with db_conn.cursor(cursor=None) as cursor:
        # No event type passed, so we get the details of all the events

        sql = ('SELECT event_type FROM web_event INNER JOIN `session` ON web_event.session_id=session.session_id'
                ' WHERE  project_id=%s AND DATE(time_entered) >= DATE(%s) AND DATE(time_entered) <= DATE(%s)'
                ' GROUP BY event_type')

        cursor.execute(sql, (project_id, start_time.isoformat(), end_time.isoformat()))
        result = cursor.fetchall()
        events_list = [row["event_type"] for row in result]

    data = get_event_details(project_id, start_time, end_time, event_type)

    return render_template('projects/events_dashboard.html', template_context={"project_id": project_id, "organisation": organisation,
                                "event_data": data, "events_list": events_list,"start_date": start_time, "end_date": end_time})


def get_event_details(project_id, start_time, end_time, event_type=None):
    """

    """
    db_conn = db.get_database_connection()
    result_to_return = []
    resulting_custom_data_keys = []
    events_to_query = []
    with db_conn.cursor(cursor=None) as cursor:
        if event_type is None:
            # No event type passed, so we get the details of all the events
            sql = ('SELECT event_type, count(*) as total_events_count FROM web_event INNER JOIN `session`'
                    ' ON web_event.session_id=session.session_id WHERE project_id=%s'
                    ' AND DATE(time_entered) >= DATE(%s) AND DATE(time_entered) <= DATE(%s) GROUP BY event_type')

            cursor.execute(sql, (project_id, start_time.isoformat(), end_time.isoformat()))
        else:
            sql = ('SELECT event_type, count(*) as total_events_count FROM web_event INNER JOIN `session`'
                    ' ON web_event.session_id=session.session_id WHERE project_id=%s'
                    ' AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s)')
            cursor.execute(sql, (project_id, event_type, start_time.isoformat(), end_time.isoformat()))

        result = cursor.fetchall()
        result_to_return = result # The DictCursor we use returns the data in required format

        for event_dict in result_to_return:
            # Query the page_wise events count
            sql = ('SELECT page_url, count(*) as total_events_count FROM web_event INNER JOIN `session`'
                    ' ON web_event.session_id=session.session_id WHERE project_id=%s'
                    ' AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s) GROUP BY page_url')
            cursor.execute(sql, (project_id, event_dict["event_type"], start_time.isoformat(), end_time.isoformat()))
            result = cursor.fetchall()
            event_dict["page_wise"] = result


            resulting_custom_data_keys = []

            sql = ('SELECT JSON_KEYS(custom_data)  as custom_keys from web_event INNER JOIN `session` '
                    ' ON web_event.session_id=session.session_id where project_id=%s'
                    ' AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s)'
                    ' group by custom_keys')

            cursor.execute(sql, (project_id, event_dict["event_type"], start_time.isoformat(), end_time.isoformat()))
            result = cursor.fetchall()
            for row in result:
                resulting_custom_data_keys.extend(json.loads(row["custom_keys"]))

            # Eliminate duplicates
            resulting_custom_data_keys = set(resulting_custom_data_keys)
            custom_data_key_value_aggregation = {}
            for key in resulting_custom_data_keys:
                sql = 'SELECT JSON_EXTRACT(custom_data, %s) as key_value, count(*) as key_value_count from \
                        web_event INNER JOIN `session` ON web_event.session_id=session.session_id where project_id=%s AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s)  group by key_value'
                json_path_for_mysql = f'$.{key}'
                cursor.execute(sql, (json_path_for_mysql, project_id, event_dict["event_type"], start_time.isoformat(), end_time.isoformat()))

                result = cursor.fetchall()
                custom_data_key_value_aggregation[key] = result
            event_dict["custom_data"] = custom_data_key_value_aggregation

        print(result_to_return)
        return result_to_return

