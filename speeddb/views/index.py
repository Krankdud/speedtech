from speeddb import app
from flask import g, render_template
from flask_user import current_user

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def index():
    return render_template('index.html')