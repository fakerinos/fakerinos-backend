from .base_settings import *
import django_heroku
import dj_database_url

DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(ssl_require=True)
}

ACCOUNT_EMAIL_VERIFICATION = 'optional'

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

django_heroku.settings(locals(), databases=False, test_runner=False, allowed_hosts=False, secret_key=False)
