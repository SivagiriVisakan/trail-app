import json
import datetime

from flask import Blueprint, request, render_template

import db
from utils import check_missing_keys
import auth

blueprint = Blueprint('projects', __name__, url_prefix='/projects')


# TODO: Restrict access to projects based on user

@blueprint.route('/<string:project_id>/dashboard')
@auth.login_required
def project_dashboard(project_id):
    return render_template('projects/home_dashboard.html', template_context={"project_id": project_id})

