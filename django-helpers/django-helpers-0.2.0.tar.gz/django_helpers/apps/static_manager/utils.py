from types import StringTypes

from django.contrib.staticfiles import finders

from django_helpers import get_settings_val
from exceptions import PYESPRIMAException, SyntaxErrorException
from storage import add_js_files
from exceptions import StaticFileNotFoundException


INCLUDE_CSS = get_settings_val('STATIC_MANAGER_INCLUDE_CSS', True)
INCLUDE_JS = get_settings_val('STATIC_MANAGER_INCLUDE_JS', True)


def file_exists(name):
    if finders.find(name) is None:
        if get_settings_val('RAISE_STATIC_EXCEPTIONS', True):
            raise StaticFileNotFoundException(name)
        else:
            print StaticFileNotFoundException(name)
            return False
    else:
        return True


def resolve_file_name(file_name):
    t = type(file_name)
    if t in (list, tuple):
        if len(file_name) is 1:
            return file_name[0]
        else:
            raise
    if t in StringTypes:
        return file_name

    raise


def remove_duplicates(arr):
    """
    @summary Removes duplicate entries in the list and
    append the static dir prefix if add static is True.

    @author Muhammed K K
    @rtype list


    @param arr: The list from which duplicates has to be removed.
    @return: The newly created array with duplicates removed.
    """
    new_arr = []
    for js in arr:
        if js not in new_arr:
            new_arr.append(js)
    return new_arr


def has_js(obj):
    """
    @summary Checks whether a object has javascript in it or not.
    @param obj: The object from which has javascript to be checked.
    @return: yes or no
    """
    has_meta = hasattr(obj, '_meta')
    _has_js = hasattr(obj, 'render_js') and getattr(obj, 'has_js', False)

    if not has_meta:
        return _has_js

    _meta = obj._meta
    _has_js_meta = hasattr(obj, 'render_js') and getattr(_meta, 'has_js', False)

    return _has_js or _has_js_meta


def get_js_files(obj):
    """
    @param obj: The object from which the list of javascript files has to be found.
    @return: A list of required javascript file.
    """
    if not has_js(obj):
        return []

    if not hasattr(obj, 'js_files'):
        return []

    files = obj.js_files

    if hasattr(files, '__call__'):
        files = obj.js_files()

    if type(files) not in (list, tuple):
        raise Exception('js_files is not in correct format in %s.' % str(type(obj)))

    files = remove_duplicates(files)
    return files


# noinspection PyUnresolvedReferences
def validate_javascript(code):
    try:
        import pyesprima
    except ImportError:
        raise PYESPRIMAException()
    try:
        pyesprima.parse(code)
        return True
    except Exception:
        return False


def load_js_files_from_context(context):
    js_arr = []
    for dictionary in context.dicts:
        for key, val in dictionary.items():
            js_arr += get_js_files(val)
    return js_arr


def add_js_from_context(context, app_name):
    js_arr = load_js_files_from_context(context)
    add_js_files(app_name, js_arr)


def append_static_arr(arr):
    static_url = get_settings_val('STATIC_URL')
    return [static_url + a for a in arr]


def generate_js_from_context(context, app_name=None):
    js_arr = []
    for dictionary in context.dicts:
        for key, val in dictionary.items():
            if has_js(val):
                js_files = get_js_files(val)

                if app_name is not None:
                    add_js_files(app_name, js_files)

                js_files = append_static_arr(js_files)
                js_code = val.render_js().strip()

                if not validate_javascript(js_code):
                    raise SyntaxErrorException(val)

                js_arr.append({
                    'files': js_files,
                    'js_code': js_code
                })
    return js_arr