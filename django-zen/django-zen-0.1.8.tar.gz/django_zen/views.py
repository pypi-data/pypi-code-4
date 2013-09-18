from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django_zen.models import Page
from django.template import loader, RequestContext, Template, TemplateDoesNotExist
from django.utils.safestring import mark_safe


DEFAULT_TEMPLATE = 'pages/default.html'


def page(request, url):
    if not url.startswith('/'):
        url = '/' + url

    try:
        page = get_object_or_404(Page, url__exact=url, published=True)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            page = get_object_or_404(Page, url__exact=url, published=True)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise
    return render_page(request, page)


@csrf_protect
def render_page(request, page):
    try:
        if page.template:
            template = loader.select_template(('pages/' + page.template, DEFAULT_TEMPLATE))
        else:
            template = loader.get_template(DEFAULT_TEMPLATE)
    except TemplateDoesNotExist:
        template = Template(
            "<html>" +
            "<head><title>Template not found</title></head>" +
            "<body>" +
            "<h1>Template {{ page.template }} not found</h1><br>" +
            "{{ page.content|safe }}" +
            "</body>" +
            "</html>"
        )

    page.title = mark_safe(page.title)
    page.content = mark_safe(page.content)

    c = RequestContext(request, {
        'page': page,
    })
    response = HttpResponse(template.render(c))
    return response
