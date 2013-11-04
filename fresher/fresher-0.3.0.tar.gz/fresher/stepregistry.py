#-*- coding: utf-8 -*-
import imp
import logging
import re
import os
import sys
from itertools import chain
import importlib
import pkgutil
import six

__all__ = ['Given', 'When', 'Then', 'Before', 'After', 'AfterStep', 'Transform', 'NamedTransform']
__unittest = 1

log = logging.getLogger('fresher')

class AmbiguousStepImpl(Exception):

    def __init__(self, step, impl1, impl2):
        self.step = step
        self.impl1 = impl1
        self.impl2 = impl2
        if (impl1.func is impl2.func):
            # Determine who defined it
            defined_in = [x for x in step_cache if impl1 in step_cache[x]]
            msg = 'Ambiguous: "%s"\n %s\n %s\nDefined through:\n %s' % \
                  (step.match,
                   impl1.get_location(),
                   impl2.get_location(),
                   "\n".join(defined_in))
        else:
            msg = 'Ambiguous: "%s"\n %s %s\n %s %s' % (step.match,
                                                       impl1.get_location(),
                                                       repr(impl1.func),
                                                       impl2.get_location(),
                                                       repr(impl2.func))

        super(AmbiguousStepImpl, self).__init__(msg)

class UndefinedStepImpl(Exception):

    def __init__(self, step):
        self.step = step
        super(UndefinedStepImpl, self).__init__('"%s" # %s' % (step.match, step.source_location()))

class StepImpl(object):
    def __init__(self, step_type, spec, func):
        self.step_type = step_type
        self.spec = spec
        self.func = func
        self.named_transforms = []

    def apply_named_transform(self, name, pattern, transform):
        if name in self.spec:
            self.spec = self.spec.replace(name, pattern)
            self.named_transforms.append(transform)
            if hasattr(self, 're_spec'):
                del self.re_spec

    def run(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def match(self, match):
        if not hasattr(self, 're_spec'):
            self.re_spec = re.compile(self.spec)
        return self.re_spec.match(match)

    def get_location(self):
        code = self.func.__code__
        return "%s:%d" % (code.co_filename, code.co_firstlineno)

class HookImpl(object):

    def __init__(self, cb_type, func, tags=[]):
        self.cb_type = cb_type
        self.tags = tags
        self.func = func
        self.tags = tags
        self.order = 0

    def __repr__(self):
        return "<Hook: @%s %s(...)>" % (self.cb_type, self.func.__name__)

    def run(self, scenario):
        return self.func(scenario)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class TransformImpl(object):

    def __init__(self, spec_fragment, func):
        self.spec_fragment = spec_fragment
        self.re_spec = re.compile(spec_fragment)
        self.func = func

    def is_match(self, arg):
        if arg is None:
            return False
        return self.re_spec.match(arg) != None

    def transform_arg(self, arg):
        match = self.re_spec.match(arg)
        if match:
            return self.func(*match.groups())

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)

class NamedTransformImpl(TransformImpl):

    def __init__(self, name, in_pattern, out_pattern, func):
        super(NamedTransformImpl, self).__init__(out_pattern, func)
        self.name = name
        self.in_pattern = in_pattern
        self.out_pattern = out_pattern

    def apply_to_step(self, step):
        step.apply_named_transform(self.name, self.in_pattern, self)


class StepImplLoadException(Exception):
    def __init__(self, exc):
        self.exc = exc


class StepImplLoader(object):
    # Create a package in which we'll load all the steps modules
    if "fresher.steps" not in sys.modules:
        steps_pkg = imp.new_module("fresher.steps")
        steps_pkg.__path__ = []
        sys.modules["fresher.steps"] = steps_pkg
    else:
        raise Exception("fresher.steps already defined!")

    def __init__(self):
        self.modules = {}

    def load_steps_impl(self, registry, topdir, path, module_names=None):
        """
        Load the step implementations at the given path, with the given module names. If
        module_names is None then the module 'steps' is searched by default.
        """

        if not module_names:
            module_names = ['steps']

        path = os.path.abspath(path)

        for module_name in module_names:
            mod = self.modules.get((path, module_name))

            if mod is None:
                #log.debug("Looking for step def module '%s' in %s" % (module_name, path))
                cwd = os.getcwd()
                if cwd not in sys.path:
                    sys.path.append(cwd)

                actual_module_name = os.path.basename(module_name)
                complete_path = os.path.join(path, os.path.dirname(module_name))

                # We still do this to emulate the behavior of fresher so that
                # we just return if the module does not exist at all rather
                # than raise an error. Maybe this should be changed...
                try:
                    imp.find_module(actual_module_name, [complete_path])
                except ImportError:
                    #log.debug("Did not find step defs module '%s' in %s" % (module_name, path))
                    return

                pkg = self.find_pkg_for_import(topdir, complete_path)

                try:
                    mod = importlib.import_module(
                        pkg + "." + actual_module_name)
                except:
                    exc = sys.exc_info()
                    raise StepImplLoadException(exc)

                def walk_error(x):
                    raise StepImplLoadException((ImportError, "can't load " + x,
                                                 None))

                propagate_steps_to_parent(mod)

                self.modules[(path, module_name)] = mod

            # Add the items from the module itself.
            for item in step_cache.get(mod.__name__, []):
                registry.add_step(item.step_type, item)

            # The module is a package, add the items from its
            # submodules and subpackages.
            if hasattr(mod, "__path__"):
                for candidate in step_cache:
                    if candidate.startswith(mod.__name__):
                        for item in step_cache[candidate]:
                            registry.add_step(item.step_type, item)

            for item_name in dir(mod):
                item = getattr(mod, item_name)
                if isinstance(item, HookImpl):
                    registry.add_hook(item.cb_type, item)
                elif isinstance(item, NamedTransformImpl):
                    registry.add_named_transform(item)
                elif isinstance(item, TransformImpl):
                    registry.add_transform(item)

    def find_pkg_for_import(self, topdir, path):
        """
        Finds the package that should receive the module. It also modifies
        the package's ``__path__`` to load the module.

        :param topdir: The top directory of the test suite.
        :type topdir: :class:`str`
        :param path: The complete absolute path of the module.
        :type path: :class:`str`
        :returns: A package name
        :rtype: :class:`str`
        """
        a_path = os.path.abspath(path)
        a_topdir = os.path.abspath(topdir)
        if os.path.commonprefix([a_path, a_topdir]) != a_topdir:
            raise ValueError("path is not in topdir")

        def splitpath(head):
            if os.path.isabs(head):
                raise ValueError("can't call splitpath with absolute path")
            ret = []
            while head:
                (head, tail) = os.path.split(head)
                if tail:
                    ret[0:0] = [tail]

            return ret

        rel = os.path.relpath(a_path, a_topdir)
        parts = splitpath(rel)
        parent = self.steps_pkg
        search_path = a_topdir
        for part in parts:
            new_name = parent.__name__ + "." + part
            mod = sys.modules.get(new_name)
            if not mod:
                mod = imp.new_module(new_name)
                sys.modules[new_name] = mod
            search_path = os.path.join(search_path, part)
            if "__path__" not in dir(mod):
                mod.__path__ = [search_path]
            elif search_path not in mod.__path__:
                mod.__path__.append(search_path)
            parent = mod

        return parent.__name__


class StepImplRegistry(object):

    def __init__(self, tag_matcher_class):
        self.steps = {
            'given': [],
            'when': [],
            'then': []
        }

        self.hooks = {
            'before': [],
            'after': [],
            'after_step': []
        }

        self.transforms = []
        self.named_transforms = []
        self.tag_matcher_class = tag_matcher_class

    def add_step(self, step_type, step):
        if step not in self.steps[step_type]:
            self.steps[step_type].append(step)
        for named_transform in self.named_transforms:
            named_transform.apply_to_step(step)

    def add_hook(self, hook_type, hook):
        self.hooks[hook_type].append(hook)

    def add_transform(self, transform):
        self.transforms.append(transform)

    def add_named_transform(self, named_transform):
        self.named_transforms.append(named_transform)
        # pylint: disable=E1101
        for step in chain(*(self.steps.values() if not six.PY3 else
                            list(self.steps.values()))):
            named_transform.apply_to_step(step)

    def _apply_transforms(self, arg, step):
        for transform in chain(step.named_transforms, self.transforms):
            if transform.is_match(arg):
                return transform.transform_arg(arg)
        return arg

    def find_step_impl(self, step):
        """
        Find the implementation of the step for the given match string. Returns the StepImpl object
        corresponding to the implementation, and the arguments to the step implementation. If no
        implementation is found, raises UndefinedStepImpl. If more than one implementation is
        found, raises AmbiguousStepImpl.

        Each of the arguments returned will have been transformed by the first matching transform
        implementation.
        """
        result = None
        for si in self.steps[step.step_type]:
            matches = si.match(step.match)
            if matches:
                if result:
                    raise AmbiguousStepImpl(step, result[0], si)

                args = [self._apply_transforms(arg, si) for arg in matches.groups()]
                result = si, args

        if not result:
            raise UndefinedStepImpl(step)
        return result

    def get_hooks(self, cb_type, tags=[]):
        hooks = [h for h in self.hooks[cb_type] if self.tag_matcher_class(h.tags).check_match(tags)]
        hooks.sort(key=lambda x: x.order)
        return hooks

step_cache = {}

def step_decorator(step_type):
    def decorator_wrapper(spec):
        """ Decorator to wrap step definitions in. Registers definition. """
        def wrapper(func):
            ret = StepImpl(step_type, spec, func)
            steps = step_cache.setdefault(func.__module__, [])
            steps.append(ret)
            return ret
        return wrapper
    return decorator_wrapper


def merge_steps_no_dup(into, other):
    into.extend([x for x in other if x not in into])

def propagate_steps_to_parent(parent):
    if hasattr(parent, "__path__"):
        to_add = []
        for (_loader, name, ispkg) in pkgutil.iter_modules(parent.__path__,
                                                           parent.__name__ +
                                                           "."):
            if ispkg:
                continue
            to_add.extend(step_cache[importlib.import_module(name).__name__])
        other_steps = step_cache.setdefault(parent.__name__, [])
        merge_steps_no_dup(other_steps, to_add)

def import_steps(other):
    """
    Imports the steps associated with another module into the module
    that calls this function.
    """
    import inspect

    frame = inspect.stack()[1]
    me = inspect.getmodule(frame[0])
    steps = step_cache.setdefault(me.__name__, [])
    package_name = None
    if other.startswith("."):
        if hasattr(me, "__path__"):
            # Package, use it as the reference point.
            package_name = me.__name__
        elif me.__name__.find(".") > -1:
            # Not a package, but *in* a package, use the package as
            # ref point.
            package_name = me.__name__.rsplit(".", 1)[0]
    other_mod = importlib.import_module(other, package=package_name)

    # Propagate the steps defined by submodules to the parent package
    if other_mod.__name__ not in step_cache:
        propagate_steps_to_parent(other_mod)

    merge_steps_no_dup(steps, step_cache[other_mod.__name__])

def hook_decorator(cb_type):
    """ Decorator to wrap hook definitions in. Registers hook. """
    def decorator_wrapper(*tags_or_func):
        if len(tags_or_func) == 1 and six.callable(tags_or_func[0]):
            # No tags were passed to this decorator
            func = tags_or_func[0]
            return HookImpl(cb_type, func)
        else:
            # We got some tags, so we need to produce the real decorator
            tags = tags_or_func
            def d(func):
                return HookImpl(cb_type, func, tags)
            return d
    return decorator_wrapper

def transform_decorator(spec_fragment):
    def wrapper(func):
        return TransformImpl(spec_fragment, func)
    return wrapper

def named_transform_decorator(name, in_pattern, out_pattern=None):
    if out_pattern is None: out_pattern = in_pattern
    def wrapper(func):
        return NamedTransformImpl(name, in_pattern, out_pattern, func)
    return wrapper

Given = step_decorator('given')
When = step_decorator('when')
Then = step_decorator('then')
Before = hook_decorator('before')
After = hook_decorator('after')
AfterStep = hook_decorator('after_step')
Transform = transform_decorator
NamedTransform = named_transform_decorator
