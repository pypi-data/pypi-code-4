# This file mainly exists to allow python setup.py test to work.
# Read more at http://ericholscher.com/blog/2009/jun/29/enable-setuppy-test-your-django-apps/

import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'testproject.settings'

test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)

from django.test.utils import get_runner
from django.conf import settings

def runtests():
    app_label = ['testapp']
    from django.test.simple import DjangoTestSuiteRunner
    def run_tests(app_label, verbosity, interactive):
        runner = DjangoTestSuiteRunner(verbosity=verbosity, interactive=interactive, failfast=False)
        return runner.run_tests(app_label)
    failures = run_tests(app_label, verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    runtests()