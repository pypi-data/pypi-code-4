#!/usr/bin/python
# test -- implements a test command for distutils.core.setup
# Copyright (c) 2011 Sean Robinson <seankrobinson@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import distutils.core
import unittest

class test(distutils.core.Command):
    """ Run unit tests.

        This command loads tests using the unittest module's test
        discovery abilities (see the unittest documentation regarding
        "Test Discovery").

        Then the tests are run using unittest.TextTestRunner() with a
        default verbosity of 2, or a verbosity of 0 if the --quiet
        option is passed to the command.

        This command should work with Python >= 2.7 out of the box.  It
        may work in Python 2.4-2.6 with unittest2.
    """
    description = "Run unit tests."

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('start-dir=', 's',
                     "Directory to start discovery ('.' default)"),
                    ('pattern=', 'p',
                     "Pattern to match test files ('test*.py' default)"),
                    ('top-level-dir=', 't',
                     "Top level directory of project (defaults to start directory)"),
                   ]

    boolean_options = ['verbose']

    def initialize_options(self):
        """ Set the default values for command options.
        """
        self.verbosity = 2
        self.start_dir = '.'
        self.pattern = 'test*.py'
        self.top_level_dir = None

    def finalize_options(self):
        """ Ensure options are ready to be used during test set-up.
        """
        if not self.verbose:
            self.verbosity = 0

    def run(self):
        """ Run the test suites returned by unittest.TestLoader.discover.
        """
        discover = unittest.defaultTestLoader.discover
        for suite in discover(self.start_dir, self.pattern, self.top_level_dir):
            unittest.TextTestRunner(verbosity=self.verbosity).run(suite)

