__all__ = ('locale_url_is_installed',)

from django.conf import settings

def locale_url_is_installed():
    """
    Checks if localeurl is installed in the Django project.

    :return bool:
    """
    if 'localeurl' in settings.INSTALLED_APPS and \
       'localeurl.middleware.LocaleURLMiddleware' in settings.MIDDLEWARE_CLASSES:
       return True
    return False