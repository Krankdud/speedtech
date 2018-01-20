from speeddb import app, forms
from flask import render_template, request
from flask_user import login_required

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def members():
    return 'Profile page'

@app.route('/upload', methods=['GET', 'POST'])
def submit():
    form = forms.UploadForm()

    if request.method == 'POST':
        return form.title.data
    elif request.method == 'GET':
        return render_template('upload.html', form=form)