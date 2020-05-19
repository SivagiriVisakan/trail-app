import json
import datetime

from flask import redirect, render_template, request, url_for
from flask.views import MethodView

import auth
import db
from organisation import set_active_org_project

import utils


class EventDashboard(MethodView):
    """
    Class for handling requests related to the project's events dashboard
    """

    decorators = [auth.check_valid_org_and_project, auth.login_required]

    def get_event_details(self, start_time, end_time, event_type=None):
        result_to_return = []
        resulting_custom_data_keys = []
        events_to_query = []
        with self.db_conn.cursor(cursor=None) as cursor:
            if event_type is None:
                # No event type passed, so we get the details of all the events
                sql = ('SELECT event_type, count(*) as total_events_count FROM web_event INNER JOIN `session`'
                    ' ON web_event.session_id=session.session_id WHERE project_id=%s'
                    ' AND DATE(time_entered) >= DATE(%s) AND DATE(time_entered) <= DATE(%s) GROUP BY event_type')

                cursor.execute(
                    sql, (self.project_id, self.start_time.isoformat(), end_time.isoformat()))
            else:
                sql = ('SELECT event_type, count(*) as total_events_count FROM web_event INNER JOIN `session`'
                    ' ON web_event.session_id=session.session_id WHERE project_id=%s'
                    ' AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s)')
                cursor.execute(sql, (self.project_id, event_type,
                                    start_time.isoformat(), end_time.isoformat()))

            result = cursor.fetchall()
            result_to_return = result  # The DictCursor we use returns the data in required format

            for event_dict in result_to_return:
                # Query the page_wise events count
                sql = ('SELECT page_url, count(*) as total_events_count FROM web_event INNER JOIN `session`'
                    ' ON web_event.session_id=session.session_id WHERE project_id=%s'
                    ' AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s) GROUP BY page_url')
                cursor.execute(sql, (self.project_id, event_dict["event_type"], start_time.isoformat(
                ), end_time.isoformat()))
                result = cursor.fetchall()
                event_dict["page_wise"] = result

                resulting_custom_data_keys = []

                sql = ('SELECT JSON_KEYS(custom_data)  as custom_keys from web_event INNER JOIN `session` '
                    ' ON web_event.session_id=session.session_id where project_id=%s'
                    ' AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s)'
                    ' group by custom_keys')

                cursor.execute(sql, (self.project_id, event_dict["event_type"], start_time.isoformat(
                ), end_time.isoformat()))
                result = cursor.fetchall()
                for row in result:
                    resulting_custom_data_keys.extend(
                        json.loads(row["custom_keys"]))

                # Eliminate duplicates
                resulting_custom_data_keys = set(resulting_custom_data_keys)
                custom_data_key_value_aggregation = {}
                for key in resulting_custom_data_keys:
                    sql = 'SELECT JSON_EXTRACT(custom_data, %s) as key_value, count(*) as key_value_count from \
                            web_event INNER JOIN `session` ON web_event.session_id=session.session_id where project_id=%s AND event_type=%s AND DATE(time_entered) >= DATE(%s)  AND DATE(time_entered) <= DATE(%s)  group by key_value'
                    json_path_for_mysql = f'$.{key}'
                    cursor.execute(sql, (json_path_for_mysql, self.project_id,
                                        event_dict["event_type"], start_time.isoformat(), end_time.isoformat()))

                    result = cursor.fetchall()
                    custom_data_key_value_aggregation[key] = result
                event_dict["custom_data"] = custom_data_key_value_aggregation

            return result_to_return

    def get(self, organisation, project_id):
        set_active_org_project(organisation, project_id)
        self.organisation = organisation
        self.project_id = project_id
        self.event_type = request.args.get('event_type') or None

        current_timestamp = datetime.datetime.now().timestamp()
        start_timestamp = request.args.get(
            "start_time", None) or current_timestamp

        end_timestamp = request.args.get(
            "end_time") or current_timestamp

        if 'start_time' not in request.args or 'end_time' not in request.args:
            # If either one is not set, then redirect to the current page with the options set
            return redirect(url_for(request.endpoint, organisation=organisation, project_id=project_id,
                                    start_time=start_timestamp, end_time=end_timestamp))

        # We replace the set the hour and minute to 0 so that the difference in days will not be lesser than the actual value
        self.end_time = utils.parse_date_from_timestamp(
            end_timestamp).replace(hour=0, minute=0)
        self.start_time = utils.parse_date_from_timestamp(
            start_timestamp).replace(hour=0, minute=0)

        self.db_conn = db.get_database_connection()

        data = self.get_event_details(self.start_time, self.end_time, self.event_type)
        with self.db_conn.cursor(cursor=None) as cursor:

            sql = ('SELECT event_type FROM web_event INNER JOIN `session` ON web_event.session_id=session.session_id'
                ' WHERE  project_id=%s AND DATE(time_entered) >= DATE(%s) AND DATE(time_entered) <= DATE(%s)'
                ' GROUP BY event_type')

            cursor.execute(
                sql, (project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchall()
            events_list = [row["event_type"] for row in result]

        return render_template('projects/events_dashboard.html', template_context={"project_id": project_id, "organisation": organisation,
                                        "event_data": data, "events_list": events_list, "start_date": self.start_time, "end_date": self.end_time})

