# SpeedTech
[![Build Status](https://travis-ci.org/Krankdud/speedtech.svg?branch=master)](https://travis-ci.org/Krankdud/speedtech) [![codecov](https://codecov.io/gh/Krankdud/speedtech/branch/master/graph/badge.svg)](https://codecov.io/gh/Krankdud/speedtech) [![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)
SpeedTech is a website for finding speedrunning clips and strategies. The goal is to get all of the clips scattered around Twitter, YouTube, and Twitch and compile them all into one location where people can easily find them.

## Setting up the development server
```bash
git clone https://github.com/Krankdud/speedtech
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
pip install -e .
export FLASK_APP=speeddb.application
flask init_db
flask run
```
The server should be running on localhost:5000

## Configuration
Create a directory named "instance" in the same directory as setup.py. Add configuration settings to "instance/application.py"
Setting | Explanation
------- | -----------
ENABLE_LOGGING | Set to true to enable logging
LOG_FILENAME | Path to the log file
SQLALCHEMY_DATABASE_URI | Database URI. Determines the type of SQL database and specifies the location of the database. Check the [SQLAlchemy documentation](http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls) for which databases are supported
WHOOSH_INDEX | Directory to store the [Whoosh](https://bitbucket.org/mchaput/whoosh/wiki/Home) index
OEMBED_CACHE_TYPE | Type of cache to store the oEmbed contents in. Options are "simple", "memcached", and "file"
OEMBED_CACHE_FILE_DIRECTORY | Directory for the oEmbed cache. Must be set if OEMBED_CACHE_TYPE is "file"
OEMBED_CACHE_TIMEOUT | Time in seconds for contents in the oEmbed cache to become invalid
STATSD_HOST | IP or hostname for the [statsd](https://github.com/etsy/statsd) instance. Used for collecting metrics
STATSD_PORT | Port for the statsd instance
STATSD_PREFIX | Prefix used to differentiate the captured metrics from other metrics
RECAPTCHA_PUBLIC_KEY | Public key for [reCAPTCHA](https://www.google.com/recaptcha/intro/)
RECAPTCHA_PRIVATE_KEY | Private key for reCAPTCHA

Other Flask configuration also belongs in this file. Check the documentation for each of the plugins for configuration values:
* [Flask](http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values)
* [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
* [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.3/config/)
* [Flask-User](http://flask-user.readthedocs.io/en/v0.6/customization.html)
* [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/config.html)

## Testing
Tests use the standard Python unittest module and can be run using:
```bash
python setup.py test
or
coverage run setup.py test
```
