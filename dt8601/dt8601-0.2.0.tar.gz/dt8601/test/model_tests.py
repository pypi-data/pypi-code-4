import unittest
import dt8601


class ModelTestCase(unittest.TestCase):

    def test_iso_parser(self):
        res = dt8601.datecore.iso8601_parser('2013-06-21T12:34:56.1234+02:00')
        print res['fraction_value']
        self.assertEqual(res['year'], 2013, 'year parsing failed')
        self.assertEqual(res['month'], 6, 'month parsing failed')
        self.assertEqual(res['day'], 21, 'day parsing failed')
        self.assertEqual(res['hour'], 12, 'hour parsing failed')
        self.assertEqual(res['minute'], 34, 'minute parsing failed')
        self.assertEqual(res['second'], 56, 'seconds parsing failed')
        self.assertEqual(res['fraction_value'], 1234, 'invalid fraction part')
        self.assertEqual(res['tz_offset'], 7200, 'timezone offset invalid')

    def test_iso_formatting(self):
        assert '2013' == dt8601.IsoDate.from_iso_string('2013').iso_string('YYYY')
        assert '2013-06' == dt8601.IsoDate.from_iso_string('2013-06').iso_string('YYYY-MM')
        assert '2013-06-25' == dt8601.IsoDate.from_iso_string('2013-06-25').iso_string('YYYY-MM-DD')
        assert '2013-W26' == dt8601.IsoDate.from_iso_string('2013-06-25').iso_string('YYYY-WWW')
        assert '2013-W26-2' == dt8601.IsoDate.from_iso_string('2013-06-25').iso_string('YYYY-WWW-D')
        assert '2013-176' == dt8601.IsoDate.from_iso_string('2013-06-25').iso_string('YYYY-DDD')

if __name__ == '__main__':
    unittest.main()



