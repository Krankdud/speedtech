from speeddb import app, constants as cn, db, forms
from speeddb.oembed_cache import get_cached_embed
import speeddb.pagination as pagination
import speeddb.search as search
from speeddb.models.user import User
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from flask import abort, g, Markup, redirect, render_template, request, url_for
from flask_user import current_user, login_required
from pyembed.core import PyEmbed

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<username>')
def user_profile(username):
    return redirect(url_for('user_profile_page', username=username, page=1))

@app.route('/user/<username>/<int:page>')
def user_profile_page(username, page):
    user = User.query.filter_by(username=username).first()
    if user == None:
        abort(404)

    if page < 1:
        abort(400)

    clips = pagination.get_clips_on_page(user.clips, page)
    page_count = pagination.get_page_count(len(user.clips))

    return render_template('user.html', user=user, clips=clips, page=page, page_count=page_count)

@app.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
def user_edit_profile():
    form = forms.EditProfileForm(twitter=current_user.twitter, twitch=current_user.twitch, youtube=current_user.youtube, speedruncom=current_user.speedruncom, discord=current_user.discord)

    if request.method == 'POST' and form.validate():
        # If values in the form are empty, set the empty fields to None
        current_user.twitter = form.twitter.data or None
        current_user.twitch = form.twitch.data or None
        current_user.youtube = form.youtube.data or None
        current_user.speedruncom = form.speedruncom.data or None
        current_user.discord = form.discord.data or None

        db.session.add(current_user)
        db.session.commit()

        return redirect(url_for('user_profile_page', username=current_user.username, page=1))
    
    return render_template('edit_profile.html', user=current_user, form=form, post_url=url_for('user_edit_profile'))

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

    clip_embed = get_cached_embed(clip.url)

    return render_template('clip.html', clip=clip, clip_embed=clip_embed)

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

@app.route('/tag/<tag_name>')
def show_tag(tag_name):
    return redirect(url_for('show_tag_page', tag_name=tag_name, page=1))

@app.route('/tag/<tag_name>/<int:page>')
def show_tag_page(tag_name, page):
    tag = Tag.query.filter_by(name=tag_name).first()
    if tag is None:
        abort(404)

    clips = pagination.get_clips_on_page(tag.clips, page)
    page_count = pagination.get_page_count(len(tag.clips))

    return render_template('tag.html', clips=clips, search_query='Tag: %s' % tag.name, tag_name=tag.name, page=page, page_count=page_count)

@app.route('/search')
def search_clips():
    query = request.args.get('q')
    if query == None:
        return redirect(url_for('index'))

    page = request.args.get('page')
    if page == None:
        page = 1

    try:
        page = int(page)
    except ValueError:
        abort(400)

    search_results = search.search_clips(query, page)

    page_count = pagination.get_page_count(search_results.length)

    for clip in search_results.clips:
        clip.embed = get_cached_embed(clip.url)

    return render_template('search.html', clips=search_results.clips, search_query=query, page=page, page_count=page_count)