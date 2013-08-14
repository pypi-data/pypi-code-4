from django_nose_qunit import QUnitTestCase


class QUnitIntroTestCase(QUnitTestCase):
    test_file = 'django_nose_qunit/test/qunit_intro.js'
    html_fixtures = ('django_nose_qunit/fixtures/qunit_intro.html',)

class QUnitHTMLStringsTestCase(QUnitTestCase):
    test_file = 'django_nose_qunit/test/qunit_html_strings.js'
    html_strings = ('<div id="dummy">Here\'s the raw HTML for you.</div>',)

class QUnitRawScriptUrlTestCase(QUnitTestCase):
    test_file = 'django_nose_qunit/test/qunit_raw_script.js'
    raw_script_urls = ('/raw-script/',)
