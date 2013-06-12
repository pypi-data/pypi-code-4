__all__ = ('site')

from collections import namedtuple

from django.contrib.sites.models import Site

SiteData = namedtuple('SiteData', 'name domain logo team')

from lime.conf import get_setting

SITE_NAME = get_setting('SITE_NAME')
SITE_DOMAIN = get_setting('SITE_DOMAIN')
SITE_LOGO = get_setting('SITE_LOGO')
SITE_TEAM = get_setting('SITE_TEAM')

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
