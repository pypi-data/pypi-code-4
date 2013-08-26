from django.core.urlresolvers import resolve

__author__ = 'ir4y'


def url_name(request):
    result = {'url_name': None}
    try:
        path = request.get_full_path().split('?')[0]
        result['url_name'] = resolve(path).url_name
    except:
        pass
    return result
