# -*- coding: utf-8 -*-

'''
    importer: timezones
    ~~~~~~~~~~~~~~~~~~~

    this package provides utilities and predefined
    dictionaries for dealing with timezones and
    time offsets.

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

# stdlib
import logging

# pytz
try:
    from pytz import timezone

except ImportError as e:  # pragma: nocover
    logging.critical('Failed to load `pytz`, which `Importer` depends on. Exiting.')
    exit(1)


# `_TIMEZONE_DATA`: compound data dictionary of timezone names, offsets, DST's, and keys
_TIMEZONE_DATA = (
    (-12, 'BIT', 'Baker Island Time', 'Pacific/Baker'),
    (-11.5, 'NUT', 'Niue Time', 'Pacific/Niue'),
    (-11, 'SST', 'Samoa Standard Time', 'Pacific/Samoa'),
    (-10, 'CKT', 'Cook Island Time', 'Pacific/Cook_Islands'),
    (-9.5, 'MART', 'Marquesas Islands Time', 'Pacific/Marquesas'),
    (-9, 'AKST', 'Alaska Standard Time', 'US/Alaska'),
    (-8, 'PST', 'Pacific Standard Time', 'US/Pacific'),
    (-7, 'MST', 'Mountain Standard Time', 'US/Mountain'),
    (-6, 'CST', 'Central Standard Time', 'US/Central'),
    (-5, 'EST', 'Eastern Standard Time', 'US/Eastern'),
    (-4.5, 'VET', 'Venezuelan Standard Time', 'Americas/Venezuela'),
    (-4, 'AST', 'Atlantic Standard Time', 'Americas/Atlantic'),
    (-3.5, 'NST', 'Newfoundland Standard Time', 'Americas/Newfoundland'),
    (-3, 'ADT', 'Atlantic Daylight Time', 'Americas/Atlantic/DST'),
    (-2.5, 'NDT', 'Newfoundland Daylight Time', 'Americas/Newfoundland/DST'),
    (-2, 'FNT', 'Fernando de Noronha Time', 'European/Spain'),
    (-1, 'EGT', 'East Greenland Time', 'European/East_Greenland'),
    (0, 'UTC', 'UTC', 'UTC'),
    (1, 'CET', 'Central European Time', 'European/Central'),
    (2, 'CAT', 'Central Africa Time', 'Africa/Central'),
    (3, 'AST', 'Arabia Standard Time', 'MiddleEast/Arabia_Standard'),
    (3.5, 'IRST', 'Iran Standard Time', 'MiddleEast/Iran'),
    (4, 'AZT', 'Azerbaijan Time', 'MiddleEast/Azerbaijan'),
    (4.5, 'AFT', 'Afghanistan Time', 'MiddleEast/Afghanistan'),
    (5, 'MVT', 'Maldives Time', 'Asia/Maldives'),
    (5.5, 'IST', 'Indian Standard Time', 'Asia/India_Standard'),
    (6, 'BST', 'Bangladesh Standard Time', 'Asia/Bangladesh'),
    (6.5, 'CCT', 'Cocos Islands Time', 'Oceania/Cocos'),
    (7, 'CXT', 'Christmas Island Time', 'Oceania/Christmas_Island'),
    (8, 'ACT', 'ASEAN Common Time', 'Asia/Common'),
    (9, 'JST', 'Japan Standard Time', 'Asia/Japan'),
    (9.5, 'ACST', 'Australian Central Standard Time', 'Australia/Central'),
    (10, 'AEST', 'Australian Eastern Standard Time', 'Australia/Eastern'),
    (10.5, 'ACDT', 'Australian Central Daylight Time', 'Australia/Central/DST'),
    (11, 'AEDT', 'Australian Eastern Daylight Time', 'Australia/Eastern/DST'),
    (11.5, 'NFT', 'Norfolk Time', 'Oceania/Norfolk'),
    (12, 'FJT', 'Fiji Time', 'Oceania/Fiji')
)


# `_TZNAMES`: mapping from long (config) names to offsets
_TZNAMES = dict(((name, offset) for offset, shortcode, longname, name in _TIMEZONE_DATA))


# `_TZSHORT`: mapping from timezone offsets to shortcodes
_TZSHORT = dict(((offset, shortcode) for offset, shortcode, longname, name in _TIMEZONE_DATA))


# `_TIMEZONES`: map TZ offsets to full data
_TIMEZONES = dict(((offset, (shortcode, longname, name)) for offset, shortcode, longname, name in _TIMEZONE_DATA))
