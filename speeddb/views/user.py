from speeddb import app, db, forms, pagination
from speeddb.models.user import User
from flask import abort, redirect, render_template, url_for
from flask_user import login_required

@app.route('/user/<username>')
def user_profile(username):
    return redirect(url_for('user_profile_page', username=username, page=1))

@app.route('/user/<username>/<int:page>')
def user_profile_page(username, page):
    user = User.query.filter_by(username=username).first()
    if user == None:
        abort(404)

    clips = pagination.get_clips_on_page(user.clips, page)
    page_count = pagination.get_page_count(len(user.clips))
    
    report_form = forms.ReportForm()

    return render_template('user.html', user=user, clips=clips, page=page, page_count=page_count, report_form=report_form)

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