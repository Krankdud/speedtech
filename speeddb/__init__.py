import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from flask_wtf import CSRFProtect

# Create the flask app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('speeddb.default_settings')
app.config.from_pyfile('application.cfg', silent=True)

# Create the database
db = SQLAlchemy(app)

# Create CSRF protection
csrf = CSRFProtect(app)

# Initialize the oembed cache
import speeddb.oembed_cache as oembed_cache
oembed_cache.init_cache()

import speeddb.views

from speeddb.models.user import User
import speeddb.models.tags
import speeddb.models.clips

# Register the user class
db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)


@app.cli.command()
def initdb():
    click.echo('Creating the db...')
    click.echo(app.config['SQLALCHEMY_DATABASE_URI'])
    db.create_all()
    click.echo('Done!')