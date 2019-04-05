import os

ENVIRONMENT = None

# region Django Stuff

# region Basic
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False
ROOT_URLCONF = 'fakerinos.urls'
ALLOWED_HOSTS = ['*']
SITE_ID = 1
# endregion
AUTH_USER_MODEL = 'accounts.User'
INSTALLED_APPS = [
    # Apps
    'fakerinos',
    'chat',
    'accounts',
    'articles',
    'rooms',

    # Third Party
    'guardian',
    'channels',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'rest_auth',
    'rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Builtins
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]
DEFAULT_USER_PERMISSIONS = [
    'add_room',
]

# region Guardian
GUARDIAN_GET_INIT_ANONYMOUS_USER = 'accounts.models.get_anonymous_user_instance'
ANONYMOUS_USER_NAME = None
# endregion

# region Misc
WSGI_APPLICATION = 'fakerinos.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# endregion

# endregion

# region REST Framework
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.AcceptHeaderVersioning',
    'DEFAULT_VERSION': '1.0',
    'DEFAULT_PERMISSION_CLASSES': (
        'fakerinos.permissions.StrictDjangoModelPermissions',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# region REST Auth
LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
LOGIN_REDIRECT_URL = '/api/accounts/user/'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 15
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_PRESERVE_USERNAME_CASING = False
OLD_PASSWORD_FIELD_ENABLED = True
# endregion
# endregion

# region Django Channels
ASGI_APPLICATION = 'fakerinos.routing.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [
                (os.environ['REDIS_URL']),
            ]
        },
    },
}
# endregion
