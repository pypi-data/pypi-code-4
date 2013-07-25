"""
Utilities module used in template_pages.
"""
from django.conf import settings


def get_ctx(request, path):
    """
    Get context from given path using
    settings.TEMPLATE_PAGES_CONTEXT_MODULE
    and 'this_is_pathto' function for this/is/path-to path.
    (/ is _ and - are ommited)
    
    When path is not set we search for 'index' function in
    settings.TEMPLATE_PAGES_CONTEXT_MODULE.
    
    We always update RequestContext dictionary
    """
    ctx = {}
    if getattr(settings, 'TEMPLATE_PAGES_CONTEXT_MODULE', False):
        # get rid of / at beginning
        if path[0] == '/':
            path = path[1:]

        if not path:
            function_name = 'index'
        else:
            function_name = path.replace(u'/', u'_').replace(u'-', u'')

        module = __import__(settings.TEMPLATE_PAGES_CONTEXT_MODULE, globals(), locals(), [function_name])
        ctx_function = getattr(module, function_name, None)
        if ctx_function:
            ctx = ctx_function(request)
    return ctx

