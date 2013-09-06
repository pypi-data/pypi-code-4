from django.test import TestCase
from onesky.inline import *


_tag = 'os-p'

_prefix = '{{__'
_suffix = '__}}'


class OneSkyInlineTest(TestCase):
    def test_trans(self):
        msg = 'Hello World!'
        self.assertEqual(trans(msg), '<%s key=">%s">%s</%s>' % (_tag, msg, msg, _tag))

    def test_trans2(self):
        msg = 'Hello World!'
        self.assertEqual(trans2(msg), _prefix + msg + _suffix)