import imp
from django.conf import settings

MODULE_NAME = 'diazo'

def autodiscover():
    """
    Autodiscovers the 'diazo' module in project apps.
    """
    for app in settings.INSTALLED_APPS:
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue

        try:
            imp.find_module(MODULE_NAME, app_path)
        except ImportError:
            continue
        __import__('%s.%s' % (app, MODULE_NAME))
