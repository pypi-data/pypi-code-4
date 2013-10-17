import os
import imp
import pkgutil


def load_classes(package_path):
    if os.path.isfile(package_path):
        for name, data in get_classes(load_source(package_path)):
            yield name, data
    else:
        for module in load_package(package_path):
            for name, data in get_classes(module):
                yield name, data


def load_source(source_path):
    name = os.path.splitext(os.path.basename(source_path))[0]
    return imp.load_source(name, source_path)


def load_package(package_path):
    for loader, name, is_pkg in pkgutil.iter_modules([package_path]):
        if is_pkg:
            subpackage_path = os.path.join(package_path, name)
            for module in load_package(subpackage_path):
                yield module
        else:
            yield loader.find_module(name).load_module(name)


def get_classes(module):
    import inspect
    for class_name, Class in inspect.getmembers(module, inspect.isclass):
        methods = [n
                   for n, _ in inspect.getmembers(Class, inspect.isroutine)
                   if '__' not in n]
        yield class_name, {'class': Class, 'methods': methods}
