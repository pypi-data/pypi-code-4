# -*- coding: utf-8 -*-

__doc__ = '''

    `importer`:

    a handy package to transfer data
    between mixpanel.com and keen.io.

    run `make`, configure via `config.json`,
    and then run this utility to transfer
    data.

    command line flags override entries in
    `config.json`.

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

__version__ = (1, 1)
__author__ = "Sam Gammon <sam@keen.io"


# stdlib
import os
import sys
import logging
import argparse

# importer
import mix
from mix import Importer

# logging
logging.basicConfig(format=Importer.log_format)

# dependencies
try:
    import keen
    import mixpanel  # try to grab libs globally

except ImportError:  # pragma: nocover

    # calculate absolute path to `importer` and patch sys.path
    if 'lib/' not in sys.path:
        [sys.path.insert(0, os.path.join(os.path.dirname(__file__), path))
            for path in ('lib/', 'lib/dist', 'lib/keen', 'lib/mixpanel')]

    try:
        import keen, mixpanel  # try to grab libs locally

    except ImportError:  # pragma: nocover

        try:  # try to grab them manually from `lib`
            if 'keen' not in globals():
                from lib import keen
            if 'mixpanel' not in globals():
                from lib.mixpanel import mixpanel

        except ImportError:
            # no dependencies: can't go on
            logging.critical('Dependencies `keen` and `mixpanel` are missing. '
                             'Please run `make` or `pip install keen mixpanel`.')

            sys.exit(1)  # exit with error


# provider choice names
_provider_choices = frozenset(map(lambda x: x.lower(), mix.PROVIDERS.iterkeys()))


## == Command line parser
parser = argparse.ArgumentParser(description=__doc__)

## == Command line flags

# begin date
parser.add_argument('begin', metavar='BEGIN', type=unicode,
                    help='start of event range to fetch (YYYY-MM-DD)')

# end date
parser.add_argument('end', metavar='END', type=unicode,
                    help='end of event range to fetch (YYYY-MM-DD)')

# config file
parser.add_argument('--config', '-c', dest='config_file', type=unicode,
                    help='config.json file with keys and settings', required=False)

# source provider
parser.add_argument('--from', '-f', dest='source', type=unicode,
                    help='provider name to get events from', choices=_provider_choices, required=False)

# destination provider
parser.add_argument('--to', '-t', dest='target', type=unicode,
                    help='provider name to send events to', choices=_provider_choices, required=False)

# event kinds
parser.add_argument('--kind', '-k', dest='kind', type=unicode, nargs='+',
                    help='event types to provide (multiple can be specified)', required=False)

# option: reset timestamps
parser.add_argument('--reset_timestamps', '-r', dest='reset_ts', action='store_true',
                    help='reset event timestamps upon upload')

# option: say `yes` to all prompts
parser.add_argument('--yes', '-y', action='store_true',
                    help='assume "yes" to all prompts')

# option: quieter output
parser.add_argument('--quiet', '-q', action='store_true',
                    help='be quiet about everything')

# option: louder output
parser.add_argument('--verbose', '-v', action='count', dest='verbose', default=0,
                    help='be loud about everything')

# option: print version and exit
parser.add_argument('--version', '-V', action='version',
                    help='print importer\'s version and exit', version='importer %s' % '.'.join(map(unicode, __version__)))


## == Importer! :)
run = lambda: sys.exit(Importer(keen=keen, mixpanel=mixpanel)(**vars(parser.parse_args())))


if __name__ == '__main__':  # pragma: nocover
    run()
