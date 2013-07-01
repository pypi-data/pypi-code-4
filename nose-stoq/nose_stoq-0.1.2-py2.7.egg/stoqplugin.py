import os
import sys

from nose.plugins import Plugin

if 'STOQ_USE_GI' in os.environ:
    from stoq.lib import gicompat
    gicompat.enable()

class StoqPlugin(Plugin):
    # This is a little hack to make sure that Stoq's database configuration
    # is properly setup. If we import tests.base before Cover.setup() in the
    # coverage plugin is called the statistics will skip the modules imported
    # by tests.base
    def begin(self):
        for path in os.environ['PYTHONPATH'].split(':'):
            sys.path.insert(0, path)

        import tests.base
        tests.base  # pyflakes
