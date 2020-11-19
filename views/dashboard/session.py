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
        clickhouse_sql = ('SELECT count(distinct(session_id)) AS count FROM `web_events`'
                        ' WHERE  project_id=%(project_id)s AND toDate(time_entered) >= toDateTime(%(start_date)s) AND toDate(time_entered) <= toDateTime(%(end_date)s)')
        r = self.clickhouse_client.execute(clickhouse_sql,
                                         {'project_id': self.project_id,
                                          'start_date': self.start_time.isoformat(),
                                          'end_date':self.end_time.isoformat()})
        count = r[0][0]
        return count

    def get_datewise_sessions_count(self):
        """
            Returns the number of sessions aggregated daywise for dates in the
            time period
        """
        with self.db_conn.cursor(cursor=None) as cursor:

            clickhouse_sql = ('SELECT '
                                   'toDate(time_entered) AS event_date, '
                                   'COUNT(DISTINCT(session_id))  '
                                'FROM '
                                   'web_events '
                                'WHERE '
                                    'project_id=%(project_id)s '
                                    'AND '
                                    'toDate(time_entered) >= toDate(%(start_date)s) AND toDate(time_entered) <= toDate(%(end_date)s)'
                                'GROUP BY '
                                   'event_date '
                                )

            # We need value zero for missing dates
            all_dates_data = {(self.start_time+datetime.timedelta(days=i)
                               ).strftime("%d %b"): 0 for i in range(self.total_days)}
            datewise_data = self.clickhouse_client.execute(clickhouse_sql,
                                          {'project_id': self.project_id,
                                          'start_date': self.start_time.isoformat(),
                                          'end_date':self.end_time.isoformat()})
            dates_from_data = {d.strftime(
                "%d %b"): count for d, count in datewise_data}

            return {**all_dates_data, **dates_from_data}

    def get_os_aggregate(self):
        """
            Returns the top 5 used operating systems for sessions
        """
        sql = ('SELECT'
                    '   os,'
                    '   COUNT(*) as count '
                    'FROM'
                    '   ('
                    '      SELECT DISTINCT'
                    '(session_id),'
                    '         os '
                    '      FROM'
                    '         web_events '
                         'WHERE '
                                    'project_id=%(project_id)s '
                                    'AND '
                                    'toDate(time_entered) >= toDate(%(start_date)s) AND toDate(time_entered) <= toDate(%(end_date)s)'
                    '      ORDER BY'
                    '         time_entered'
                    '   )'
                    'GROUP BY'
                    '   os'
                    ' ORDER BY '
                    'count DESC LIMIT 5')

        os_data = self.clickhouse_client.execute(sql,{'project_id': self.project_id,
                                          'start_date': self.start_time.isoformat(),
                                          'end_date':self.end_time.isoformat()})
        os_aggregate = {}
        if len(os_data) > 0:
            os_aggregate = {os: count for os, count in os_data}
        return os_aggregate

    def get_browser_aggregate(self):
        """
            Returns the top 5 most used browsers for sessions
        """
        sql = ('SELECT'
                    '   browser,'
                    '   COUNT(*) as count '
                    'FROM'
                    '   ('
                    '      SELECT DISTINCT'
                    '(session_id),'
                    '         browser '
                    '      FROM'
                    '         web_events '
                         'WHERE '
                                    'project_id=%(project_id)s '
                                    'AND '
                                    'toDate(time_entered) >= toDate(%(start_date)s) AND toDate(time_entered) <= toDate(%(end_date)s)'
                    '      ORDER BY'
                    '         time_entered'
                    '   )'
                    'GROUP BY'
                    '   browser'
                    ' ORDER BY '
                    'count DESC LIMIT 5')

        browser_data = self.clickhouse_client.execute(sql,{'project_id': self.project_id,
                                          'start_date': self.start_time.isoformat(),
                                          'end_date':self.end_time.isoformat()})
        browser_aggregate = {}
        if len(browser_data) > 0:
            browser_aggregate = {os: count for os, count in browser_data}
        return browser_aggregate

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

        self.clickhouse_client = db.get_clickhouse_client()
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

            print(entry_and_exit_point)
            start_page_count_sql = ('SELECT'
                '   page_url as start_page,'
                '   COUNT(*) AS count '
                'FROM'
                '   web_events '
                'WHERE'
                '   ('
                '      session_id,'
                '      time_entered'
                '   )'
                '   IN '
                '   ('
                '      SELECT'
                '         session_id,'
                '         MIN(time_entered) '
                '      FROM'
                '         web_events '
                         'WHERE '
                                    'project_id=%(project_id)s '
                                    'AND '
                                    'toDate(time_entered) >= toDate(%(start_date)s) AND toDate(time_entered) <= toDate(%(end_date)s)'
                '      GROUP BY'
                '         session_id'
                '   )'
                'GROUP BY'
                '   page_url '
                'ORDER BY'
                '   count DESC')

            start_page_data = self.clickhouse_client.execute(start_page_count_sql,{'project_id': self.project_id,
                                          'start_date': self.start_time.isoformat(),
                                          'end_date':self.end_time.isoformat()})

            entry_point = {}
            for page, count in start_page_data:
                entry_point[page] = count

            # Reports on the end page of sessions
            end_page_count_sql = ('SELECT'
                '   page_url as end_page,'
                '   COUNT(*) AS count '
                'FROM'
                '   web_events '
                'WHERE'
                '   ('
                '      session_id,'
                '      time_entered'
                '   )'
                '   IN '
                '   ('
                '      SELECT'
                '         session_id,'
                '         MAX(time_entered) '
                '      FROM'
                '         web_events '
                         'WHERE '
                            'project_id=%(project_id)s '
                            'AND '
                                'toDate(time_entered) >= toDate(%(start_date)s) AND toDate(time_entered) <= toDate(%(end_date)s)'
                '      GROUP BY'
                '         session_id'
                '   )'
                'GROUP BY'
                '   page_url '
                'ORDER BY'
                '   count DESC')

            end_page_data = self.clickhouse_client.execute(end_page_count_sql,{'project_id': self.project_id,
                                          'start_date': self.start_time.isoformat(),
                                          'end_date':self.end_time.isoformat()})

            exit_point = {}
            for page, count in end_page_data:
                exit_point[page] = count

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
