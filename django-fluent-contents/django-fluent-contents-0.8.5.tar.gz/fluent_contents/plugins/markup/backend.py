"""
The rendering support of the markup plugin.

This simply re-uses Django's template filters to do the formatting,
"""
from django.core.exceptions import ImproperlyConfigured
from django.contrib.markup.templatetags import markup
from django.utils.safestring import SafeData, mark_safe
from fluent_contents.plugins.markup import appsettings

_languageNames = {
    'restructuredtext': 'reStructuredText',
    'markdown': 'Markdown',
    'textile': 'Textile',
}

# Copy, and allow adding more options.
SUPPORTED_LANGUAGES = dict(markup.register.filters.iteritems())
SUPPORTED_LANGUAGES['markdown'] = lambda text: markup.markdown(text, ','.join(appsettings.FLUENT_MARKUP_MARKDOWN_EXTRAS))

if appsettings.FLUENT_MARKUP_USE_DJANGO_MARKUP:
    # With django-markup installed, it can be used instead of the default Django filters.
    # Since most django-markup filters are meant for simple text enhancements,
    # only use the filters which are really full text markup languages.
    # Note that the enhanced markdown above will also be replaced. Use the MARKUP_SETTINGS setting to configure django-markup instead.
    from django_markup.markup import formatter
    for filter_name, FilterClass in formatter.filter_list.iteritems():
        real_filters = _languageNames.keys() + ['creole']
        if filter_name in real_filters:
            _languageNames[filter_name] = FilterClass.title
            SUPPORTED_LANGUAGES[filter_name] = lambda text: mark_safe(formatter(text, filter_name))

# Format as choices
LANGUAGE_CHOICES = [(n, _languageNames.get(n, n.capitalize())) for n in SUPPORTED_LANGUAGES.keys()]
LANGUAGE_NAMES = dict(LANGUAGE_CHOICES)


def render_text(text, language=None):
    """
    Render the text, reuses the template filters provided by Django.
    """
    # Get the filter
    filter = SUPPORTED_LANGUAGES.get(language, None)
    if not filter:
        raise ImproperlyConfigured("markup filter does not exist: {0}. Valid options are: {1}".format(
            language, ', '.join(SUPPORTED_LANGUAGES.keys())
        ))

    # Convert. The Django markup filters return the literal string on ImportErrors
    markup = filter(text)
    if not isinstance(markup, SafeData):
        raise ImproperlyConfigured("The '{0}' filter did not update the text. Perhaps the required package for the filter is not installed?".format(language))

    return markup
