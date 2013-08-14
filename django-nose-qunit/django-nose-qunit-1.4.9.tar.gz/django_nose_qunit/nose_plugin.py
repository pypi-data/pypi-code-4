import logging
import os
import re
import sys

from nose.case import MethodTestCase, Test
from nose.failure import Failure
from nose.plugins import Plugin
from nose.plugins.collect import TestSuiteFactory
from nose.util import test_address

from django_nose_qunit.testcases import QUnitTestCase

log = logging.getLogger('nose.plugins.django_nose_qunit')


class QUnitMethodTestCase(MethodTestCase):
    """
    Subclass of nose's test case class for test methods which produces better
    descriptions for QUnit tests.  Other types of tests continue to use the
    original class.
    """

    def __init__(self, method, test=None, arg=tuple(), descriptor=None):
        super(QUnitMethodTestCase, self).__init__(method, test, arg,
                                                  descriptor)
        module_name = arg[0]
        test_name = arg[1]
        if module_name:
            self.description = '[%s] %s' % (module_name, test_name)
        else:
            self.description = test_name

    def shortDescription(self):
        return self.description

    def __str__(self):
        # Periods and parentheses can confuse the xunit plugin, strip them
        desc = re.sub(r'[\.\(\)]', '', self.description)
        name = "%s.%s.%s" % (self.cls.__module__,
                             self.cls.__name__,
                             desc)
        return name
    __repr__ = __str__


class QUnitIndexPlugin(Plugin):
    """
    Nose plugin which just finds QUnit test cases without actually running
    them.  Used by the view at '/qunit/' which lists all the
    available QUnit test files.
    """

    name = 'django-qunit-index'
    qunit_test_classes = []

    def options(self, parser, env=os.environ):
        super(QUnitIndexPlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        super(QUnitIndexPlugin, self).configure(options, conf)

    def prepareTestLoader(self, loader):
        """Install collect-only suite class in TestLoader.
        """
        # Disable context awareness
        log.debug("Preparing test loader")
        self.__class__.qunit_test_classes = []
        loader.suiteClass = TestSuiteFactory(self.conf)

    def prepareTestCase(self, test):
        """Replace actual test with dummy that always passes.
        """
        # Return something that always passes
        log.debug("Preparing test case %s", test)
        if not isinstance(test, Test):
            return

        def run(result):
            # We need to make these plugin calls because there won't be
            # a result proxy, due to using a stripped-down test suite
            self.conf.plugins.startTest(test)
            result.startTest(test)
            self.conf.plugins.addSuccess(test)
            result.addSuccess(test)
            self.conf.plugins.stopTest(test)
            result.stopTest(test)
        return run

    def wantClass(self, cls):
        if issubclass(cls, QUnitTestCase) and len(cls.test_file) > 0:
            self.qunit_test_classes.append(cls)
            return True
        return False

    def wantFunction(self, function):
        return False


class QUnitPlugin(Plugin):
    """
    Nose plugin which starts PhantomJS and uses it to run QUnit JavaScript
    tests identified by subclasses of QUnitTestCase.
    """

    name = 'django-qunit'

    def options(self, parser, env=os.environ):
        super(QUnitPlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        super(QUnitPlugin, self).configure(options, conf)

    def loadTestsFromTestCase(self, testCaseClass):
        if not issubclass(testCaseClass, QUnitTestCase):
            return None
        if len(testCaseClass.test_file) < 1:
            return None
        log.debug('Loading tests from %s' % testCaseClass.__name__)
        inst = testCaseClass()
        generator = getattr(inst, 'generator')

        def generate(g=generator, c=testCaseClass):
            try:
                for test in g():
                    test_func, arg = (test[0], test[1:])
                    yield QUnitMethodTestCase(test_func, arg=arg, descriptor=g)
            except KeyboardInterrupt:
                raise
            except:
                exc = sys.exc_info()
                yield Failure(exc[0], exc[1], exc[2],
                              address=test_address(generator))
        return self.loader.suiteClass(generate, context=generator,
                                      can_split=False)

    def prepareTestLoader(self, loader):
        self.loader = loader
        return None
