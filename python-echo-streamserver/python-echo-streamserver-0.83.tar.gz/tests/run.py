#! /usr/bin/python
#
# Unit Testing Package: Run Tests
#
import sys, os
try:
    import unittest2 as unittest
except ImportError:
    import unittest

def main(stream=sys.stderr, discovery_pattern='test*.py'):
    # TEST_PATH: Path to package containing test modules
    TEST_PATH = os.path.dirname(__file__)

    print TEST_PATH
    # Discover Unit Tests:
    suite = unittest.loader.TestLoader().discover(TEST_PATH, pattern=discovery_pattern)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)

if __name__ == '__main__':
    # Use alternate discovery pattern.
    # NOTE: SHELL will GLOB first, w/o quotes, e.g. "test_group*.py"
    try:
        # Pass discovery_pattern glob string for *.py files.
        pattern=sys.argv[1]
        main(discovery_pattern=pattern)
    except IndexError:
        main()

