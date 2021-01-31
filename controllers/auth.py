"""
This will contain all the functions and views related to user authentication
"""

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_bcrypt import check_password_hash, generate_password_hash

import helpers.db as db
from helpers.decorators import login_required

blueprint = Blueprint('auth', __name__, url_prefix='/auth')


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
            return render_template('login.html', next=request.args.get("next", None))
        else:
            session["username"] = user["username"]
            if request.args.get('next', None):
                return redirect(request.args["next"])
            return redirect(url_for('organisation.organisation'))

@blueprint.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))

@blueprint.route('/me', methods=["GET"])
@login_required
def my_details():
    return g.user or {}


def get_email(email):
    db_conn = db.get_database_connection()
    with db_conn.cursor() as cursor:
        sql = 'SELECT `email` FROM `user` WHERE `email`=%s'
        cursor.execute(sql, (email, ))
        result = cursor.fetchone()
        return result

def check_user_login(username: str, password: str):
    if username and password:
        result = db.get_user(username, with_password=True)
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
        first_name = request.form.get("first_name", None)
        last_name = request.form.get("last_name", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)
        print(f'{username}')

        if username and first_name and last_name and email and password:
            user = db.get_user(username)
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
                    return redirect(url_for('organisation.organisation'))
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