# coding: utf-8
from django.conf import settings
from django_relinking.models import Link
from hashlib import md5


link_template = getattr(
    settings, "RELINKING_LINK_TEMPLATE",
    '<a target="{target}" href="{url}">{text}</a>'
)
index_pattern = getattr(
    settings, "RELINKING_INDEX_PATTERN",
    "<%=link {}=%>"
)
key_pattern = getattr(
    settings, "RELINKING_CACHE_PREFIX",
    "{links_table}.{hash}"
)
enable_cache = getattr(settings, "RELINKING_ENABLE_CACHE", False)


def get_relinked_text(origin):
    links = []
    for link in Link.objects.all():
        for key in link.keys_list:
            i = len(links)
            links.append(link_template.format(
                target=dict(Link.TARGET_CHOICES)[link.target],
                url=link.url,
                text=key
            ))
            origin = origin.replace(key, index_pattern.format(i))
    for i, link in enumerate(links):
        origin = origin.replace(index_pattern.format(i), link)
    return origin


def relink_text(origin):
    if enable_cache:
        from django.core.cache import cache
        key = key_pattern.format(
            links_table=Link._meta.db_table,
            hash=md5(origin).hexdigest()
        )
        relinked = cache.get(key, None)
        if relinked is None:
            relinked = get_relinked_text(origin)
            cache.set(key, relinked)
    else:
        relinked = get_relinked_text(origin)
    return relinked
