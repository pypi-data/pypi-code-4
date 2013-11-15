# -*- coding: utf-8 -*-
import logging

from datetime import datetime
from django import template
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _

from modeltranslation.settings import AVAILABLE_LANGUAGES

from td_cms.models import Category, Page

register = template.Library()
logger = logging.getLogger(__name__)


@register.assignment_tag
def get_parent_categories():
    """
    Add TD CMS page categories to the context
    """
    return Category.visible_objects.all()


@register.assignment_tag
def get_highlighted_pages():
    """
    Add TD CMS highlighted pages to the context
    """
    return Page.highlighted_objects.all()


@register.assignment_tag
def get_category(slug):
    """
    Add a category to the context given its slug
    """
    for language_code in AVAILABLE_LANGUAGES:
        slug_field = 'slug_%s' % language_code
        try:
            return Category.objects.get(**{slug_field: slug})
        except:
            pass
    logger.warning("Cannot resolve category slug '%s'" % slug)
    return None


@register.assignment_tag
def get_page(slug):
    """
    Add a page to the context given its slug
    """
    for language_code in AVAILABLE_LANGUAGES:
        slug_field = 'slug_%s' % language_code
        try:
            return Page.objects.get(**{slug_field: slug})
        except:
            pass
    logger.warning("Cannot resolve page slug '%s'" % slug)
    return None


@register.filter
def timestamp(value):
    """
    Convert a datetime object representation to a unix timestamp.

    If the object to filter is not a valid datetime.datetime instance, returns
    the original unmodified object.
    """
    if not isinstance(value, datetime):
        return value
    return value.strftime("%s")


@register.inclusion_tag('td_cms/partials/comments/disqus_thread.html')
def show_disqus_thread(page):
    """
    Show the disqus thread for a Page that allows comments
    """
    from td_cms import settings
    # We force settings reloading for testing purpose: when we change the
    # TD_CMS_DISQUS_SHORTNAME in django settings, we need to update td_cms
    # settings
    reload(settings)

    if not settings.DISQUS_SHORTNAME:
        msg = _('TD_CMS_DISQUS_SHORTNAME parameter is missing in your '
                'settings')
        raise ImproperlyConfigured(msg)

    return {
        'page': page,
        'disqus_shortname': settings.DISQUS_SHORTNAME,
    }
