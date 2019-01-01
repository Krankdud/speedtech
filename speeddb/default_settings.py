DEBUG = False
TESTING = False
SECRET_KEY = b'g3\x96*7:\x89\xe2\xa5K\xa3|\x8d\x13D\x9a\xfcO\xa2V\xb0v5\xe9'

ENABLE_LOGGING = True
LOG_FILENAME = 'log'

SQLALCHEMY_DATABASE_URI = 'sqlite://:memory:'
SQLALCHEMY_TRACK_MODIFICATIONS = False

WHOOSH_INDEX = '/tmp/speeddb/whoosh'

OEMBED_CACHE_TYPE = 'simple'
OEMBED_CACHE_FILE_DIRECTORY = None
OEMBED_CACHE_TIMEOUT = 259200 # 3 days

CSRF_ENABLED = True

REPORT_EMAIL = ''

# flask-user
USER_ENABLE_CONFIRM_EMAIL = True
USER_ENABLE_LOGIN_WITHOUT_CONFIRM_EMAIL = False

# flask-mail configuration
MAIL_DEFAULT_SENDER = 'noreply <noreply@speeddb.com>'
MAIL_SERVER = '127.0.0.1'
MAIL_PORT = '25'
MAIL_ERROR_SENDER = 'server-error@speeddb.com'
MAIL_ERROR_RECV = ''
MAIL_ERROR_SUBJECT = 'Server Error'

STATSD_HOST = 'localhost'
STATSD_PORT = 8125
STATSD_PREFIX = 'speeddb'

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
