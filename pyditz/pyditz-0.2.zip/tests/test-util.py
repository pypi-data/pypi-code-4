"""
Test utility functions.
"""

from ditz import util


def test_utils():
    "Test utility functions"

    for num in 0.43, 1, 23, 64, 432, 3656, 1539424, 41749360, 97492847:
        print num, '=', util.ago(num)

    print
    print util.extract_username('Alan Partridge <alan@norwichradio.co.uk>')

    print
    names = "fred brian derek tarquin ermintrude cyril"
    util.print_columns(names.split(), linelen=45)

    print
    print util.default_name()
    print util.default_email()


if __name__ == "__main__":
    test_utils()
