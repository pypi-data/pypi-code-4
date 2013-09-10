__title__ = 'django-lime.defaults'
__version__ = '0.3'
__build__ = 0x000003
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__all__ = ('SITE_LOGO', 'SITE_TEAM', 'SITE_NAME', 'SITE_DOMAIN')

_ = lambda s: s

# Relative path to logo (in static files)
SITE_LOGO = "logo.png"

# Website team name
SITE_TEAM = _("Website team")

# Name of the web site. If not None, overrides the Django values.
SITE_NAME = None

# Domain. If not None, overrides the Django values.
SITE_DOMAIN = None
