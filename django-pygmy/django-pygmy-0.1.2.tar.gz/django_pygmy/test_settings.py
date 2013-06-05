DEBUG = True

SECRET_KEY = 'rudea(_8&amp;q$f3z5!$)4eaa)(l=2rd4lifz(i0ti4v^1zg%6#&amp;8'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MEDIA_URL = ''
STATIC_URL = ''

INSTALLED_APPS = (
    'django_pygmy.tests',
    'django_pygmy',
)
