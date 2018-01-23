from speeddb import app, db, forms
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from flask import render_template, request
from flask_user import current_user, login_required

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def members():
    return 'Profile page'

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def submit():
    form = forms.UploadForm()

    if request.method == 'POST' and form.validate():
        clip = Clip(title=form.title.data, description=form.description.data, url=form.url.data, user_id=current_user.id)

        for tag_name in form.tags.data.split(','):
            tag_name = tag_name.strip()
            if len(tag_name) > 0:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag is None:
                    tag = Tag(name=tag_name)
            
                clip.tags.append(tag)

        db.session.add(clip)
        db.session.commit()

        return 'Success'

    return render_template('upload.html', form=form)