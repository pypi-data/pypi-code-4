"""
Fix incorrect pylint import errors of nose.tools.

pylint cannot detect the PEP-8'd assertion functions that nose provides
in nose.tools, which leads to errors about missing imports.  This
pylint plugin fixes that.

Installation Instructions:

1) Put this file somewhere on your PYTHONPATH.
2) Load it using either the --load-plugins command-line option, or
   adding it to the load-plugins setting in your pylintrc.
"""
from logilab.astng import MANAGER
from logilab.astng.builder import ASTNGBuilder

from nose import tools


function_template = """
def {}(*args, **kwargs):
    pass
"""


def nose_transform(module):
    funcs = ''.join(function_template.format(func_name)
                    for func_name in tools.__all__)
    fake = ASTNGBuilder(MANAGER).string_build(funcs)

    for func_name in tools.__all__:
        if func_name not in module.locals:
            module.locals[func_name] = fake[func_name]


def transform(module):
    if module.name == 'nose.tools':
        nose_transform(module)

from logilab.astng import MANAGER
MANAGER.register_transformer(transform)


def register(linter):
    pass
