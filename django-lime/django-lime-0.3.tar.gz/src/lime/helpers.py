__title__ = 'django-lime.helpers'
__version__ = '0.3'
__build__ = 0x000003
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__all__ = ('site')

from collections import namedtuple

from django.contrib.sites.models import Site

SiteData = namedtuple('SiteData', 'name domain logo team')

from lime.settings import SITE_NAME, SITE_DOMAIN, SITE_LOGO, SITE_TEAM

site = None

try:
    current_site = Site.objects.get_current()
    site_name = current_site.name
    domain = current_site.domain
    if SITE_NAME is not None:
        site_name = SITE_NAME
    if SITE_DOMAIN is not None:
        domain = SITE_DOMAIN
    site = SiteData(site_name, domain, SITE_LOGO, SITE_TEAM)
except:
    site = SiteData(SITE_NAME, SITE_DOMAIN, SITE_LOGO, SITE_TEAM)
