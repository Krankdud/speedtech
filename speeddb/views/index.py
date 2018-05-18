from speeddb import db, oembed_cache, statsd
from speeddb.views import blueprint
from speeddb.models.clips import Clip
from flask import g, render_template
from flask_user import current_user
from sqlalchemy import func

@blueprint.route('/')
@statsd.timer('views.index')
def index():
    clips = Clip.query.order_by(Clip.time_created.desc()).limit(20).all()
    clip_count = db.session.query(func.count('*')).select_from(Clip).scalar()

    for clip in clips:
        clip.embed = oembed_cache.get(clip.url)
        clip.is_twitter = 'class="twitter-tweet"' in clip.embed

    return render_template('index.html', clips=clips, clip_count='{:,}'.format(clip_count))

@blueprint.route('/about')
@statsd.timer('views.about')
def about():
    return render_template('about.html')