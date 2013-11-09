import datetime

from django.test import TestCase

from .models import OnCall


class SimpleTest(TestCase):
    def test_get_on_call(self):
        """Test the basic OnCall.get_on_call functionality
        """
        on_call = OnCall(slug='test', rule='on_call = "Alice"')
        self.assertEqual(on_call.get_on_call(), 'Alice')

    def test_weekly(self):
        """Test a week-on round robin
        """
        on_call = OnCall(slug='test', rule='\n'.join([
            'handlers = ["Alice", "Bob", "Charlie"]',
            'week = int(now.strftime("%W"))',
            'on_call = handlers[week % len(handlers)]',
            ]))
        for now, expected in [
                (datetime.datetime(2013, 1, 1), 'Alice'),
                (datetime.datetime(2013, 1, 8), 'Bob'),
                (datetime.datetime(2013, 1, 15), 'Charlie'),
                (datetime.datetime(2013, 1, 22), 'Alice'),
                ]:
            self.assertEqual(on_call.get_on_call(now=now), expected)
