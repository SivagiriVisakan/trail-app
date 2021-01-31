import uuid

from flask import flash, g, redirect, render_template, request, url_for
from flask.views import MethodView

from helpers.decorators import login_required, check_valid_org_and_project
import helpers.db as db
import helpers.utils as utils
from controllers.organisation import set_active_org_project


class ViewProject(MethodView):
    """
    The view that presents a project.
    """

    decorators = [check_valid_org_and_project, login_required]

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

    decorators = [check_valid_org_and_project, login_required]

    def get(self, slug, project_id):
        db_conn = db.get_database_connection()


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


class NewProject(MethodView):
    """
    The view to create a new project.
    """

    decorators = [check_valid_org_and_project, login_required]

    def get(self, slug):
        return render_template('organisation/new_project.html', slug=slug)

    def post(self, slug):

        user = g.user
        username = user["username"]


        project_id = request.form.get("project_id", None)

        if project_id == "new" or project_id == "project":
            flash("project_id is not applicable", "danger")
            return render_template('organisation/new_project.html')

        name = request.form.get("name", None)
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
