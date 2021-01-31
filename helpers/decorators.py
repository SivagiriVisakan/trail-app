
from functools import wraps

from flask import abort, g, redirect, request, session, url_for

import helpers.db as db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get("username", None)
        if not username:
            return redirect(url_for('auth.login', next=request.url))
        g.user = db.get_user(username)
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))

        db_conn = db.get_database_connection()

        with db_conn.cursor() as cursor:
            sql = ("SELECT"
                   " belongs_to.slug, project.project_id, organisation.name"
                   " FROM"
                   " `user`"
                   " LEFT OUTER JOIN"
                   " belongs_to ON user.username = belongs_to.username"
                   " LEFT OUTER JOIN"
                   " project ON project.slug = belongs_to.slug"
                   " LEFT OUTER JOIN"
                   " organisation ON organisation.slug = belongs_to.slug"
                   " WHERE"
                   " user.username = %s;")
            cursor.execute(sql, (username, ))
            result = cursor.fetchall()
            g.user["orgs"] = {}
            g.orgs = {}

            if result is not None:
                for record in result:
                    organisation_slug = record["slug"]
                    project_id = record["project_id"]
                    org_data = g.orgs.get(organisation_slug, None) or {
                        "name": record["name"]}
                    l = org_data.get("projects", None) or []
                    org_data["projects"] = l + [project_id]
                    g.orgs[organisation_slug] = org_data

        return f(*args, **kwargs)
    return decorated_function


def check_valid_org_and_project(f):
    """
    Used to restrict access to URLs based on the user.
    Returns 404 if it not a valid page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            # This shouldn't happen, all the endpoints using this decorator must use login_required
            # But just in case.
            return redirect(url_for('auth.login', next=request.url))
        organisation = request.view_args.get(
            'organisation', None) or request.view_args.get('slug', None)
        project_id = request.view_args.get('project_id', None)

        if organisation in g.orgs:
            if project_id is not None and project_id not in g.orgs[organisation]["projects"]:
                # Valid org but invalid project
                abort(404)
        else:
            # Not a valid project
            abort(404)

        return f(*args, **kwargs)
    return decorated_function
