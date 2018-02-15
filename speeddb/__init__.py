import click
import logging
from logging.handlers import TimedRotatingFileHandler
import shutil
from flask import Flask, g
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter, current_user
from flask_wtf import CSRFProtect
from statsd import StatsClient
from speeddb import constants as cn, forms, util

mail = Mail()
db = SQLAlchemy()
csrf = CSRFProtect()
statsd = StatsClient()

def create_app(extra_config_options={}):
    # Create the flask app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('speeddb.default_settings')
    app.config.from_pyfile('application.cfg', silent=True)
    app.config.from_mapping(extra_config_options)

    if app.config['ENABLE_LOGGING']: # pragma: no cover
        file_handler = TimedRotatingFileHandler(app.config['LOG_FILENAME'], when='midnight')
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

    global statsd
    statsd = StatsClient(host = app.config['STATSD_HOST'], port = app.config['STATSD_PORT'], prefix = app.config['STATSD_PREFIX'])

    # Setup mail
    mail.init_app(app)

    # Create the database
    db.init_app(app)

    # Create CSRF protection
    csrf.init_app(app)

    # Initialize the oembed cache
    import speeddb.oembed_cache as oembed_cache
    oembed_cache.init_cache(cache_type=app.config['OEMBED_CACHE_TYPE'], cache_dir=app.config['OEMBED_CACHE_FILE_DIRECTORY'], timeout=app.config['OEMBED_CACHE_TIMEOUT'])

    # Create the search index
    import speeddb.search as search
    search.create_index(app.config['WHOOSH_INDEX'])

    from speeddb.views import clip, index, report, search, user, tags
    from speeddb.views import blueprint
    app.register_blueprint(blueprint)

    from speeddb.models.user import User
    import speeddb.models.tags
    import speeddb.models.clips

    # Register the user class
    db_adapter = SQLAlchemyAdapter(db, User)
    user_manager = UserManager(db_adapter, app, register_form=forms.RecaptchaRegisterForm, login_form=forms.LoginFormWithBans)

    @app.before_request
    def before_request():
        g.user = current_user
        g.user_is_admin = util.is_admin(current_user)

    @app.cli.command()
    def init_db(): # pragma: no cover
        click.echo('Creating the db...')
        db.create_all()
        click.echo('Done!')

    @app.cli.command()
    def rebuild_index(): # pragma: no cover
        from speeddb.models.clips import Clip

        click.echo('Removing whoosh directory...')
        shutil.rmtree(app.config['WHOOSH_INDEX'])

        click.echo('Recreating index...')
        search.create_index(app.config['WHOOSH_INDEX'])

        click.echo('Adding clips to index...')
        clips = Clip.query.all()
        search.add_clips(clips)

        click.echo('Done!')

    @app.cli.command()
    @click.argument('name')
    def add_role(name): #pragma: no cover
        if len(name) <= 0 or len(name) > cn.ROLE_NAME_LENGTH:
            click.echo('Name must be between 0 and %d characters' % cn.ROLE_NAME_LENGTH)
            return

        from speeddb.models.user import Role
        role = Role(name=name)
        db.session.add(role)
        db.session.commit()
        click.echo('Created role "%s" (id: %d)' % (role.name, role.id))

    @app.cli.command()
    @click.argument('role_id')
    @click.argument('user_id')
    def add_role_to_user(role_id, user_id): #pragma: no cover
        from speeddb.models.user import Role

        user = User.query.get(user_id)
        if user == None:
            click.echo('User not found')
            return
        
        role = Role.query.get(role_id)
        if role == None:
            click.echo('Role not found')

        click.echo('Adding role %s to %s' % (role.name, user.username))
        user.roles.append(role)
        db.session.add(user)
        db.session.commit()
        click.echo('Done!')

    return app