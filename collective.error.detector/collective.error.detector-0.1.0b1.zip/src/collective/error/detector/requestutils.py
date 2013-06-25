""" The module provides utils """
import time
from itertools import imap


from OFS.interfaces import IObjectManager
from Products.CMFCore.interfaces import IContentish, IFolderish


def create_request_info(request, extra_info=None):
    """ It forms the request info """
    # it is not an universal way to get a user name, but it's the simplest.
    user = request.get('AUTHENTICATED_USER', '')
    request_info = {
        'time': time.ctime(),
        'user': user.getId() if hasattr(user, 'getId') else 'Anonymous',
        'data': extra_info,
        'method': request.method,
        'headers': {
            'USER_AGENT': request.get('HTTP_USER_AGENT', ''),
        },
        'path_info': request.get('PATH_INFO', ''),
    }
    return request_info


def plain_dict(params):
    """ Remove unsuitable parameters from params (e.g.:request.form).
        For example, remove ZPublisher.HTTPRequest.FileUpload instance
    """
    return dict(
        (key, value)
        for key, value in params.iteritems()
        if isinstance(value, (str, dict, tuple, list))
    )


def is_request_suitable(request):
    """ It is dedicated to getting only important requests """
    # TODO: find a better solution
    # additional filter
    if any(imap(lambda x: request.PATH_INFO.endswith(x),
                ['.css', '.kss', 'kssValidateField'])):
        return False

    published = request.get('PUBLISHED', None)
    context = getattr(published, '__parent__', None)
    if context is None:
        context = request.PARENTS[0]
    # Filter out CSS and other unimportant things
    interfaces = [IContentish, IFolderish, IObjectManager]
    if any(imap(lambda x: x.providedBy(context), interfaces)):
        return True
