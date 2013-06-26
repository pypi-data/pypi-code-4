"""Parallel Python Software, Common Utilities"""

# Author: Vitalii Vanovschi <support@parallelpython.com>,
#         Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: new BSD.

import threading

def start_thread(name,  target,  args=(),  kwargs={},  daemon=True):
    """Starts a thread"""
    thread = threading.Thread(name=name,  target=target, args=args,  kwargs=kwargs)
    thread.daemon = True
    thread.start()
    return thread


def get_class_hierarchy(clazz):
    classes = []
    if clazz is type(object()):
        return classes
    for base_class in clazz.__bases__:
        classes.extend(get_class_hierarchy(base_class))
    classes.append(clazz)
    return classes


def is_not_imported(arg, modules):
    args_module = str(arg.__module__)
    for module in modules:
        if args_module == module or args_module.startswith(module + "."):
            return False
    return True
