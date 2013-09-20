__copyright__ = """ Copyright (c) 2011-2013 Torsten Schmits

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

import unittest

from tek.config import Configurations

from tek_utils.sharehoster.search import SiteValidator
# from tek_utils.sharehoster import DownloadChoice, downloader
from tek_utils.sharehoster.zevera import ZeveraDownloader

class SharehosterTest(unittest.TestCase):

    def test_match(self):
        Configurations.enable_lazy_class_attr = False
        Configurations.override('search', match_url='how,i.met,s05e16')
        self.assertTrue(SiteValidator().match_link('How I met s05E16'))
        Configurations.override('search', match_url='howw,i.met,s05e16')
        self.assertFalse(SiteValidator().match_link('How I met s05E16'))

    def test_zevera(self):
        url = ('http://rapidgator.net/file/a485f588eff808f4369f24da00cd6678/'
               'ddlsource.com_Futurama.S07E17.HDTV.x264-ASAP.mp4.html')
        down = ZeveraDownloader(url)
        down.retrieve()

if __name__ == '__main__':
    unittest.main()
