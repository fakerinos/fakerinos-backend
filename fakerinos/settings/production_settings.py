from .heroku import *

ENVIRONMENT = 'production'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_PORT = 465
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
DEFAULT_FROM_EMAIL = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
ACCOUNT_EMAIL_VERIFICATION = 'none'
