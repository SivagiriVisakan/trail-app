import datetime
from collections import defaultdict

import helpers.db as db
import helpers.utils as utils
from controllers.organisation import set_active_org_project
from flask import redirect, render_template, request, url_for
from flask.views import MethodView
from helpers.decorators import check_valid_org_and_project, login_required


class EventDashboard(MethodView):
    """
    Class for handling requests related to the project's events dashboard
    """

    decorators = [check_valid_org_and_project, login_required]

    def get_event_details(self, start_time, end_time, event_type=None):
        result_to_return = []

        if event_type is None:
            clickhouse_sql = ('SELECT event_type, count(*) AS total_events FROM `web_events`'
                                    'WHERE project_id=%(project_id)s AND toDate(time_entered) >= toDateTime(%(start_date)s)'
                                    'AND toDate(time_entered) <= toDateTime(%(end_date)s)'
                                    'GROUP BY event_type')

            result = self.clickhouse_client.execute(clickhouse_sql,
                                            {'project_id': self.project_id,
                                            'start_date': self.start_time.isoformat(),
                                            'end_date':self.end_time.isoformat()})


            result_to_return = []
            for event, count in result:
                    result_to_return.append({'total_events_count': count, 'event_type': event})
                    
        else:
            clickhouse_sql = ('SELECT event_type, count(*) AS total_events FROM `web_events`'
                                    'WHERE project_id=%(project_id)s AND event_type=%(event_type)s AND toDate(time_entered) >= toDateTime(%(start_date)s)'
                                    'AND toDate(time_entered) <= toDateTime(%(end_date)s)'
                                    'GROUP BY event_type')

            result = self.clickhouse_client.execute(clickhouse_sql,
                                            {'project_id': self.project_id,
                                            'event_type': self.event_type,
                                            'start_date': self.start_time.isoformat(),
                                            'end_date':self.end_time.isoformat()})


            result_to_return = []
            for event, count in result:
                    result_to_return.append({'total_events_count': count, 'event_type': event})
                    
        for event_dict in result_to_return:

            clickhouse_sql = ('SELECT page_url, count(*) as total_events FROM `web_events` '
                                'WHERE project_id=%(project_id)s AND event_type=%(event_type)s'
                                ' AND toDate(time_entered) >= toDateTime(%(start_date)s) '
                                'AND toDate(time_entered) <= toDateTime(%(end_date)s) '
                                'GROUP BY page_url')
            result = self.clickhouse_client.execute(clickhouse_sql,
                                        {
                                          'project_id': self.project_id,
                                          'event_type': event_dict['event_type'],
                                          'start_date': self.start_time.isoformat(),
                                          'end_date':self.end_time.isoformat()
                                        })
            
            pagewise_count = []
            for page_url, count in result:
                    pagewise_count.append({'page_url': page_url, 'total_events_count': count})

            event_dict["page_wise"] = pagewise_count


            clickhouse_sql = ('select custom_data.key, custom_data.value, count(*) from web_events array join custom_data '
                                'WHERE project_id=%(project_id)s AND event_type=%(event_type)s '
                                ' AND toDate(time_entered) >= toDateTime(%(start_date)s)'
                                '   group by custom_data.key, custom_data.value')
            result = self.clickhouse_client.execute(clickhouse_sql,
                                        {
                                          'project_id': self.project_id,
                                          'event_type': event_dict["event_type"],
                                          'start_date': self.start_time.isoformat(),
                                          'end_date':self.end_time.isoformat()
                                        })
            keywise_data = defaultdict(list)
            for key, value, count  in result:
                keywise_data[key].append({'key_value': value, 'key_value_count': count })
            event_dict["custom_data"] = keywise_data
        return result_to_return

    def get(self, organisation, project_id):
        set_active_org_project(organisation, project_id)
        self.organisation = organisation
        self.project_id = project_id
        self.event_type = request.args.get('event_type') or None

        current_timestamp = int(datetime.datetime.now().timestamp())
        default_older_timestamp = int((datetime.datetime.now() - datetime.timedelta(7)).timestamp())
        start_timestamp = request.args.get(
            "start_time", None) or default_older_timestamp

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
        self.clickhouse_client = db.get_clickhouse_client()

        data = self.get_event_details(self.start_time, self.end_time, self.event_type)

        clickhouse_sql = ('SELECT distinct(event_type) FROM `web_events`'
                                'WHERE project_id=%(project_id)s AND toDate(time_entered) >= toDateTime(%(start_date)s)'
                                'AND toDate(time_entered) <= toDateTime(%(end_date)s)'
                                '')

        result = self.clickhouse_client.execute(clickhouse_sql,
                                         {
                                            'project_id': self.project_id,
                                            'start_date': self.start_time.isoformat(),
                                            'end_date':self.end_time.isoformat()
                                         })


        events_list = [row[0] for row in result]

        return render_template('projects/events_dashboard.html', template_context={"project_id": project_id, "organisation": organisation,
                                        "event_data": data, "events_list": events_list, "start_date": self.start_time, "end_date": self.end_time})

