from django.conf import settings
from django.utils._os import safe_join
from django.http.response import Http404
from django.shortcuts import render
from django.template.base import TemplateDoesNotExist

from template_pages.utils import get_ctx


def routing_view(request, path):
    # check if path is plain text not utf-8
    try:
        path = str(path)
    except UnicodeEncodeError:
        raise Http404

    # try safely joining paths
    try:
        path = safe_join('/', path)
    except ValueError:
        # in case of trying to get outside of
        # /template_pages/
        raise Http404

    # get extra context for current path
    ctx = {}
    if getattr(settings, 'TEMPLATE_PAGES_CONTEXT_MODULE', False):
        ctx = get_ctx(request, path)

    # try template_pages/#path.html
    first_template_path = u'template_pages%s.html' % path
    try:
        return render(request, first_template_path, ctx)
    except TemplateDoesNotExist, e:
        # Some tags (eg. include) raise
        # TemplateDoesNotExists(PATH) so
        # we need to check template path
        # with raised error and raise them
        if str(e) != first_template_path:
            raise

        # try template_pages/#path/index.html
        try:
            return render(request, u'template_pages%s/index.html' % path, ctx)
        except TemplateDoesNotExist:
            # Return TemplateDoesNotExist
            # errors in debug mode (for
            # developers) otherwise page
            # doesn't exists...
            if settings.DEBUG:
                raise
            raise Http404
