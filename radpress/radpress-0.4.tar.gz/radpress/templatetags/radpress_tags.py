from django import template
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from radpress import settings as radpress_settings, get_version
from radpress.compat import User
from radpress.models import Article

register = template.Library()


@register.inclusion_tag('radpress/tags/datetime.html')
def radpress_datetime(datetime):
    """
    Time format that compatible with html5.

    Arguments:
    - `datetime`: datetime.datetime
    """
    context = {'datetime': datetime}
    return context


@register.inclusion_tag('radpress/tags/widget_latest_posts.html')
def radpress_widget_latest_posts():
    """
    Receives latest posts.
    """
    limit = radpress_settings.LIMIT
    context = {
        'object_list': Article.objects.all_published()[:limit]
    }
    return context


@register.simple_tag
def radpress_static_url(path):
    """
    Receives Radpress static urls.
    """
    version = get_version()
    return '%sradpress/%s?ver=%s' % (settings.STATIC_URL, path, version)


@register.filter
def radpress_full_name(user):
    if not isinstance(user, User):
        full_name = ''

    else:
        full_name = user.get_full_name()

        if not full_name:
            full_name = user.username

    return full_name


@register.assignment_tag(takes_context=True)
def radpress_get_url(context, o):
    return context['request'].build_absolute_uri(o.get_absolute_url())


@register.assignment_tag
def radpress_zen_mode_url(entry):
    try:
        if not isinstance(entry, Article):
            url = reverse('radpress-zen-mode')
        else:
            url = reverse('radpress-zen-mode-update', args=[entry.pk])

    except NoReverseMatch:
        url = ''

    return url
