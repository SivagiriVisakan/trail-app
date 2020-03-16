"""
This will contain all the functions and views related to user authentication
"""

from flask import render_template
from flask import Blueprint

blueprint = Blueprint('auth', __name__, url_prefix='/auth')

@blueprint.route('/login')
def login():
    return render_template('login.html')