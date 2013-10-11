# -*- coding: utf-8 -*-

'''

    importer: testrunner
    ~~~~~~~~~~~~~~~~~~~~

    this file collects and runs ``importer``'s testsuite.

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

# pragma: nocover

# stdlib
import os
import sys
import unittest


## Globals

_TEST_PATHS = [
    'test_tz',  # timezone-related tests
    'test_mix',  # importer-related tests (and abstract stuff)
    'test_keen',  # keen-specific adapter/provider tests
    'test_mixpanel'  # mixpanel-specific adapter/provider tests
]


## Testsuite

## `fix_path`: add local paths to sys.path
def fix_path():

    ''' Add ``.`` and ``dir/lib`` to ``sys.path``. '''

    for path in ((os.path.dirname(__file__)),
                 (os.path.dirname(os.path.dirname(__file__))),
                 (os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lib'))):

        sys.path.insert(0, path)


## `load_module` - Load a single testsuite module.
def load_module(path):

    ''' __main__ testing entrypoint for `apptools.model`. '''

    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromName(path))
    return suite


## `load` - Gather AppTools testsuites.
def load(paths=None):

    ''' __main__ entrypoint '''

    mixtests = unittest.TestSuite()

    if paths is None:
        paths = _TEST_PATHS[:]

    for path in paths:
        mixtests.addTest(load_module(path))

    return mixtests


## `run` - Run a suite of tests loaded via `load`.
def run(suite=None):

    ''' Optionally allow switching between XML or text output, if supported. '''

    fix_path()
    if suite is None:
        suite = load()

    # resolve text runner
    if hasattr(unittest, 'TestRunner'): runner = unittest.TestRunner
    else: runner = unittest.TextTestRunner

    if len(sys.argv) > 1:
        args = sys.argv[1:]  # slice off invocation

        if len(args) == 2:  # <format>, <output location>
            format, output = tuple(args)

            if format.lower().strip() == 'xml':
                try:
                    import xmlrunner
                except ImportError:
                    print "ERROR! XML testrunner (py module `xmlrunner`) could not be imported. Please run in text-only mode."
                    exit(1)
                xmlrunner.XMLTestRunner(output=output).run(suite)

            elif format.lower().strip() == 'text':
                return runner(verbosity=5, output=output).run(suite)
        else:
            return runner(verbosity=5, output=output).run(suite)  # text mode with

    return runner(verbosity=5).run(suite)
