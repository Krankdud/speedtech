from speeddb import app
from flask import render_template
from flask_user import login_required

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/profile')
@login_required
def members():
    return 'Profile page'