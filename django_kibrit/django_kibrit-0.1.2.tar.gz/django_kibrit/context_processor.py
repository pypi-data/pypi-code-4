from django.conf import settings
from django_kibrit.base import GitRevision
from django_kibrit.constants import DJANGO_KIBRIT_CACHED_KEY_ID
from django.core.cache import cache


def revision(request):
    '''
    A context processor to add the "current site" to the current Context
    '''
    cached_tag = cache.get(DJANGO_KIBRIT_CACHED_KEY_ID)
    if cached_tag:
        revision = cached_tag
    else:
        revision = GitRevision(settings.KIBRIT_PATH).revision,
    return {
        'KIBRIT_REVISION': str('?%s'%revision),
        }