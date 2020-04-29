import json 
import datetime 

from flask import Blueprint, request, render_template, flash, g, redirect, url_for

import db
from utils import check_missing_keys
import auth
from werkzeug.utils import secure_filename
import os
import app

blueprint = Blueprint('organisation', __name__, url_prefix='/')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blueprint.route('')
@auth.login_required
def organisation():
	#TODO: Do conditional rendering here (or somewhere) based on user's authencation state
	#		i.e if he is logged in, show workspaces list, else show a landing page.
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


@blueprint.route('/new',methods=["GET","POST"])
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


# TODO: Restrict access to projects based on user
@blueprint.route('/<string:workspace>/<string:project_id>/')
@blueprint.route('/<string:workspace>/<string:project_id>/dashboard/')
@auth.login_required
def project_dashboard(workspace, project_id):
    return render_template('projects/home_dashboard.html', template_context={"project_id": project_id, "workspace": workspace})

# TODO: Restrict access to projects based on user
@blueprint.route('/<string:workspace>/<string:project_id>/events/')
@auth.login_required
def project_events_dashboard(workspace, project_id):
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

        return redirect(url_for('organisation.project_events_dashboard', workspace=workspace, project_id=project_id,
                            start_time=start_timestamp, end_time=end_timestamp, event_type=event_type))
    db_conn = db.get_database_connection()
    events_list = []
    with db_conn.cursor(cursor=None) as cursor:
        # No event type passed, so we get the details of all the events
        sql = 'SELECT event_type FROM web_event WHERE project_id=%s AND DATE(time_entered) >= DATE(%s) AND DATE(time_entered) <= DATE(%s) GROUP BY event_type'
        cursor.execute(sql, (project_id, start_time.isoformat(), end_time.isoformat()))
        result = cursor.fetchall()
        events_list = [row["event_type"] for row in result]

    data = get_event_details(project_id, start_time, end_time, event_type)

    return render_template('projects/events_dashboard.html', template_context={"project_id": project_id, "workspace": workspace,
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
            sql = 'SELECT event_type, count(*) as total_events_count FROM web_event WHERE project_id=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s) GROUP BY event_type'
            cursor.execute(sql, (project_id, start_time.isoformat(), end_time.isoformat()))
        else:
            sql = 'SELECT event_type, count(*) as total_events_count FROM web_event WHERE project_id=%s AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s) '
            cursor.execute(sql, (project_id, event_type, start_time.isoformat(), end_time.isoformat()))
        result = cursor.fetchall()
        result_to_return = result # The DictCursor we use returns the data in required format
        print('\n\n\n',cursor._last_executed,'\n\n\n')
        
        for event_dict in result_to_return:
            # Query the page_wise events count
            sql = 'SELECT page_url, count(*) as total_events_count FROM web_event WHERE project_id=%s  \
                                                AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s) GROUP BY page_url'
            cursor.execute(sql, (project_id, event_dict["event_type"], start_time.isoformat(), end_time.isoformat()))
            result = cursor.fetchall()
            event_dict["page_wise"] = result


            resulting_custom_data_keys = []
            sql = 'SELECT JSON_KEYS(custom_data)  as custom_keys from web_event where event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s) group by custom_keys'
            cursor.execute(sql, ( event_dict["event_type"], start_time.isoformat(), end_time.isoformat()))
            result = cursor.fetchall()
            for row in result:
                resulting_custom_data_keys.extend(json.loads(row["custom_keys"]))

            # Eliminate duplicates
            resulting_custom_data_keys = set(resulting_custom_data_keys)
            custom_data_key_value_aggregation = {}
            for key in resulting_custom_data_keys:
                sql = 'SELECT JSON_EXTRACT(custom_data, %s) as key_value, count(*) as key_value_count from \
                        web_event where event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s)  group by key_value'
                json_path_for_mysql = f'$.{key}'
                cursor.execute(sql, (json_path_for_mysql, event_dict["event_type"], start_time.isoformat(), end_time.isoformat()))

                result = cursor.fetchall()
                custom_data_key_value_aggregation[key] = result
            event_dict["custom_data"] = custom_data_key_value_aggregation

        return result_to_return        
