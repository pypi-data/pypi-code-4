# -*- coding: utf-8 -*-

'''

    importer: timezone tests
    ~~~~~~~~~~~~~~~~~~~~~~~~

    this module tests functionality in ``importer``
    related to timezone and time offset computation.

    :author: Sam Gammon <sam@keen.io>
    :license: This software follows the MIT (OSI-approved)
              license for open source software. A truncated
              version is included here; for full licensing
              details, see ``LICENSE.md`` in the root directory
              of the project.

              Copyright (c) 2013, Keen IO

              The above copyright notice and this permission notice shall be included in
              all copies or substantial portions of the Software.

              THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
              IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
              FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
              AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
              LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
              OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
              THE SOFTWARE.

'''


# stdlib
import time
import unittest
import datetime

# importer
from importer import tz
from importer import mix


## TZTests - puts offset calculation functions through their paces.
class TZTests(unittest.TestCase):

    ''' Tests routines related to calculating
        timezone/DST offsets. '''

    def test_exports(self):

        ''' Make sure that all expected module globals are exported
            where they should be. '''

        self.assertTrue(hasattr(tz, 'timezone'))  # test that proxy exists to :py:mod:`pytz`
