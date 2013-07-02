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

"""The database and lookups."""

__all__ = [
    'Database',
    'gTLDs',
    ]


import re
import pickle

from pkg_resources import resource_filename


class Database:
    def __init__(self, cache=None):
        if cache is None:
            cache = resource_filename('worldlib.data', 'codes.pck')
        with open(cache, 'rb') as fp:
            self.ccTLDs = pickle.load(fp)
        # Some additional common mappings.
        self._by_code = self.ccTLDs.copy()
        self._by_code.update(gTLDs)

    def lookup_code(self, domain):
        return self._by_code.get(domain.lower())

    def find_matches(self, text):
        matches = []
        cre = re.compile(text, re.IGNORECASE)
        for key, value in self._by_code.items():
            if cre.search(value):
                matches.append((key, value))
        return sorted(matches)

    def __iter__(self):
        for code in sorted(self._by_code):
            yield code


# Generic top-level domains.
# http://en.wikipedia.org/wiki/GTLD
gTLDs = {
    # Intrastructure.
    'arpa': 'Arpanet',
    # Additional IANA TLDs.
    'aero': 'air-transport industry',
    'asia': 'Asia-Pacific region',
    'biz' : 'business',
    'cat' : 'Catalan',
    'com' : 'commercial',
    'coop': 'cooperatives',
    'info': 'information',
    'int' : 'international organizations',
    'jobs': 'companies',
    'mobi': 'mobile devices',
    'museum': 'museums',
    'name': 'individuals, by name',
    'net' : 'network',
    'org' : 'non-commercial',
    'post': 'postal services',
    'pro' : 'professionals',
    'tel' : 'Internet communications services',
    'travel': 'travel and tourism industry related sites',
    'xxx' : 'adult entertainment',
    # USA TLDs.
    'edu' : 'educational',
    'gov' : 'governmental',
    'mil' : 'US military',
    # These additional ccTLDs are included here even though they are not part
    # of ISO 3166.  IANA has 5 reserved ccTLDs as described here:
    #
    # http://www.iso.org/iso/en/prods-services/iso3166ma/04background-on-iso-3166/iso3166-1-and-ccTLDs.html
    #
    # but I can't find an official list anywhere.
    #
    # Note that `uk' is the common practice country code for the United
    # Kingdom.  AFAICT, the official `gb' code is routinely ignored!
    #
    # <D.M.Pick@qmw.ac.uk> tells me that `uk' was long in use before ISO3166
    # was adopted for top-level DNS zone names (although in the reverse order
    # like uk.ac.qmw) and was carried forward (with the reversal) to avoid a
    # large-scale renaming process as the UK switched from their old `Coloured
    # Book' protocols over X.25 to Internet protocols over IP.
    #
    # See <url:ftp://ftp.ripe.net/ripe/docs/ripe-159.txt>
    'ac': 'Ascension Island',
    'eu': 'European Union',
    'su': 'Soviet Union (historical)',
    'tp': 'East Timor (obsolete)',
    'uk': 'United Kingdom (common practice)',
    }
