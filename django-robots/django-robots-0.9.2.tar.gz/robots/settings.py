from django.conf import settings

#: A list of one or more sitemaps to inform robots about:
SITEMAP_URLS = []
SITEMAP_URLS.extend(getattr(settings, 'ROBOTS_SITEMAP_URLS', []))

USE_SITEMAP = getattr(settings, 'ROBOTS_USE_SITEMAP', True)

CACHE_TIMEOUT = getattr(settings, 'ROBOTS_CACHE_TIMEOUT', None)
