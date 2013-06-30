from django.conf import settings

TITLE = getattr(settings, 'RADPRESS_TITLE', "Radpress")
DESCRIPTION = getattr(
    settings, 'RADPRESS_DESCRIPTION', "A blog application for Djangonauts")
LIMIT = getattr(settings, 'RADPRESS_LIMIT', 5)
GOOGLE_ANALYTICS_CODE = getattr(settings, 'RADPRESS_GA_CODE', None)
DISQUS = getattr(settings, 'RADPRESS_DISQUS', None)
DEFAULT_MARKUP = getattr(
    settings, 'RADPRESS_DEFAULT_MARKUP', 'restructuredtext')
HIDE_EMAIL = getattr(settings, 'RADPRESS_HIDE_EMAIL', True)

CONTEXT_DATA = {
    'RADPRESS_TITLE': TITLE,
    'RADPRESS_DESCRIPTION': DESCRIPTION,
    'RADPRESS_DISQUS': DISQUS,
    'RADPRESS_GA_CODE': GOOGLE_ANALYTICS_CODE
}

# reader settings
MORE_TAG = '<!-- more -->'

# restructuredtext settings
RST_SETTINGS = getattr(settings, 'RESTRUCTUREDTEXT_FILTER_SETTINGS', {})
RST_SETTINGS.update({
    'initial_header_level': 2,
    'doctitle_xform': True,
    'language_code': 'en',
    'footnote_references': 'superscript',
    'trim_footnote_reference_space': True,
    'default_reference_context': 'view',
    'link_base': '',
})
