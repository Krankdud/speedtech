from speeddb import app, forms, oembed_cache, pagination, search
from speeddb.models.tags import Tag
from flask import abort, redirect, render_template, request, url_for

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

    report_form = forms.ReportForm()

    return render_template('tag.html', clips=clips, search_query='Tag: %s' % tag.name, tag_name=tag.name, page=page, page_count=page_count, report_form = report_form)

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
        clip.embed = oembed_cache.get(clip.url)

    report_form = forms.ReportForm()

    return render_template('search.html', clips=search_results.clips, search_query=query, page=page, page_count=page_count, report_form = report_form)