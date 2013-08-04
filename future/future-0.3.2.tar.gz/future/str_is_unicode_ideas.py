"""
This module redefines str on Python 2.x to be the unicode type.

It is designed to be used together with the unicode_literals import as
follows:

    from __future__ import unicode_literals
    from future import str_is_unicode

On Python 3.x and normally on Python 2.x, this expression:

    str('blah') is 'blah'

return True.

However, on Python 2.x, with this import:

    from __future__ import unicode_literals

the same expression

    str('blah') is 'blah'

returns False.

This module is designed to be imported together with unicode_literals on
Python 2 to bring the meaning of str() back into alignment with
unprefixed string literals.

Note that str() would then normally call the __unicode__ method on
objects in Python 2. Therefore this module also defines a simple decorator
called python_2_unicode_compatible (borrowed from django.utils.encoding)
which defines __unicode__ and __str__ methods under Python 2. To support
Python 2 and 3 with a single code base, define a __str__ method returning
text and apply the python_2_unicode_compatible decorator to the class.

Limitations on auto-decorate: if a class is defined in function-level
scope or enclosed within the scope of another class, it's harder to get
at the local class statement and modify it through introspection.
"""

from __future__ import unicode_literals

import __builtin__
import inspect
import imp
import logging

from . import six


def python_2_unicode_compatible(klass):
    """
    A decorator that defines __unicode__ and __str__ methods under Python
    2. Under Python 3 it does nothing.
    
    To support Python 2 and 3 with a single code base, define a __str__
    method returning text and apply this decorator to the class.

    The implementation comes from django.utils.encoding.
    """
    if not six.PY3:
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass


def add_unicode_method_to_classes(module):
    """
    Find classes in the module's top-level namespace.
    # tell if they are liked by the :class:`OpinionatedElf`.
    # and tag it with the :param:`extension_tag` as a flag name.
    # Do not attempt to extend already-flagged modules.
    # Do not clobber existing methods with the extension method name.

    Warning: swallows exceptional cases where :param:`module`
        is builtin, frozen, or None.
    """
    name = module.__name__ if module else None
    logging.info('Instrumenting module %s', name)
    # if not module or imp.is_builtin(name) or imp.is_frozen(name):
    #     #    or getattr(module, extension_tag, False):
    #     logging.info('Skipping module: %s', name)
    #     return
    # # module._opinionated_instrumented = True
    classes = inspect.getmembers(module, inspect.isclass)
    print(classes)
    for name, cls in classes:
        logging.debug('%s: %s', name, cls)
        # try:
        #     conforming = IMonster.is_conforming(cls)
        # except AttributeError, e:
        #     if '__abstractmethods__' in str(e): # Abstract class.
        #         continue
        #     raise
        # if not conforming:
        #     continue
        class_name = cls.__name__
        logging.debug('Instrumenting class %s', class_name)
        attr_name = '__unicode__'
        if hasattr(cls, attr_name): # Don't clobber existing methods.
            logging.warn('Method already exists: %s', cls)
            continue
        # logging.info('Setting %s on %s', attr_name, class_name)
        # setattr(cls, attr_name,
        #     lambda self: OpinionatedElf.is_liked_by_class_name.get(
        #         self.__class__.__name__, None))
    return module


def import_decorator(old_import, modules, post_processor):
    """
    :param old_import: The import function to decorate, most likely
        ``__builtin__.__import__``.
    :param modules: A list of strings of module names to hook the
        `post_processor` into.
    :param post_processor: Function of the form
        `post_processor(module) -> module`.
    :return: A new import function, most likely to be assigned to
        ``__builtin__.__import__``.
    """
    assert all(callable(fun) for fun in (old_import, post_processor))
    def new_import(*args, **kwargs):
        module = old_import(*args, **kwargs)
        if args[0] in modules:
            print('Running post_processor on module: {}'.format(args[0]))
            return post_processor(module)
        else:
            return module
    return new_import

# __builtin__.__import__ = import_decorator(__builtin__.__import__,
#                                           ['cStringIO'], #lambda(x): x)
#                                           add_unicode_method_to_classes)


if not six.PY3:
    caller = inspect.currentframe().f_back
    caller.f_globals['str'] = unicode
    # print(caller)
    # print(dir(caller))
    # classes = inspect.getmembers(caller) # , inspect.isclass)
    # import pdb
    # pdb.set_trace()
    # print('Classes are: ******')
    # print(classes)
    # for thing in classes:
    #     if thing == 'A':
    #         print(thing)
    # # for name, module in sys.modules.items():
    # #     extend_monsters(module)


