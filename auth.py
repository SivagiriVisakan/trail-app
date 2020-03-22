"""
This will contain all the functions and views related to user authentication
"""

from functools import wraps

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_bcrypt import check_password_hash

import db

blueprint = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get("username", None)
        if not username:
            return redirect(url_for('auth.login', next=request.url))
        g.user = get_user(username)
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@blueprint.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        user = check_user_login(username, password)
        if not user:
            flash("Invalid username or password", "danger")
            return render_template('login.html')
        else:
            session["username"] = user["username"]
            return redirect(url_for('auth.my_details'))

@blueprint.route('/me', methods=["GET"])
@login_required
def my_details():
    return g.user or {}

def get_user(username, with_password=False):
    db_conn = db.get_database_connection()
    with db_conn.cursor() as cursor:
        sql = 'SELECT * FROM `user` WHERE `username`=%s'
        cursor.execute(sql, (username, ))
        result = cursor.fetchone()
        if result and not with_password:
            result.pop("password")
        return result

def check_user_login(username: str, password: str):
    if username and password:
        result = get_user(username, with_password=True)
        if result:
            return result if check_password_hash(result["password"], password) else None 
    return None
