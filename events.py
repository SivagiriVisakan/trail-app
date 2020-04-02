import json

from flask import Blueprint, request

import db
from utils import check_missing_keys

blueprint = Blueprint('events', __name__, url_prefix='/events')

# An endpoint to list all the events
# TODO: Restrict access based on user and project.
@blueprint.route('/list-all', methods=["GET"])
def list_all_events():
    db_conn = db.get_database_connection()
    with db_conn.cursor() as cursor:
        sql = 'SELECT * FROM `web_event`'
        cursor.execute(sql)
        result = cursor.fetchall()
        return {"events": result}
    return {}


# This function adds CORS headers to all the responses from this blueprint
# CORS headers are required as the requests to this server will be made from other
# sites.
@blueprint.after_request
def add_cors_header(response):
    headers = response.headers
    if 'Access-Control-Allow-Origin' not in response.headers:
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Content-Length'
    return response


@blueprint.route('/register-new', methods=["POST"])
def register_new_event():
    """
    This endpoint registers a new event for a project.
    This endpoint should typically be called from an external site (i.e site of an user)
    to log a new event onto our database.

    parameters:
    	page_url:   The current URL of the from which the event is to be registered
	    event_type: A specific tag for that particular event.
	    custom_params: (Optional) Any other data that the client developer wants to send along.
                        (Should be valid JSON)
		api_key: The API key of the project for which the event is to be logged
		origin_id: A unique tag identifying the end-user of the client-website.
    """

    # The keys that should be present a request that comes in to register a new event
    REGISTER_NEW_EVENT_KEYS = {"page_url", "event_type", "api_key", "origin_id"}

    response = {"success": False}
    if not request.is_json:
        # Requests should be of type application/json
        return response, 400

    request_body = request.get_json()
    missing = check_missing_keys(request_body, REGISTER_NEW_EVENT_KEYS)
    if missing:
        response["error"] = "Malformed request - missing parameters - " + str(missing)
        return response, 400

    user_agent = request.headers.get('User-Agent', None)
    api_key = request_body["api_key"]
    get_project_from_api_key_sql  = 'SELECT `project_id` FROM `project` WHERE `api_key`=%s'
    project_id = None

    custom_data = request_body.get('custom_params', None)
    custom_data = json.dumps(custom_data)

    db_connection = db.get_database_connection()
    with db_connection.cursor() as cursor:
        cursor.execute(get_project_from_api_key_sql, (api_key,))
        result = cursor.fetchone()
        if not result:
            response["error"] = "Invalid API key"
            return response, 404

        project_id = result.get("project_id", None)

        insert_new_event_sql = "INSERT INTO `web_event` ( `project_id`, `origin_id`,`user_agent`, \
                                `page_url`, `event_type`, `custom_data`) VALUES \
                                (%s, %s, %s, %s, %s, %s)"

        cursor.execute(insert_new_event_sql, (project_id, request_body["origin_id"],
                                                user_agent, request_body["page_url"], request_body["event_type"],
                                                custom_data))
        db_connection.commit()

        response["success"] = True
    return response
