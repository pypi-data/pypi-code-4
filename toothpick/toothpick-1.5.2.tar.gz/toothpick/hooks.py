import sys
import types
from functools import wraps

'''
These decorators allow you to register functions to be called before, around,
or after certain events in the toothpick object lifecycle.  

Methods that are to be registered as hooks should take a single `self`
argument.

Both `register_hook` and `hook_provider` take a keyword option, `only`, that
allows you to specify if you want to register or fire (respectively) callbacks
at a specific time.  The default is before, around, and after.

Around hooks deserve a special look.  They are written as generator methods,
which look like regular methods, but have a `yield` keyword in the method body.
Consider this `yield` to be the call to the provider fuction.  This gives you
control of before- and after- calls in a single method, which means a shared
scope (stack frame).

'''

HOOKS_FIELD = '_toothpick_hooks'


def register_hook(hook_name, module=None, **options):
    '''
    This method creates a decorator with the same name as the hook being
    registered whose sole purpose is to mark methods on an object as being
    hooks, which will then be called appropriately during a method invocation
    decorated with `hook_provider`.  If `module` is passed, then the decorator
    function will be added to the object passed in, instead of the module
    `toothpick.hooks`.
    '''
    only = options.pop('only', ['before', 'around', 'after'])
    if isinstance(only, types.StringTypes):
        only = [only]

    if not module:
        module = sys.modules[__name__]

    # wrapper method needed to force early parameter binding
    # see http://stackoverflow.com/questions/3107231
    def declare_hook(full_hook_name):
        def hook(fn):
            hooks = getattr(fn, HOOKS_FIELD, [])
            hooks.append(full_hook_name)
            setattr(fn, HOOKS_FIELD, hooks)
            return fn
        setattr(module, full_hook_name, hook)

    for when in only:
        declare_hook('%s_%s' % (when, hook_name))


register_hook('validation')
register_hook('save')
register_hook('create')
register_hook('update')
register_hook('delete')
register_hook('modification')
register_hook('eviction')
register_hook('find', only='after')
register_hook('init', only='after')

def _which_hook(obj):
    return getattr(obj, HOOKS_FIELD, [])


def hook_provider(hook_name, **options):
    only = options.pop('only', ['before', 'around', 'after'])
    if isinstance(only, types.StringTypes):
        only = [only]

    def provides_hook(fn):
        @wraps(fn)
        def closure(model, *args, **kwargs):
            if 'before' in only:
                for hook in model._hooks.get("before_%s" % hook_name, []):
                    hook(model, *args, **kwargs)

            gens = []
            if 'around' in only:
                for hook in model._hooks.get("around_%s" % hook_name, []):
                    gen = hook(model, *args, **kwargs)
                    # make sure our around hooks all yield
                    if isinstance(gen, types.GeneratorType):
                        gens.append(gen)
                    else:
                        raise RuntimeError("around hooks must yield: %s" % \
                                           hook.__name__)

            # call the first part
            for gen in gens:
                gen.next()

            # call the actual function we're decorating
            result = fn(model, *args, **kwargs)

            # call the second part, looping in reverse order
            for gen in gens[::-1]:
                try:
                    gen.next()
                except StopIteration:
                    pass
                else: 
                    raise RuntimeError("too many yields in hook: %s" % \
                                       gen.__name__)

            if 'after' in only:
                for hook in model._hooks.get("after_%s" % hook_name, []):
                    hook(model, *args, **kwargs)

            return result

        # retain a reference to the original function
        closure.without_hooks = fn
        return closure

    return provides_hook

