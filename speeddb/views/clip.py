from speeddb import app, db, forms, oembed_cache, search
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from flask import abort, redirect, render_template, url_for
from flask_user import login_required

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_clip():
    form = forms.UploadForm()

    if request.method == 'POST' and form.validate():
        clip = Clip(title=form.title.data, description=form.description.data, url=form.url.data, user_id=current_user.id)

        for tag_name in form.tags.data.split(','):
            tag_name = tag_name.strip().lower()
            if len(tag_name) > 0:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag is None:
                    tag = Tag(name=tag_name)
            
                clip.tags.append(tag)

        db.session.add(clip)
        db.session.commit()

        search.add_clip(clip)

        return redirect(url_for('show_clip', clip_id=clip.id))

    return render_template('upload.html', form=form, post_url=url_for('upload_clip'), title='Submit a clip')

@app.route('/clip/<int:clip_id>')
def show_clip(clip_id):
    clip = Clip.query.get(clip_id)
    if clip is None:
        abort(404)

    clip_embed = oembed_cache.get(clip.url)

    report_form = forms.ReportForm(clip_id=clip_id)

    return render_template('clip.html', clip=clip, clip_embed=clip_embed, report_form=report_form)

@app.route('/clip/<int:clip_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_clip(clip_id):
    clip = Clip.query.get(clip_id)

    if clip.user.id != current_user.id:
        abort(403)

    tag_string = ''
    for tag in clip.tags:
        tag_string += tag.name
    form = forms.UploadForm(title=clip.title, description=clip.description, url=clip.url, tags=tag_string)

    if request.method == 'POST' and form.validate():
        clip.title = form.title.data
        clip.description = form.description.data
        clip.url = form.url.data 

        clip.tags.clear()
        for tag_name in form.tags.data.split(','):
            tag_name = tag_name.strip().lower()
            if len(tag_name) > 0:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag is None:
                    tag = Tag(name=tag_name)
            
                clip.tags.append(tag)

        db.session.add(clip) 
        db.session.commit()

        search.remove_clip(clip)
        search.add_clip(clip)

        return redirect(url_for('show_clip', clip_id=clip.id))

    return render_template('upload.html', form=form, post_url=url_for('edit_clip', clip_id=clip_id), title='Edit your clip')