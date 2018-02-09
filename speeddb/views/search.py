from speeddb import constants as cn, forms, oembed_cache, pagination, search, statsd
from speeddb.views import blueprint
from speeddb.models.clips import Clip
from speeddb.models.tags import Tag
from flask import abort, redirect, render_template, request, url_for

@blueprint.route('/tag/<tag_name>')
def show_tag(tag_name):
    return redirect(url_for('views.show_tag_page', tag_name=tag_name, page=1))

@blueprint.route('/tag/<tag_name>/<int:page>')
def show_tag_page(tag_name, page):
    statsd.incr('views.tag')
    tag = Tag.query.filter_by(name=tag_name).first_or_404()

    clips = tag.clips.order_by(Clip.time_created.desc()).paginate(page, cn.SEARCH_CLIPS_PER_PAGE)
    pagination.fetch_embeds_for_clips(clips.items)

    report_form = forms.ReportForm()

    return render_template('tag.html', clips=clips.items, search_query='Tag: %s' % tag.name, tag_name=tag.name, page=page, page_count=clips.pages, report_form = report_form)

@blueprint.route('/search')
def search_clips():
    statsd.incr('views.search')
    query = request.args.get('q')
    if query == None:
        return redirect(url_for('views.index'))

    page = request.args.get('page')
    if page == None:
        page = 1

    try:
        page = int(page)
    except ValueError:
        abort(400)

    search_results = search.search_clips(query, page)

    page_count = pagination.get_page_count(search_results.length)
    pagination.fetch_embeds_for_clips(search_results.clips)

    report_form = forms.ReportForm()

    return render_template('search.html', clips=search_results.clips, search_query=query, page=page, page_count=page_count, report_form = report_form)