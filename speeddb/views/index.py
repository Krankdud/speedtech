from speeddb.views import blueprint
from flask import g, render_template
from flask_user import current_user

@blueprint.route('/')
def index():
    return render_template('index.html')