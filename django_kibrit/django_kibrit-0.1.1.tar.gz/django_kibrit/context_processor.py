from django.conf import settings
from django_kibrit.base import GitRevision


def revision(request):
    '''
    A context processor to add the "current site" to the current Context
    '''
    try:
        revision = GitRevision(settings.KIBRIT_PATH).revision,
    except:
        revision = ''# an empty string
    return {
            'REVISION': str('?%s'%revision),
            'TAG': revision,
        }