import unittest

from ukpostcodeparser import parse_uk_postcode

test_data = [
    ('cr0 2yr', False, False, ('CR0', '2YR')),
    ('CR0 2YR', False, False, ('CR0', '2YR')),
    ('cr02yr', False, False, ('CR0', '2YR')),
    ('dn16 9aa', False, False, ('DN16', '9AA')),
    ('dn169aa', False, False, ('DN16', '9AA')),
    ('ec1a 1hq', False, False, ('EC1A', '1HQ')),
    ('ec1a1hq', False, False, ('EC1A', '1HQ')),
    ('m2 5bq', False, False, ('M2', '5BQ')),
    ('m25bq', False, False, ('M2', '5BQ')),
    ('m34 4ab', False, False, ('M34', '4AB')),
    ('m344ab', False, False, ('M34', '4AB')),
    ('sw19 2et', False, False, ('SW19', '2ET')),
    ('sw192et', False, False, ('SW19', '2ET')),
    ('w1a 4zz', False, False, ('W1A', '4ZZ')),
    ('w1a4zz', False, False, ('W1A', '4ZZ')),
    ('cr0', False, False, ('CR0', '')),
    ('sw19', False, False, ('SW19', '')),
    ('xx0 2yr', False, False, ('XX0', '2YR')),
    ('3r0 2yr', False, False, ('3R0', '2YR')),
    ('20 2yr', False, False, ('20', '2YR')),
    ('3r0 ayr', False, False, ('3R0', 'AYR')),
    ('3r0 22r', False, False, ('3R0', '22R')),
    ('w1m 4zz', False, False, ('W1M', '4ZZ')),
    ('3r0', False, False, ('3R0', '')),
    ('ec1c 1hq', False, False, ('EC1C', '1HQ')),
    ('m344cb', False, False, ('M34', '4CB')),
    ('gir 0aa', False, False, ('GIR', '0AA')),
    ('gir', False, False, ('GIR', '')),
    ('w1m 4zz', False, False, ('W1M', '4ZZ')),
    ('w1m', False, False, ('W1M', '')),
    ('dn169aaA', False, False, 'ValueError'),

    ('cr0 2yr', False, True, ('CR0', '2YR')),
    ('CR0 2YR', False, True, ('CR0', '2YR')),
    ('cr02yr', False, True, ('CR0', '2YR')),
    ('dn16 9aa', False, True, ('DN16', '9AA')),
    ('dn169aa', False, True, ('DN16', '9AA')),
    ('ec1a 1hq', False, True, ('EC1A', '1HQ')),
    ('ec1a1hq', False, True, ('EC1A', '1HQ')),
    ('m2 5bq', False, True, ('M2', '5BQ')),
    ('m25bq', False, True, ('M2', '5BQ')),
    ('m34 4ab', False, True, ('M34', '4AB')),
    ('m344ab', False, True, ('M34', '4AB')),
    ('sw19 2et', False, True, ('SW19', '2ET')),
    ('sw192et', False, True, ('SW19', '2ET')),
    ('w1a 4zz', False, True, ('W1A', '4ZZ')),
    ('w1a4zz', False, True, ('W1A', '4ZZ')),
    ('cr0', False, True, 'ValueError'),
    ('sw19', False, True, 'ValueError'),
    ('xx0 2yr', False, True, ('XX0', '2YR')),
    ('3r0 2yr', False, True, ('3R0', '2YR')),
    ('20 2yr', False, True, ('20', '2YR')),
    ('3r0 ayr', False, True, ('3R0', 'AYR')),
    ('3r0 22r', False, True, ('3R0', '22R')),
    ('w1m 4zz', False, True, ('W1M', '4ZZ')),
    ('3r0', False, True, 'ValueError'),
    ('ec1c 1hq', False, True, ('EC1C', '1HQ')),
    ('m344cb', False, True, ('M34', '4CB')),
    ('gir 0aa', False, True, ('GIR', '0AA')),
    ('gir', False, True, 'ValueError'),
    ('w1m 4zz', False, True, ('W1M', '4ZZ')),
    ('w1m', False, True, 'ValueError'),
    ('dn169aaA', False, True, 'ValueError'),

    ('cr0 2yr', True, False, ('CR0', '2YR')),
    ('CR0 2YR', True, False, ('CR0', '2YR')),
    ('cr02yr', True, False, ('CR0', '2YR')),
    ('dn16 9aa', True, False, ('DN16', '9AA')),
    ('dn169aa', True, False, ('DN16', '9AA')),
    ('ec1a 1hq', True, False, ('EC1A', '1HQ')),
    ('ec1a1hq', True, False, ('EC1A', '1HQ')),
    ('m2 5bq', True, False, ('M2', '5BQ')),
    ('m25bq', True, False, ('M2', '5BQ')),
    ('m34 4ab', True, False, ('M34', '4AB')),
    ('m344ab', True, False, ('M34', '4AB')),
    ('sw19 2et', True, False, ('SW19', '2ET')),
    ('sw192et', True, False, ('SW19', '2ET')),
    ('w1a 4zz', True, False, ('W1A', '4ZZ')),
    ('w1a4zz', True, False, ('W1A', '4ZZ')),
    ('cr0', True, False, ('CR0', '')),
    ('sw19', True, False, ('SW19', '')),
    ('xx0 2yr', True, False, 'ValueError'),
    ('3r0 2yr', True, False, 'ValueError'),
    ('20 2yr', True, False, 'ValueError'),
    ('3r0 ayr', True, False, 'ValueError'),
    ('3r0 22r', True, False, 'ValueError'),
    ('w1m 4zz', True, False, 'ValueError'),
    ('3r0', True, False, 'ValueError'),
    ('ec1c 1hq', True, False, 'ValueError'),
    ('m344cb', True, False, 'ValueError'),
    ('gir 0aa', True, False, ('GIR', '0AA')),
    ('gir', True, False, ('GIR', '')),
    ('w1m 4zz', True, False, 'ValueError'),
    ('w1m', True, False, 'ValueError'),
    ('dn169aaA', True, False, 'ValueError'),

    ('cr0 2yr', True, True, ('CR0', '2YR')),
    ('CR0 2YR', True, True, ('CR0', '2YR')),
    ('cr02yr', True, True, ('CR0', '2YR')),
    ('dn16 9aa', True, True, ('DN16', '9AA')),
    ('dn169aa', True, True, ('DN16', '9AA')),
    ('ec1a 1hq', True, True, ('EC1A', '1HQ')),
    ('ec1a1hq', True, True, ('EC1A', '1HQ')),
    ('m2 5bq', True, True, ('M2', '5BQ')),
    ('m25bq', True, True, ('M2', '5BQ')),
    ('m34 4ab', True, True, ('M34', '4AB')),
    ('m344ab', True, True, ('M34', '4AB')),
    ('sw19 2et', True, True, ('SW19', '2ET')),
    ('sw192et', True, True, ('SW19', '2ET')),
    ('w1a 4zz', True, True, ('W1A', '4ZZ')),
    ('w1a4zz', True, True, ('W1A', '4ZZ')),
    ('cr0', True, True, 'ValueError'),
    ('sw19', True, True, 'ValueError'),
    ('xx0 2yr', True, True, 'ValueError'),
    ('3r0 2yr', True, True, 'ValueError'),
    ('20 2yr', True, True, 'ValueError'),
    ('3r0 ayr', True, True, 'ValueError'),
    ('3r0 22r', True, True, 'ValueError'),
    ('w1m 4zz', True, True, 'ValueError'),
    ('3r0', True, True, 'ValueError'),
    ('ec1c 1hq', True, True, 'ValueError'),
    ('m344cb', True, True, 'ValueError'),
    ('gir 0aa', True, True, ('GIR', '0AA')),
    ('gir', True, True, 'ValueError'),
    ('w1m 4zz', True, True, 'ValueError'),
    ('w1m', True, True, 'ValueError'),
    ('dn169aaA', True, True, 'ValueError'),
]


class TestParser(unittest.TestCase):

    def test_all(self):
        for postcode, strict, incode_mandatory, required_result in test_data:
            try:
                actual_result = parse_uk_postcode(postcode, strict,
                                                  incode_mandatory)
            except ValueError:
                actual_result = 'ValueError'
            self.assertEqual(actual_result, required_result)
