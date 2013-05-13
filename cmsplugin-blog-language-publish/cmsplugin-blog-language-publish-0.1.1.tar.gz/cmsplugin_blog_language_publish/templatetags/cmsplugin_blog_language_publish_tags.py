"""Tempalte tags fot the ``cmsplugin_blog_language_publish`` app."""
from django import template
from django.core.exceptions import ObjectDoesNotExist


register = template.Library()


@register.assignment_tag
def get_published_entries(object_list, language_code):
    result = []
    for obj in object_list:
        title = None
        try:
            title = obj.entrytitle_set.get(language=language_code)
        except ObjectDoesNotExist:
            continue

        is_published = False
        if title:
            try:
                is_published = title.is_published.is_published
            except ObjectDoesNotExist:
                continue

        if not is_published:
            continue

        result.append(obj)

    return result
