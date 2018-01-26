from speeddb import app, constants as cn, db, forms
from speeddb.oembed_cache import get_cached_embed
import speeddb.search as search
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from flask import abort, Markup, redirect, render_template, request, url_for
from flask_user import current_user, login_required
from pyembed.core import PyEmbed

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
@login_required
def members():
    return 'Profile page'

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_clip():
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

        search.add_clip(clip)

        return redirect(url_for('show_clip', clip_id=clip.id))

    return render_template('upload.html', form=form)

@app.route('/clip/<int:clip_id>')
def show_clip(clip_id):
    clip = Clip.query.get(clip_id)
    if clip is None:
        abort(404)

    clip_embed = get_cached_embed(clip.url)

    return render_template('clip.html', clip=clip, clip_embed=clip_embed)

@app.route('/tag/<tag_name>')
def show_tag(tag_name):
    return redirect(url_for('show_tag_page', tag_name=tag_name, page=1))

@app.route('/tag/<tag_name>/<int:page>')
def show_tag_page(tag_name, page):
    if page < 1:
        abort(400)

    tag = Tag.query.filter_by(name=tag_name).first()
    if tag is None:
        abort(404)

    page_count = len(tag.clips) // cn.SEARCH_CLIPS_PER_PAGE
    if len(tag.clips) % cn.SEARCH_CLIPS_PER_PAGE != 0:
        page_count += 1

    if page > page_count:
        return abort(404)

    clips = tag.clips[(page - 1) * cn.SEARCH_CLIPS_PER_PAGE : page * cn.SEARCH_CLIPS_PER_PAGE]
    for clip in clips:
        clip.embed = get_cached_embed(clip.url)

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

    page_count = search_results.length // cn.SEARCH_CLIPS_PER_PAGE
    if search_results.length % cn.SEARCH_CLIPS_PER_PAGE != 0:
        page_count += 1

    for clip in search_results.clips:
        clip.embed = get_cached_embed(clip.url)

    return render_template('search.html', clips=search_results.clips, search_query=query, page=page, page_count=page_count)