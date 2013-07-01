import re

from admin import TimestampedAdmin
from admintimestamps.base import TimestampedChangelist
from datetime import datetime, timedelta
from django import test
from django.contrib.auth.models import User
from models import (AlternativeTimestampedItem, FakeTimestampedItem,
                    SingleTimestampedItem, DateStampedItem,
                    NullTimestampedItem)


class TestAdmin(test.TestCase):

    def setUp(self):
        self.admin = TimestampedAdmin(FakeTimestampedItem, None)

    def test_get_changelist(self):
        self.assertTrue(issubclass(
            self.admin.get_changelist(None), TimestampedChangelist),
            'Expected changelist to be a subclass of TimestampedChangelist')

    def test_has_timestamp_fields(self):
        self.assertTrue(hasattr(self.admin, 'timestamp_fields'),
                        'Expected timestamp_fields on ModelAdmin')


class TestChangeList(test.TestCase):

    # Workaround for Django 1.2
    if not hasattr(test.TestCase, 'assertRegexpMatches'):
        def assertRegexpMatches(self, text, expected_regexp, msg=None):
            '''Fail the test unless the text matches the regular expression.'''
            if isinstance(expected_regexp, basestring):
                expected_regexp = re.compile(expected_regexp)
            if not expected_regexp.search(text):
                msg = msg or 'Regexp didn\'t match'
                msg = '%s: %r not found in %r' % (msg,
                                                  expected_regexp.pattern,
                                                  text)
                raise self.failureException(msg)

    def setUp(self):
        FakeTimestampedItem(title='just now',
                            created=datetime.now() - timedelta(minutes=1),
                            modified=datetime.now() - timedelta(minutes=2)
                           ).save()
        FakeTimestampedItem(title='some time ago',
                            created=datetime(2010, 1, 15, 21, 19),
                            modified=datetime(2011, 5, 28, 9, 59)).save()
        AlternativeTimestampedItem(title='alternative').save()
        SingleTimestampedItem(title='single timestamp').save()
        DateStampedItem(title='datestamp').save()
        NullTimestampedItem(title='null timestamp').save()
        user = User.objects.create_user('test', 'test@example.com', 'test')
        user.is_staff = user.is_superuser = True
        user.save()
        self.client.login(username='test', password='test')

    def test_header_row(self):
        response = self.client.get('/admin/testproject/faketimestampeditem/')
        self.assertRegexpMatches(response.content,
                                 r'Created\s*</a></(?:th|div)>')
        self.assertRegexpMatches(response.content,
                                 r'Modified\s*</a></(?:th|div)>')

    def test_recent_cell_values(self):
        response = self.client.get('/admin/testproject/faketimestampeditem/')
        self.assertContains(response, '<td>a minute ago</td>', count=1)
        self.assertRegexpMatches(response.content, r'<td>2\W+minutes\W+ago</td>')

    def test_some_time_ago_values(self):
        response = self.client.get('/admin/testproject/faketimestampeditem/')
        self.assertContains(response, '<td>01/15/2010 9:19 p.m.</td>',
                            count=1)
        self.assertContains(response, '<td>05/28/2011 9:59 a.m.</td>',
                            count=1)

    def test_alternative_header_row(self):
        response = self.client.get(
                     '/admin/testproject/alternativetimestampeditem/')
        self.assertRegexpMatches(response.content,
                                 r'Created at\s*</a></(?:th|div)>')
        self.assertRegexpMatches(response.content,
                                 r'Modified at\s*</a></(?:th|div)>')

    def test_single_header_row(self):
        response = self.client.get('/admin/testproject/singletimestampeditem/')
        self.assertRegexpMatches(response.content,
                                 r'Modified\s*</a></(?:th|div)>')

    def test_datestamp_header_row(self):
        response = self.client.get('/admin/testproject/datestampeditem/')
        self.assertRegexpMatches(response.content,
                                 r'Created\s*</a></(?:th|div)>')
        self.assertRegexpMatches(response.content,
                                 r'Modified\s*</a></(?:th|div)>')

    def test_null_timestamp_header_row(self):
        response = self.client.get('/admin/testproject/nulltimestampeditem/')
        self.assertRegexpMatches(response.content,
            r'Created\s*</a></(?:th|div)>')
        self.assertRegexpMatches(response.content,
            r'Modified\s*</a></(?:th|div)>')

    def test_null_timestamp_cell_values(self):
        response = self.client.get('/admin/testproject/nulltimestampeditem/')
        self.assertRegexpMatches(response.content, r'<th><a[^>]+>null timestamp</a></th>')
        self.assertContains(response, '<td>&nbsp;</td>', count=2)
