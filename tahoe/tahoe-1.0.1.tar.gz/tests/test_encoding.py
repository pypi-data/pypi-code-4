import datetime
import decimal

from tahoe.encoding import json_handler
from tahoe.tests import TahoeTestCase


class Dummy(object):
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        return dict(
            first_name=self.first_name,
            last_name=self.last_name)


class TestEncoding(TahoeTestCase):
    def test_json_encoder_uses_to_dict(self):
        """
        JSON Encoder will use the to_dict method of a class instance
        """
        first_name = 'clint`'
        last_name = 'ecker'
        dummy = Dummy(first_name=first_name, last_name=last_name)
        dummy_handled = json_handler(dummy)

        assert isinstance(dummy_handled, dict)
        assert dummy_handled.get('first_name') == first_name
        assert dummy_handled.get('last_name') == last_name

    def test_json_encoder_handles_datetimes(self):
        """
        JSON Encoder handles datetimes
        """
        dt = datetime.datetime.utcnow()
        dt_handled = json_handler(dt)

        assert isinstance(dt_handled, basestring)
        assert '.' not in dt_handled

    def test_json_encoder_handles_dates(self):
        """
        JSON Encoder handles dates
        """
        d = datetime.date.today()
        d_handled = json_handler(d)

        assert isinstance(d_handled, basestring)
        assert ':' not in d_handled

    def test_json_encoder_handles_decimals(self):
        """
        JSON Encoder handles decimals
        """
        f = 3.14159265358979
        d = decimal.Decimal(f)
        d_handled = json_handler(d)
        assert isinstance(d_handled, float)
        assert d_handled == f

    def test_json_encoder_returns_unhandled_objects(self):
        """
        JSON Encoder doesn't mess with unhandled objects
        """
        s = "Clint is Cool"
        s_handled = json_handler(s)
        assert s is s_handled
