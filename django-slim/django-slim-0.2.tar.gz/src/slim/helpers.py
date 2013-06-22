__title__ = 'slim.helpers'
__version__ = '0.1'
__build__ = 0x000001
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__all__ = ('get_default_language', 'default_language', 'get_languages', 'get_languages_keys', \
           'get_language_from_request', 'smart_resolve')

from django.conf import settings


def get_default_language():
    """
    Gets default language.

    :return str:
    """
    return settings.LANGUAGES[0][0]
default_language = get_default_language()


def get_languages():
    """
    Gets available languages.

    :return iterable:
    """
    return settings.LANGUAGES


def get_languages_keys():
    """
    Returns just languages keys.

    :return list:
    """
    return [key for key, name in get_languages()]


def get_language_from_request(request, default=default_language):
    """
    Gets language from HttpRequest

    :param django.http.HttpRequest:
    :param str default:
    :return str:
    """
    if hasattr(request, 'LANGUAGE_CODE') and request.LANGUAGE_CODE:
        return request.LANGUAGE_CODE
    else:
        return default


def smart_resolve(var, context):
    """
    Resolves variable from context in a smart way. First trying to resolve from context
    and when result is None checks if variable is not None and returns just variable
    when not. Otherwise returns None.

    :param str var:
    :param Context context:
    :return mixed:
    """
    if var is None:
        return None

    ret_val = None
    try:
        ret_val = var.resolve(context, True)
    except:
        ret_val = var
    if ret_val is None:
        ret_val = var

    return ret_val
