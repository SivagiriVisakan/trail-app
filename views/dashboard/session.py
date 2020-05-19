import datetime

from flask import redirect, render_template, request, url_for
from flask.views import MethodView

import auth
import db
from organisation import set_active_org_project

import utils


class SessionDashboard(MethodView):
    """
    Class for handling requests related to the project's session view
    """

    decorators = [auth.check_valid_org_and_project, auth.login_required]

    def get_session_count(self):
        """
            Returns the total number of session that occurred 
            in the given timeperiod
        """
        count = 0
        with self.db_conn.cursor(cursor=None) as cursor:

            sql = ('SELECT count(*) AS count FROM `session`'
                   ' WHERE  project_id=%s AND DATE(start_time) >= DATE(%s) AND DATE(start_time) <= DATE(%s)')

            cursor.execute(
                sql, (self.project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchone()
            count = result.get("count", 0)
        return count

    def get_datewise_sessions_count(self):
        """
            Returns the number of sessions aggregated daywise for dates in the
            time period
        """
        with self.db_conn.cursor(cursor=None) as cursor:

            sql = ('SELECT DATE(start_time) AS date, count(*) AS count FROM `session`'
                   ' WHERE  project_id=%s AND DATE(start_time) >= DATE(%s) AND DATE(start_time) <= DATE(%s) GROUP BY DATE(start_time)')

            cursor.execute(
                sql, (self.project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchall()

            # We need value zero for missing dates
            all_dates_data = {(self.start_time+datetime.timedelta(days=i)
                               ).strftime("%d %b"): 0 for i in range(self.total_days)}

            dates_from_data = {record["date"].strftime(
                "%d %b"): record["count"] for record in result}
            return {**all_dates_data, **dates_from_data}

    def get_os_aggregate(self):
        """
            Returns the top 5 used operating systems for sessions
        """
        with self.db_conn.cursor(cursor=None) as cursor:

            sql = ("SELECT JSON_EXTRACT(custom_data, '$.OS') AS OS, COUNT(*) AS count"
                   " FROM `session` s INNER JOIN "
                   " (SELECT session_id, custom_data FROM web_event WHERE event_type='pageview' GROUP BY session_id, custom_data) w"
                   " ON s.session_id=w.session_id WHERE  project_id=%s AND DATE(start_time) >= DATE(%s) AND DATE(start_time) <= DATE(%s)"
                   " GROUP BY OS ORDER BY count DESC LIMIT 5")

            cursor.execute(
                sql, (self.project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchall()
            return {record["OS"]: record["count"] for record in result}

    def get_browser_aggregate(self):
        """
            Returns the top 5 most used browsers for sessions
        """
        with self.db_conn.cursor(cursor=None) as cursor:
            sql = ("SELECT JSON_EXTRACT(custom_data, '$.browser') AS browser, COUNT(*) AS count"
                   " FROM `session` s INNER JOIN "
                   " (SELECT session_id, custom_data FROM web_event WHERE event_type='pageview' GROUP BY session_id, custom_data) w"
                   " ON s.session_id=w.session_id WHERE  project_id=%s AND DATE(start_time) >= DATE(%s) AND DATE(start_time) <= DATE(%s)"
                   " GROUP BY browser ORDER BY count DESC LIMIT 5")

            cursor.execute(
                sql, (self.project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchall()

            return {record["browser"]: record["count"] for record in result}

    def get(self, organisation, project_id):
        set_active_org_project(organisation, project_id)
        self.organisation = organisation
        self.project_id = project_id

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

        self.total_days = (self.end_time-self.start_time).days + 1

        self.db_conn = db.get_database_connection()

        data = {}
        data["total_sessions"] = self.get_session_count()

        sessions_chart_data = self.get_datewise_sessions_count()
        session_os_data = self.get_os_aggregate()
        session_browser_data = self.get_browser_aggregate()

        with self.db_conn.cursor() as cursor:
            sql = ("SELECT COUNT(*) AS count, start_page, end_page FROM session \
                    WHERE project_id=%s AND DATE(start_time) >= DATE(%s) AND DATE(start_time) <= DATE(%s) \
                    GROUP BY start_page, end_page ORDER BY count DESC")

            cursor.execute(sql, (project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchall()

            entry_and_exit_point = {}
            index = 0
            for row in result:
                index = index + 1
                entry_and_exit_point[index] = row

            sql = ("SELECT COUNT(*) AS count, start_page FROM session WHERE project_id=%s \
                    AND DATE(start_time) >= DATE(%s) AND DATE(start_time) <= DATE(%s) \
                    GROUP BY start_page ORDER BY count DESC")

            cursor.execute(sql, (project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchall()

            entry_point = {}
            for row in result:
                entry_point[row["start_page"]] = row["count"]

            sql = ("SELECT COUNT(*) AS count, end_page FROM session WHERE project_id=%s \
                    AND DATE(start_time) >= DATE(%s) AND DATE(start_time) <= DATE(%s) \
                    GROUP BY end_page ORDER BY count DESC")

            cursor.execute(sql, (project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchall()

            exit_point = {}
            for row in result:
                exit_point[row["end_page"]] = row["count"] 

            sql = ("SELECT start_page as page_url , COUNT(*) AS count FROM session WHERE project_id=%s \
                    AND DATE(start_time) >= DATE(%s) AND DATE(start_time) <= DATE(%s) \
                    GROUP BY start_page")       
            cursor.execute(sql, (project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchall()

            bounce_numerator = {}
            for row in result:
                bounce_numerator[row["page_url"]] = row["count"]

            sql = ("SELECT page_url, COUNT(*) AS count FROM web_event WHERE page_url IN \
                    (SELECT start_page FROM session WHERE start_page=end_page AND project_id = %s AND \
                        DATE(start_time) >= DATE(%s) AND DATE(start_time) <= DATE(%s) ) \
                    AND event_type='pageview' GROUP BY page_url")
            cursor.execute(sql, (project_id, self.start_time.isoformat(), self.end_time.isoformat()))
            result = cursor.fetchall()

            bounce_denominator = {}
            for row in result:
                bounce_denominator[row["page_url"]] = row["count"]

            bounce_rate = {}
            for page_url, count in bounce_denominator.items():
                numerator = bounce_numerator[page_url]
                bounce_rate[page_url] = str(round((numerator/count) * 100, 2)) + '%'


        return render_template('projects/sessions_dashboard.html',
                                template_context={"project_id": project_id, "organisation": organisation,
                                                "start_date": self.start_time, "end_date": self.end_time, "data": data},
                               sessions_chart_data=sessions_chart_data,
                               session_os_data=session_os_data,
                               session_browser_data=session_browser_data,
                                entry_and_exit_point=entry_and_exit_point,
                                entry_point=entry_point,
                                exit_point=exit_point,
                                bounce_rate=bounce_rate

                               )
