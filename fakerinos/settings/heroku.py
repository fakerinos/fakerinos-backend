from .base_settings import *
import django_heroku
import dj_database_url

DEBUG = False

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(ssl_require=True)
}

ACCOUNT_EMAIL_VERIFICATION = 'none'

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# AWS Storage
INSTALLED_APPS += ['storages']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_AUTO_CREATE_BUCKET = True
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
# S3 Static Files
STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/'
STATICFILES_STORAGE = 'fakerinos.storage_backends.StaticStorage'
# S3 Public Media Files
MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'
DEFAULT_FILE_STORAGE = 'fakerinos.storage_backends.MediaStorage'

django_heroku.settings(locals(), databases=False, test_runner=False, allowed_hosts=False, secret_key=False,
                       staticfiles=False)
