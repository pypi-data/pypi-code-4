import unittest
from datetime import datetime


class DatetimeMatcherTestCase(unittest.TestCase):

    def test_that_isDateTime_returns_a_DatetimeMatcher(self):
        from ilogue.readable.matching import that
        from ilogue.readable.datetimematcher import DatetimeMatcher
        matcher = that().isDateTime()
        self.assertIsInstance(matcher, DatetimeMatcher)

    def test_withinOneSecondOf_matches_appropriately(self):
        from ilogue.readable.datetimematcher import DatetimeMatcher
        tooEarly = datetime(2011, 6, 5, 23, 41, 20, 400)
        earlier = datetime(2011, 6, 5, 23, 41, 21, 300)
        reference = datetime(2011, 6, 5, 23, 41, 22, 0)
        later = datetime(2011, 6, 5, 23, 41, 22, 900000)
        tooLate = datetime(2011, 6, 5, 23, 41, 23, 400)
        matcher = DatetimeMatcher().withinOneSecondOf(reference)
        self.assertFalse(matcher.matches(tooEarly),
            str(matcher.matchFor(tooEarly)))
        self.assertFalse(matcher.matches(tooLate),
            str(matcher.matchFor(tooLate)))
        self.assertTrue(matcher.matches(earlier),
            str(matcher.matchFor(earlier)))
        self.assertTrue(matcher.matches(later),
            str(matcher.matchFor(later)))

    def test_asString_sets_matcher_to_accept_string_as_other(self):
        from ilogue.readable.datetimematcher import DatetimeMatcher
        tooEarly = str(datetime(2011, 6, 5, 23, 41, 20, 400))
        earlier = str(datetime(2011, 6, 5, 23, 41, 21, 300))
        reference = datetime(2011, 6, 5, 23, 41, 22, 0)
        later = str(datetime(2011, 6, 5, 23, 41, 22, 900000))
        tooLate = str(datetime(2011, 6, 5, 23, 41, 23, 400))
        matcher = DatetimeMatcher().asString().withinOneSecondOf(reference)
        self.assertFalse(matcher.matches(tooEarly),
            str(matcher.matchFor(tooEarly)))
        self.assertFalse(matcher.matches(tooLate),
            str(matcher.matchFor(tooLate)))
        self.assertTrue(matcher.matches(earlier),
            str(matcher.matchFor(earlier)))
        self.assertTrue(matcher.matches(later),
            str(matcher.matchFor(later)))


if __name__ == '__main__':
    unittest.main()
