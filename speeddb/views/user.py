from speeddb import constants as cn, db, forms, pagination, statsd
from speeddb.views import blueprint
from speeddb.models.clips import Clip
from speeddb.models.user import User
from flask import abort, redirect, render_template, request, url_for
from flask_user import current_user, login_required, roles_required

@blueprint.route('/user/<username>')
def user_profile(username):
    return redirect(url_for('views.user_profile_page', username=username, page=1))

@blueprint.route('/user/<username>/<int:page>')
@statsd.timer('views.user.profile')
def user_profile_page(username, page):
    user = User.query.filter_by(username=username).first()
    if user == None:
        abort(404)

    clips = user.clips.order_by(Clip.time_created.desc()).paginate(page, cn.SEARCH_CLIPS_PER_PAGE)
    pagination.fetch_embeds_for_clips(clips.items)
    
    report_form = forms.ReportForm()
    ban_form = forms.BanUserForm(user_id=user.id)

    return render_template('user.html', user=user, clips=clips.items, page=page, page_count=clips.pages, report_form=report_form, ban_form=ban_form)

@blueprint.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
@statsd.timer('views.user.edit')
def user_edit_profile():
    form = forms.EditProfileForm(twitter=current_user.twitter, twitch=current_user.twitch, youtube=current_user.youtube, speedruncom=current_user.speedruncom, discord=current_user.discord)

    if request.method == 'POST' and form.validate():
        # If values in the form are empty, set the empty fields to None
        current_user.twitter = form.twitter.data or None
        current_user.twitch = form.twitch.data or None
        current_user.youtube = form.youtube.data or None
        current_user.speedruncom = form.speedruncom.data or None
        current_user.discord = form.discord.data or None

        with statsd.timer('db.user.edit'):
            db.session.add(current_user)
            db.session.commit()

        statsd.incr('user.edit')

        return redirect(url_for('views.user_profile_page', username=current_user.username, page=1))
    
    return render_template('edit_profile.html', user=current_user, form=form, post_url=url_for('views.user_edit_profile'))

@blueprint.route('/user/ban', methods=['POST'])
@login_required
@roles_required('admin')
def ban_user():
    form = forms.BanUserForm()
    user = User.query.get(form.user_id.data)
    if user == None:
        abort(404)

    user.banned = True
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('views.user_profile_page', username=user.username, page=1))