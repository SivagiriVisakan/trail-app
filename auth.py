"""
This will contain all the functions and views related to user authentication
"""

from functools import wraps

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_bcrypt import check_password_hash, generate_password_hash

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

@blueprint.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))

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

def get_email(email):
    db_conn = db.get_database_connection()
    with db_conn.cursor() as cursor:
        sql = 'SELECT `email` FROM `user` WHERE `email`=%s'
        cursor.execute(sql, (email, ))
        result = cursor.fetchone()
        return result

def check_user_login(username: str, password: str):
    if username and password:
        result = get_user(username, with_password=True)
        if result:  
            return result if check_password_hash(result["password"], password) else None 
    return None



@blueprint.route('/signup',methods=["GET","POST"])
def signup():
    if 'username' in session:
        return redirect(url_for('auth.my_details'))
    if request.method == "GET":
        return render_template('signup.html')
    elif request.method == "POST":
        username = request.form.get("username", None)
        if len(username) > 20:
            flash("Username should not exceed 20 characters","danger")
            return render_template('signup.html')
        first_name = request.form.get("first_name", None)
        if len(first_name) > 30:
            flash("first_name should not exceed 30 characters","danger")
            return render_template('signup.html')
        last_name = request.form.get("last_name", None)
        if len(last_name) > 30:
            flash("last_name should not exceed 30 characters","danger")
            return render_template('signup.html')
        email = request.form.get("email", None)
        password = request.form.get("password", None)
        print(f'{username}')

        if username and first_name and last_name and email and password:
            user = get_user(username)
            if user is not None:
                flash("Username already exists","danger")
                return render_template('signup.html')
            else:
                _email = get_email(email)
                if _email is not None:
                    flash("Email already exists","danger")
                    return render_template('signup.html')
                else:
                    password_hash = generate_password_hash(password)
                    db_conn = db.get_database_connection()                
                    with db_conn.cursor() as cursor:
                        cursor.execute("INSERT INTO `user`(`username`,`email`,`first_name`,`last_name`,`password`) Values (%s, %s, %s, %s, %s)", (username, email, first_name, last_name, password_hash))
                        db_conn.commit();
                    session["username"] = username
                    return redirect(url_for('auth.my_details'))
        else:
            if not username:
                flash("Enter Username", "danger")
            if not first_name:
                flash("Enter First name", "danger")
            if not last_name:
                flash("Enter Last name", "danger")
            if not email:
                flash("Enter Email", "danger")
            if not password:
                flash("Enter Password", "danger")
            
            return render_template('signup.html')