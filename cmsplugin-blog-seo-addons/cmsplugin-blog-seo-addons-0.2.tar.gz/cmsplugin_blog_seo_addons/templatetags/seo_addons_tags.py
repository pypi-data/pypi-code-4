"""Template tags for the ``cmsplugin_blog_seo_addons`` app."""
import re

from django.template import Context, Library

from cms.plugin_rendering import render_placeholder

from ..models import EntrySEOAddon


register = Library()


@register.simple_tag
def get_entry_meta_description(entry, request):
    """Returns the meta description for the given entry."""
    try:
        seoaddon = EntrySEOAddon.objects.get(entry=entry).seoaddon
    except EntrySEOAddon.DoesNotExist:
        pass
    else:
        return seoaddon.get_meta_description()

    # If there is no seo addon found, take the info from the excerpt
    placeholder = entry.placeholders.get(slot='excerpt')

    context = Context({'request': request})
    html = render_placeholder(placeholder, context)

    text = re.sub('<.*?>', '', html)

    if len(text) > 160:
        return '{}...'.format(text[:160])
    return text
