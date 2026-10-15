"""Einstellungen für automatische Tests.

Braucht weder Postgres noch Redis noch Keycloak. Alle Zugriffe auf Keycloak
werden in den Tests ersetzt (siehe conftest.py).
"""
import os

_TEST_ENV = {
    'SECRET_KEY': 'test-only-not-secret',
    'DEBUG': 'False',
    'ALLOWED_HOSTS': 'testserver,localhost',
    'CORS_ORIGIN_WHITELIST': 'http://localhost:8080',
    'USE_RDS_DB': 'False',
    'USE_S3': 'False',
    'USE_SES': 'False',
    'USE_CELERY': 'False',
    'FRONT_URL': 'http://localhost:8080',
    'BASE_URI': 'http://keycloak.invalid/',
    'OIDC_RP_REALMNAME': 'dpv',
    'OIDC_RP_CLIENT_ID': 'scout-frontend',
    'OIDC_RP_CLIENT_SECRET_BACKEND': 'unused',
    'KEYCLOAK_APP_REALM': 'dpv',
    'KEYCLOAK_ADMIN_USER': 'scout-backend',
    'KEYCLOAK_ADMIN_PASSWORD': 'unused',
}
for _key, _value in _TEST_ENV.items():
    os.environ[_key] = _value

from .settings import *  # noqa: E402,F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
SEND_MAIL = False
CELERY_TASK_ALWAYS_EAGER = True
LOGGING = {'version': 1, 'disable_existing_loggers': False}
# Der API-Logger schreibt in einem Hintergrund-Thread. In Tests kollidiert das
# mit dem Aufräumen der Testdatenbank und führt zu zufälligen Fehlern.
MIDDLEWARE = [m for m in MIDDLEWARE if not m.startswith('drf_api_logger.')]
