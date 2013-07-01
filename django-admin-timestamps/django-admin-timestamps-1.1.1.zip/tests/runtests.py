import os
import sys


def runtests():
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'testproject.settings'
    from django.conf import settings
    from django.test.utils import get_runner
    try:
        from django.test.simple import DjangoTestSuiteRunner
        run_tests = get_runner(settings)().run_tests
    except ImportError:
        # for Django versions that don't have DjangoTestSuiteRunner
        run_tests = get_runner(settings)
    failures = run_tests(['testproject'], verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
