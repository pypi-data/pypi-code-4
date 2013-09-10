__title__ = 'django-lime.settings'
__version__ = '0.3'
__build__ = 0x000003
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__all__ = ('SITE_LOGO', 'SITE_TEAM', 'SITE_NAME', 'SITE_DOMAIN')

from lime.conf import get_setting

SITE_NAME = get_setting('SITE_NAME')
SITE_DOMAIN = get_setting('SITE_DOMAIN')
SITE_LOGO = get_setting('SITE_LOGO')
SITE_TEAM = get_setting('SITE_TEAM')
