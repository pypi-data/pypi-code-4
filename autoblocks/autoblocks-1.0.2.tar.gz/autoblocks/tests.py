import unittest


from autoblocks.templatetags.helpers import parse_token_data


class TokenParsingTest(unittest.TestCase):
    def test_handles_on_site(self):
        expected = (['foo', 'bar'], 'site', None)
        actual = parse_token_data(['foo', 'bar', 'on', 'site'])
        self.assertEqual(expected, actual)

    def test_handles_as_context_var(self):
        expected = (['foo', 'bar'], None, 'site')
        actual = parse_token_data(['foo', 'bar', 'as', 'site'])
        self.assertEqual(expected, actual)

    def test_handles_no_on_or_as(self):
        expected = (['foo', 'bar'], None, None)
        actual = parse_token_data(['foo', 'bar'])
        self.assertEqual(expected, actual)

    def test_handles_on_and_as(self):
        expected = (['foo', 'bar'], 'site', 'var')
        actual = parse_token_data(['foo', 'bar', 'on', 'site', 'as', 'var'])
        self.assertEqual(expected, actual)

        expected = (['foo', 'bar'], 'site', 'var')
        actual = parse_token_data(['foo', 'bar', 'as', 'var', 'on', 'site'])
        self.assertEqual(expected, actual)

    def test_handles_on_in_unexpected_places(self):
        expected = (['foo', 'on', 'bar', 'foobar'], None, None)
        actual = parse_token_data(['foo', 'on', 'bar', 'foobar'])
        self.assertEqual(expected, actual)

    def test_handles_as_in_unexpected_places(self):
        expected = (['foo', 'as', 'bar', 'foobar'], None, None)
        actual = parse_token_data(['foo', 'as', 'bar', 'foobar'])
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
