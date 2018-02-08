import click
import logging
from logging.handlers import TimedRotatingFileHandler
import shutil
from flask import Flask, g
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter, current_user
from flask_wtf import CSRFProtect

mail = Mail()
db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(extra_config_options={}):
    # Create the flask app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('speeddb.default_settings')
    app.config.from_pyfile('application.cfg', silent=True)
    app.config.from_mapping(extra_config_options)

    if app.config['ENABLE_LOGGING']: # pragma: no cover
        file_handler = TimedRotatingFileHandler(app.config['LOGGER_FILENAME'], when='midnight')
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

    # Setup mail
    mail.init_app(app)

    # Create the database
    db.init_app(app)

    # Create CSRF protection
    csrf.init_app(app)

    # Initialize the oembed cache
    import speeddb.oembed_cache as oembed_cache
    oembed_cache.init_cache()

    # Create the search index
    import speeddb.search as search
    search.create_index(app.config['WHOOSH_INDEX'])

    from speeddb.views import clip, index, report, search, user
    from speeddb.views import blueprint
    app.register_blueprint(blueprint)

    from speeddb.models.user import User
    import speeddb.models.tags
    import speeddb.models.clips

    # Register the user class
    db_adapter = SQLAlchemyAdapter(db, User)
    user_manager = UserManager(db_adapter, app)

    @app.before_request
    def before_request():
        g.user = current_user

    @app.cli.command()
    def init_db(): # pragma: no cover
        click.echo('Creating the db...')
        click.echo(app.config['SQLALCHEMY_DATABASE_URI'])
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

    return app