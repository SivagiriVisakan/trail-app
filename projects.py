import json
import datetime

from flask import Blueprint, request, render_template

import db
from utils import check_missing_keys

blueprint = Blueprint('projects', __name__, url_prefix='/projects')


# TODO: Restrict access to projects based on user

@blueprint.route('/<string:project_id>/dashboard')
def project_dashboard(project_id):
    return render_template('projects/home_dashboard.html')


