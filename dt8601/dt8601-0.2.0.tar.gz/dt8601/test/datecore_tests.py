import unittest
import dt8601.datecore as datecore


class dt8601TestCase(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_easter(self):
        y, m, d = datecore.easter_sunday(2013)
        assert y == 2013 and m == 3 and d == 31


    def test_leap_year(self):
        self.assertTrue(datecore.is_leap_year(2012), 'leap year calculation failed: 2012 is a leap year')
        self.assertFalse(datecore.is_leap_year(2006), 'leap year calculation failed: 2006 is not a leap year')
        self.assertFalse(datecore.is_leap_year(1900), 'leap year calculation failed: 1900 is not a leap year')
        self.assertEqual(datecore.days_in_year(2012), 366, 'leap year does not have correct number of days')


    def test_day_of_year(self):
        self.assertEqual(datecore.day_of_year(2005, 8, 20), 232, 'day 2005-232 == 2005-08-20!')
        self.assertEqual(datecore.doy_to_ymd(2005, 232), (2005, 8, 20), 'day 2005-232 == 2005-08-20!')


    def test_julian_routines(self):
        self.assertEqual(datecore.gregorian_to_julian(2005, 8, 20), 2453603, 'julian 2453603 == 2005-08-20!')
        self.assertEqual(datecore.julian_to_gregorian(2453603), (2005, 8, 20), 'julian 2453603 == 2005-08-20!')
        self.assertEqual(datecore.julian_to_mjd(2453603), 53602.5, 'MJD 53602.5 == JD 2453603')
        self.assertEqual(datecore.mjd_to_julian(53602.5), 2453603.0, 'MJD 53602.5 == JD 2453603')


    def test_day_of_week(self):
        self.assertEqual(datecore.day_of_week(1964, 3, 27), 'FR', '1964-03-27 == Friday')
        self.assertEqual(datecore.day_of_week(1964, 3, 27, fmt='number'), 5, '1964-03-27 == Friday')


    def test_week_routines(self):
        self.assertEqual(datecore.week_of_year(2013, 6, 25), 26, '2013-W26 == 2013-06-24..2013-06-30')
        self.assertEqual(datecore.weeks_in_year(2004), 53, '2004 has 53 weeks')
        self.assertEqual(datecore.weeks_in_year(2005), 52, '2005 has 52 weeks')
        self.assertEqual(datecore.week_to_ymd(2013, 26), (2013, 6, 24), '2013W26 starts at 2013-06-24')

    def test_add_days(self):
        self.assertEqual(datecore.add_days(2013, 3, 31, 1), (2013, 4, 1), '')
        self.assertEqual(datecore.add_days(2012, 2, 28, 1), (2012, 2, 29), '')
        self.assertEqual(datecore.add_days(2013, 2, 28, 1), (2013, 3, 1), '')

    def test_holidays(self):
        self.assertEqual(datecore.load_year(2005, country='DE', state=None)[227], '', '2005-08-15 no holiday in DE*')
        self.assertEqual(datecore.load_year(2005, country='DE', state='BY')[227], 'H', '2005-08-15 is holiday in DE-BY')


class IsoParserTestCase(unittest.TestCase):

    def test_timezone(self):
        self.assertEqual(datecore.iso8601_timezone_parser('+02:00')['tz_offset'], 7200, 'canonical timezone parsing failed')
        self.assertRaises(ValueError, datecore.iso8601_timezone_parser, ('+02:15'))
        self.assertEqual(datecore.iso8601_timezone_parser('Z')['tz_offset'], 0, 'zulu timezone parsing failed')
        self.assertEqual(datecore.iso8601_parser('2013-06-24T12,5+02:00')['tz_offset'], 7200, 'wrong tz offset')

if __name__ == '__main__':
    unittest.main()
