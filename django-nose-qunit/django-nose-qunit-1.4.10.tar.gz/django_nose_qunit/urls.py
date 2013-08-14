from django.conf.urls.defaults import patterns

# This should be safe to leave in the URL configuration even in production;
# the view always returns a 404 if the test classes haven't been loaded

urlpatterns = patterns('django_nose_qunit.views',
    (r'qunit/$', 'test_index', {}, 'django-nose-qunit-list'),
    (r'^qunit/test/$', 'run_qunit_tests', {}, 'django-nose-qunit-test')
)
