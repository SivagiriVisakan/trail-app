from flask import render_template, g, request, redirect, url_for, flash
from flask.views import MethodView

import auth
import db
from organisation import set_active_org_project

import utils


class ViewProject(MethodView):
    """
    The view that presents a project.
    """

    decorators = [auth.check_valid_org_and_project, auth.login_required]

    def get(self, slug, project_id):
        set_active_org_project(slug, project_id)

        user = g.user
        username = user["username"]

        db_conn = db.get_database_connection()
        show_results = True
        with db_conn.cursor() as cursor:
            sql = 'SELECT `role` FROM `belongs_to` WHERE `username`=%s and `slug`=%s'
            cursor.execute(sql, (username, slug, ))
            role = cursor.fetchone()

            if role["role"] == "Member":
                show_results = False
            
            sql = 'SELECT * FROM `project` WHERE `slug`=%s and `project_id`=%s'
            cursor.execute(sql, (slug, project_id, ))
            result = cursor.fetchone()
            return render_template('organisation/view_project.html', slug=slug, project=result, show_results=show_results) 


class EditProject(MethodView):
    """
    The view that presents a project.
    """

    decorators = [auth.check_valid_org_and_project, auth.login_required]

    def get(self, slug, project_id):
        set_active_org_project(slug, project_id)
        db_conn = db.get_database_connection()

        with db_conn.cursor() as cursor:
            sql = 'SELECT * FROM `project` WHERE `slug`=%s and `project_id`=%s'
            cursor.execute(sql, (slug, project_id, ))
            result = cursor.fetchone()


        set_active_org_project(slug, project_id)

        with db_conn.cursor() as cursor:
            sql = 'SELECT * FROM `project` WHERE `slug`=%s and `project_id`=%s'
            cursor.execute(sql, (slug, project_id, ))
            result = cursor.fetchone()

            return render_template('organisation/edit_project.html', slug=slug, project=result)

    def post(self, slug, project_id):
        name = request.form.get("name", None)
        description = request.form.get("description", None)
        db_conn = db.get_database_connection()
        with db_conn.cursor() as cursor:
            sql = 'SELECT * FROM `project` WHERE `slug`=%s and `project_id`=%s'
            cursor.execute(sql, (slug, project_id, ))
            result = cursor.fetchone()

        if name and description:
            with db_conn.cursor() as cursor:
                sql = 'UPDATE `project` SET `name`=%s, `description`=%s \
                    WHERE	`project`.`project_id`=%s'
                cursor.execute(sql, (name, description, project_id, ))
                db_conn.commit()
            return redirect(url_for('organisation.view_project',slug=slug,project_id=project_id))

        else:
            if not name:
                flash("Project name can't be empty", "danger")
            if not description:
                flash("Description can't be empty", "danger")

            return render_template('organisation/edit_project.html', slug=slug, project=result)


