import os
from json import load, dump

from django.utils.importlib import import_module

from django_helpers import get_settings_val

_IS_DEBUG = get_settings_val('DEBUG', True)
_STORAGES = None
_STATIC_FILES_STORAGE_FILE_NAME = get_settings_val('STATIC_FILES_STORAGE_FILE_NAME', 'STATIC_FILES_STORAGE')


def _storage_file_name():
    """
    Calculates the file path for the storage of the static files.
    @return: The absolute file name for the storage file name.
    """
    settings = os.environ.get('DJANGO_SETTINGS_MODULE')
    module = import_module(settings)
    root = os.path.dirname(module.__file__)
    root = os.path.abspath(root)
    return os.path.join(root, _STATIC_FILES_STORAGE_FILE_NAME)


def _load_data():
    """
    @summary Loads the data from the file.
    """
    global _STORAGES
    path = _storage_file_name()
    try:
        fp = file(path)
        _STORAGES = load(fp)
        fp.close()
    except Exception:
        _STORAGES = {}


def _storage(file_type, app_name):
    if _STORAGES is None:
        _load_data()

    file_storage = _STORAGES.get(file_type)
    if file_storage is None:
        file_storage = {}
        _STORAGES[file_type] = file_storage

    app_storage = file_storage.get(app_name)
    if app_storage is None:
        app_storage = []
        file_storage[app_name] = app_storage

    return app_storage


def save_data():
    """
    @summary Saves the data to the file.
    """
    path = _storage_file_name()
    fp = file(path, 'w')
    dump(_STORAGES, fp, indent=4, sort_keys=True)
    fp.close()


def add_file(file_type, app_name, path, cdn):
    if not _IS_DEBUG:
        return
    storage = _storage(file_type, app_name)

    if cdn is not None:
        path = (path, cdn)

    if path not in storage:
        storage.append(path)


def add_files(file_type, app_name, paths):
    if not _IS_DEBUG:
        return
    storage = _storage(file_type, app_name)
    for path in paths:
        if path not in storage:
            storage.append(path)


def add_js(app_name, path, cdn):
    add_file('js', app_name, path, cdn)


def add_js_files(app_name, files):
    add_files('js', app_name, files)
    save_data()


def add_css(app_name, path, cdn=None):
    add_file('css', app_name, path, cdn)


def get_files(file_type, app_name):
    if not _IS_DEBUG:
        raise

    return_arr = []
    storage = _storage(file_type, app_name)
    for file_name in storage:
        if type(file_name) is tuple:
            file_name, cdn = file_name
        return_arr.append(file_name)
    return return_arr
