from speeddb import db, forms, oembed_cache, search, statsd, util
from speeddb.views import blueprint
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from flask import abort, redirect, render_template, request, url_for
from flask_user import current_user, login_required

@blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
@statsd.timer('views.clip.upload')
def upload_clip():
    if current_user.banned:
        abort(403)
    
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

        with statsd.timer('db.clip.add'):
            db.session.add(clip)
            db.session.commit()

        search.add_clip(clip)

        statsd.incr('clip.upload')

        return redirect(url_for('views.show_clip', clip_id=clip.id))

    return render_template('upload.html', form=form, post_url=url_for('views.upload_clip'), title='Submit a clip')

@blueprint.route('/clip/<int:clip_id>')
@statsd.timer('views.clip.show')
def show_clip(clip_id):
    clip = Clip.query.get(clip_id)
    if clip is None:
        abort(404)

    clip_embed = oembed_cache.get(clip.url)
    clip.is_twitter = 'class="twitter-tweet"' in clip_embed

    report_form = forms.ReportForm(clip_id=clip_id)
    delete_form = forms.DeleteClipForm(clip_id=clip_id)

    return render_template('clip.html', clip=clip, clip_embed=clip_embed, report_form=report_form, delete_form=delete_form)

@blueprint.route('/clip/<int:clip_id>/edit', methods=['GET', 'POST'])
@login_required
@statsd.timer('views.clip.edit')
def edit_clip(clip_id):
    clip = Clip.query.get(clip_id)

    if clip.user.id != current_user.id:
        abort(403)

    tag_string = ''
    for tag in clip.tags:
        tag_string += tag.name + ','
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

        with statsd.timer('db.clip.edit'):
            db.session.add(clip) 
            db.session.commit()

        search.remove_clip(clip)
        search.add_clip(clip)
    
        statsd.incr('clip.edit')

        return redirect(url_for('views.show_clip', clip_id=clip.id))

    return render_template('upload.html', form=form, post_url=url_for('views.edit_clip', clip_id=clip_id), title='Edit your clip')

@blueprint.route('/clip/delete', methods=['POST'])
@login_required
@statsd.timer('views.clip.delete')
def delete_clip():
    form = forms.DeleteClipForm()
    clip = Clip.query.get(form.clip_id.data)
    if clip == None:
        abort(404)

    if clip.user.id != current_user.id and not util.is_admin(current_user):
        abort(403)

    if form.validate():
        
        search.remove_clip(clip)
        db.session.delete(clip)
        db.session.commit()

    return redirect(url_for('views.index'))
