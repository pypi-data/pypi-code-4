import os
from .exceptions import LoadError
from .compat import iterkeys


try:
    from importlib import import_module as import_module
except ImportError:
    from .compat import import_module


def load_locations(locations):

    for each in locations:
        try:
            data = each.load()
        except LoadError:
            continue

        yield data


def load_env_python(key):
    path = os.getenv(key, None)
    return load_python(path)


def load_python(path):
    try:
        module = import_module(path).__dict__
    except ImportError:
        raise LoadError

    data = {}

    for key in [x for x in iterkeys(module)
                if not x.startswith('__') and
                x not in('os', 'sys')]:
        data[key] = module[key]

    return data


def load_env_keys(keys):
    data = {}
    for each in keys:
        data[each] = os.getenv(each, None)

    return data


def load_env_path(key):
    path = os.getenv(key, None)

    if path:
        return load_file(path)

    raise LoadError


def load_file(path):
    try:
        with open(os.path.expanduser(path)) as f:
            return f.read()
    except IOError:
        raise LoadError
