#setuptools will be installed if it is not been installed
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import sys

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

setup(
     name = 'hello-test',
     version = '1.0-1',
     packages = find_packages(),
     entry_points = {
         'console_scripts' : [
               'hello = hello.hello:hellotest',
         ],
         'hello' : [
               'admin_actions = hello.hello:actions',
               'test_class = hello.hello:test', 
         ],
         'setuptools.installation':[
               'eggsecutable = hello.hello:actions',
         ]
     },
     tests_require=['tox'],
     cmdclass = {'test': Tox},
)
