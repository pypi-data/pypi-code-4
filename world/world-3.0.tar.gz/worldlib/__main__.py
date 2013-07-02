# Copyright (C) 2013 by Barry A. Warsaw
#
# This file is part of world
#
# world is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, version 3 of the License.
#
# world is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# world.  If not, see <http://www.gnu.org/licenses/>.

"""world script main entry point."""

__all__ = [
    'main',
    ]


import argparse

from worldlib import __version__
from worldlib.refresh import refresh
from worldlib.database import Database, gTLDs


XMLFILE = ('http://www.iso.org/iso/home/standards/country_codes/'
           'country_names_and_code_elements_xml.htm')


def main():
    parser = argparse.ArgumentParser(
        prog='world',
        description='Top level domain name mapper.')
    parser.add_argument('--version',
                        action='version',
                        version='world {}'.format(__version__))
    group_1 = parser.add_argument_group(
        'Regeneration',
        'Use these options to rebuild the cached TLD mappings.')
    group_1.add_argument('--refresh', action='store_true',
                         help='Refresh the ccTLD database from XML file.')
    group_1.add_argument('--source', default=None,
                         help="""\
URL of the source XML file.  By default the file comes from www.iso.org.  This
option is only useful when --refresh is given.""")
    group_1.add_argument('--cache', default=None,
                         help="""\
Where is the processed database stored?  By default, this is within the source
tree for updating the package.""")
    group_2 = parser.add_argument_group('Querying')
    group_2.add_argument('-r', '--reverse', action='store_true',
                         help="""\
Do a reverse lookup.  In this mode, the arguments can be any Python regular
expression; these are matched against all TLD descriptions (e.g. country
names) and a list of matches is printed.
""")
    group_2.add_argument('-a', '--all', action='store_true',
                         help='Print the mapping of all top-level domains.')
    parser.add_argument('domain', nargs='*')
    args = parser.parse_args()
    # Additional sanity checks.
    if (args.source or args.cache) and not args.refresh:
        parser.error('--source/--cache require --refresh')
    if (args.all or len(args.domain) > 0) and args.refresh:
        parser.error('--refresh cannot be used when querying/printing')
    if args.all and (args.reverse or len(args.domain) > 0):
        parser.error('--all cannot be used when querying')
    # Get the mappings.
    if args.refresh:
        refresh(XMLFILE if args.source is None else args.source, args.cache)
        return
    # Lookup.
    db = Database(args.cache)
    if args.all:
        print('Country code top level domains:')
        for cc in sorted(db.ccTLDs):
            print('    {}: {}'.format(cc, db.ccTLDs[cc]))
        print()
        print('Additional top level domains:')
        for tld in sorted(gTLDs):
            print('    {:6}: {}'.format(tld, gTLDs[tld]))
        return
    newline = False
    for domain in args.domain:
        if args.reverse:
            if newline:
                print()
            matches = db.find_matches(domain)
            if len(matches) > 0:
                print('Matches for "{}":'.format(
                    domain, len(matches)))
                for code, country in matches:
                    print('  {}: {}'.format(code, country))
                newline = True
                continue
        else:
            country = db.lookup_code(domain)
            if country is not None:
                print('{} originates from {}'.format(domain, country))
                continue
        print('Where in the world is {}?'.format(domain))


if __name__ == '__main__':
    main()
