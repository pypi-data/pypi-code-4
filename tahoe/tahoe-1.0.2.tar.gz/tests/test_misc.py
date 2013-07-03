import datetime

from tahoe.misc import cleanup_dict
from tahoe.misc import normalize_email_address
from tahoe.misc import url_is_ok
from tahoe.misc import get_timestamp

from tahoe.tests import TahoeTestCase


class TestMiscellaneous(TahoeTestCase):
    def test_normalize_email_address_non_gmail_with_plus(self):
        """
        Can normalize a non-Gmail address containing a plus symbol.
        """
        email_address = 'clintecker+somethingelse@example.com'
        norm_email_address = normalize_email_address(email_address)
        assert norm_email_address != email_address
        assert '+' not in norm_email_address
        assert norm_email_address == 'clintecker@example.com'

    def test_normalize_email_address_non_gmail_with_dots(self):
        """
        Can normalize a non-Gmail address containing dot symbols.
        """
        email_address = 'clint.ecker@example.com'
        norm_email_address = normalize_email_address(email_address)
        assert norm_email_address == email_address

    def test_normalize_email_address_non_gmail_with_dots_and_plus(self):
        """
        Can normalize a non-Gmail address containing both dot and plus symbols.
        """
        email_address = 'clint.ecker+something@example.com'
        norm_email_address = normalize_email_address(email_address)
        assert norm_email_address != email_address
        assert '+' not in norm_email_address
        assert norm_email_address == 'clint.ecker@example.com'

    def test_normalize_email_address_gmail_without_dots(self):
        """
        Can normalize a Gmail address not containing dot symbols.
        """
        email_address = 'clint@gmail.com'
        norm_email_address = normalize_email_address(email_address)
        assert norm_email_address == email_address

    def test_normalize_email_address_gmail_with_dots(self):
        """
        Can normalize a Gmail address containing dot symbols.
        """
        email_address = 'clint.ecker@gmail.com'
        norm_email_address = normalize_email_address(email_address)
        assert norm_email_address != email_address
        assert norm_email_address == 'clintecker@gmail.com'

    def test_normalize_email_address_gmail_with_dots_and_plus(self):
        """
        Can normalize a Gmail address containing both dot and plus symbols.
        """
        email_address = 'clint.ecker+something@gmail.com'
        norm_email_address = normalize_email_address(email_address)
        assert norm_email_address != email_address
        assert '+' not in norm_email_address
        assert norm_email_address == 'clintecker@gmail.com'

    def test_normalize_email_address_gmail_without_dots_and_plus(self):
        """
        Can normalize a Gmail address containing plus symbols.
        """
        email_address = 'clintecker+something@gmail.com'
        norm_email_address = normalize_email_address(email_address)
        assert norm_email_address != email_address
        assert '+' not in norm_email_address
        assert norm_email_address == 'clintecker@gmail.com'

    def test_url_is_ok(self):
        """
        Can validate that a URL points to a page on a given domain.
        """
        valid_domain = 'example.com'
        suspect_url = 'http://{}/something/12345?do_it=true#cool'.format(valid_domain)
        assert url_is_ok(suspect_url, valid_domain)

    def test_url_is_ok_subdomain(self):
        """
        Considers a URL containing a sub-domain of the given domain to be invalid.
        """
        valid_domain = 'example.com'
        suspect_url = 'http://www.{}/something/12345?do_it=true#cool'.format(valid_domain)
        assert not url_is_ok(suspect_url, valid_domain)

    def test_url_is_ok_no_domain_given(self):
        """
        Considers any URL as valid when no domain is given.
        """
        valid_domain = 'example.com'
        suspect_url = 'http://www.{}/something/12345?do_it=true#cool'.format(valid_domain)
        assert url_is_ok(suspect_url)

    def test_url_is_ok_relative(self):
        """
        Considers any relative URL as valid, regardless of the given domain.
        """
        valid_domain = 'example.com'
        suspect_url = '/something/12345?do_it=true#cool'
        assert url_is_ok(suspect_url, valid_domain)

    def test_url_is_ok_relative_no_domain_given(self):
        """
        Considers any relative URL as valid even if no domain is given.
        """
        suspect_url = '/something/12345?do_it=true#cool'
        assert url_is_ok(suspect_url)

    def test_cleanup_dict(self):
        """
        Cleanup dict works
        """
        d = dict(
            one=1,
            two=2,
            three=3)
        initial_keys = set(d.keys())
        keys_to_remove = ['three', 'one']
        keys_to_preserve = initial_keys.difference(set(keys_to_remove))
        cleanup_dict(d, keys_to_remove)
        for key in keys_to_remove:
            assert key not in d
        for key in keys_to_preserve:
            assert key in d

    def test_cleanup_dict_with_nonexistent_keys(self):
        """
        Cleanup dict works even when you present it with keys that don't exist
        """
        d = dict(
            one=1,
            two=2,
            three=3)
        initial_keys = set(d.keys())
        keys_to_remove = ['three', 'one', 'four']
        keys_to_preserve = initial_keys.difference(set(keys_to_remove))
        cleanup_dict(d, keys_to_remove)
        for key in keys_to_remove:
            assert key not in d
        for key in keys_to_preserve:
            assert key in d

    def test_get_timestamp(self):
        """
        Can get a timestamp of right now
        """
        before = get_timestamp(round=False)
        now = get_timestamp(round=False)
        after = get_timestamp(round=False)
        assert before < now < after

    def test_get_timestamp_of_exact_datetime(self):
        """
        Can get a timestamp of a specific datetime
        """
        dt1 = datetime.datetime(1970, 1, 1, 0, 0, 0)
        ts1 = get_timestamp(now=dt1)

        dt2 = datetime.datetime(2014, 5, 13, 16, 53, 20)
        ts2 = get_timestamp(now=dt2)

        dt3 = datetime.datetime(2038, 1, 19, 3, 14, 8)
        ts3 = get_timestamp(dt3)

        assert ts1 == 0
        assert ts2 == 1400000000
        assert ts3 == 2**31
