# coding: utf-8
from django.conf import settings
from django_relinking.models import Link
from hashlib import md5

import re


link_template = getattr(
    settings, 'RELINKING_LINK_TEMPLATE',
    u'<a target="{target}" href="{url}">{text}</a>'
)
index_pattern = getattr(
    settings, 'RELINKING_INDEX_PATTERN',
    u'<%=link {}=%>'
)
key_pattern = getattr(
    settings, 'RELINKING_CACHE_PREFIX',
    u'{links_table}.{hash}'
)
enable_cache = getattr(settings, 'RELINKING_ENABLE_CACHE', False)

a_pattern = re.compile(r'<\s*a.*<\s*/\s*a\s*>')


def get_relinked_text(origin):

    class LinkReplacer(object):

        def __init__(self, *a, **k):
            self.replacements = 0
            self.links = []

        def __call__(self, m):
            self.replacements += 1
            self.links.append(m.group(0))
            return index_pattern.format(self.replacements - 1)

    repl = LinkReplacer()
    origin = re.subn(a_pattern, repl, origin)[0]
    links = repl.links

    for link in Link.objects.all():
        for key in link.keys_list:
            i = len(links)
            links.append(link_template.format(
                target=dict(Link.TARGET_CHOICES)[link.target],
                url=link.url,
                text=key
            ))
            if not isinstance(origin, unicode):
                origin = origin.decode('utf-8')
            origin = origin.replace(key, index_pattern.format(i))
    for i, link in enumerate(links):
        origin = origin.replace(index_pattern.format(i), link)
    return origin


def relink_text(origin):
    if enable_cache:
        from django.core.cache import cache
        key = key_pattern.format(
            links_table=Link._meta.db_table,
            hash=md5(
                origin.encode('utf-8') if isinstance(origin, unicode) else origin
            ).hexdigest()
        )
        relinked = cache.get(key, None)
        if relinked is None:
            relinked = get_relinked_text(origin)
            cache.set(key, relinked)
    else:
        relinked = get_relinked_text(origin)
    return relinked
