from speeddb import app
from flask_user import login_required

@app.route('/')
def index():
    return 'Hello, world!'

@app.route('/profile')
@login_required
def members():
    return 'Profile page'