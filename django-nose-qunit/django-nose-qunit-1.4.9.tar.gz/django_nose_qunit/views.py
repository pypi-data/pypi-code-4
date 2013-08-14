import importlib
import urllib

from django.conf import settings as django_settings
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import render

import nose
from django_nose_qunit.conf import settings
from django_nose_qunit.nose_plugin import QUnitIndexPlugin
from django_nose_qunit.testcases import registry


def run_qunit_tests(request):
    """
    Serve a page for running the specified QUnit test file, with JavaScript
    dependencies and HTML fixtures & strings as given in the named test class.  Returns
    a 404 whenever an unknown test class is requested; should only
    happen if somebody is trying to guess URLs.
    """
    test_class_name = urllib.unquote(request.GET.get('class', ''))
    autostart = request.GET.get('autostart', '')
    if autostart == '':
        autostart = django_settings.DEBUG
    else:
        autostart = True if 'true' else False
    if not settings.QUNIT_DYNAMIC_REGISTRY and not test_class_name in registry:
        raise Http404('No such QUnit test case: ' + test_class_name)
    if test_class_name in registry:
        cls = registry[test_class_name]
    else:
        parts = test_class_name.rsplit('.', 1)
        module = importlib.import_module(parts[0])
        cls = getattr(module, parts[1])
    instance = cls('serve_page', request, autostart)
    if hasattr(cls, 'ran_setup'):
        # Part of a test run, test runner is handling setUp and tearDown
        instance.serve_page()
        return instance.response
    # Run the test to trigger setUp(), tearDown() etc.
    result = instance.defaultTestResult()
    instance(result)
    if not instance.response and len(result.errors) > 0:
        trace = result.errors[0][1]
        # Print the error for visibility in interactive testing with DEBUG = False
        print trace
        raise Exception(trace)
    return instance.response


def test_index(request):
    """
    Serve a page which lists all the QUnit test pages, so they can be run in
    a browser more easily.
    """
    if not settings.QUNIT_DYNAMIC_REGISTRY:
        raise Http404('Dynamic lookup of QUnit tests is disabled')
    nose.run(argv=['', '--with-django-qunit-index'])
    classes = QUnitIndexPlugin.qunit_test_classes
    test_classes = []
    base_url = reverse('django-nose-qunit-test')
    for cls in classes:
        qualified_name = '%s.%s' % (cls.__module__, cls.__name__)
        test_classes.append({
            'class': qualified_name,
            'url': '%s?class=%s&autostart=true' % (base_url, qualified_name),
            'script': cls.test_file,
        })
    context = {'test_classes': test_classes}
    return render(request, 'django_nose_qunit/list.html', context)


def fake_raw_script(request):
    """
    Returns a script with a global variable `raw_script` set to true. Used in
    testing the `raw_script_urls` option.
    """

    return HttpResponse('var raw_script = true;', 'text/javascript')
