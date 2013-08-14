import json
import logging
import urllib

from django.core.urlresolvers import reverse
from django.shortcuts import render

from sbo_selenium import SeleniumTestCase

logger = logging.getLogger('django.request')
registry = {}


def qualified_class_name(cls):
    module = cls.__module__
    if module:
        return '%s.%s' % (module, cls.__name__)
    else:
        return cls.__name__


class QUnitTestCase(SeleniumTestCase):
    """
    A test case which runs the QUnit tests in the specified JavaScript files.
    Executes a whole file when the first test case in it is run and caches the
    results for the other test cases in it.  Each QUnit test case
    should have a module name + test name combination that is unique within
    that test file, otherwise the results from different tests will be
    confused.  Does not yet support running a single test or only the tests in
    a particular module, although QUnit supports this.

    test_file and dependencies paths should be relative to STATIC_URL,
    entries in html_fixtures are looked up as templates. html_strings are
    injected directly. raw_script_urls are referenced directly (no STATIC_URL
    processing."""

    test_file = ''
    dependencies = ()
    raw_script_urls = ()
    html_fixtures = ()
    html_strings = ()

    @classmethod
    def setUpClass(cls):
        super(QUnitTestCase, cls).setUpClass()
        registry[qualified_class_name(cls)] = cls

    def setUp(self):
        cls = self.__class__
        cls.ran_setup = True
        # Only start a webdriver if we're in an actual test run
        if hasattr(cls, 'server_thread') and not hasattr(cls, 'generating') and not hasattr(cls, 'results'):
            super(QUnitTestCase, self).setUp()

    def __init__(self, methodName='runTest', request=None, autostart=False):
        """
        Allow the class to be instantiated without a specified test method so
        the generator function can be run by the nose plugin.
        """
        # These attributes get used when serving pages interactively
        self.request = request
        self.autostart = autostart
        self.response = None
        if methodName == 'runTest':
            super(QUnitTestCase, self).__init__('generator')
        else:
            super(QUnitTestCase, self).__init__(methodName)

    def _case_url(self):
        """
        Get the live test server URL for this test case's QUnit test file.
        """
        address = self.live_server_url
        className = urllib.quote(qualified_class_name(self.__class__), safe='')
        url = reverse('django-nose-qunit-test')
        return '%s%s?class=%s' % (address, url, className)

    def _load_case(self):
        """
        Load a test case page and wait until the JS is initialized
        """
        self.sel.get(self._case_url())
        self.wait_for_condition('return QUnit.Django.ready')

    def generator(self):
        """
        Load each file in the browser without actually running the tests in
        order to generate a list of all the test cases.  qunit_case() will be
        called for each test case in the list.
        """
        # Need to start and stop server, since tests aren't running yet
        self.__class__.setUpClass()
        # Start the webdriver also
        super(QUnitTestCase, self).setUp()
        try:
            self.__class__.generating = True
            self._load_case()
            script = 'return JSON.stringify(QUnit.Django.modules)'
            modules = json.loads(self.sel.execute_script(script))
        finally:
            del self.__class__.generating
            self.sel.quit()
            self.__class__.tearDownClass()
        for module_name in modules:
            for test_name in modules[module_name]:
                yield self.qunit_case, module_name, test_name

    def qunit_case(self, module_name, test_name):
        """
        Run the tests in the file if that hasn't been done yet, then get the
        result for the specific test case described.
        """
        if not hasattr(self.__class__, 'results'):
            self._load_case()
            self.sel.execute_script('return QUnit.start()')
            self.wait_for_condition('return QUnit.Django.done')
            script = 'return JSON.stringify(QUnit.Django.results)'
            self.__class__.results = json.loads(self.sel.execute_script(script))
        modules = self.results['modules']
        if not module_name in modules:
            msg = 'Unable to find results for module "%s".  All results: %s'
            msg = msg % (module_name, json.dumps(self.results))
            raise self.failureException(msg)
        tests = modules[module_name]['tests']
        if not test_name in tests:
            msg = 'Unable to find results for test "%s" in module "%s". '
            msg += 'Results for that module: %s'
            msg = msg % (test_name, module_name, json.dumps(self.results))
            raise self.failureException(msg)
        test = tests[test_name]
        if test['failed'] > 0:
            message = ', '.join(test['failedAssertions'])
            raise self.failureException(message)

    def serve_page(self):
        """
        Serve the page with all tests for use in an interactive session.  Runs
        setUp and tearDown once at appropriate times, so test cases can prepare
        templates and database fixtures for use by the page as a whole.
        """
        class_name = qualified_class_name(self.__class__)
        context = {
            'test_file': self.test_file,
            'title': '%s (%s)' % (class_name, self.test_file),
            'dependencies': self.dependencies,
            'raw_script_urls': self.raw_script_urls,
            'fixtures': self.html_fixtures,
            'html_strings': self.html_strings,
            # Can't assume django.core.context_processors.debug is in use
            'autostart': self.autostart,
        }
        self.response = render(self.request, 'django_nose_qunit/template.html',
                               context)
