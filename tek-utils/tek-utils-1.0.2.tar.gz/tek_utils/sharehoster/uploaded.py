__copyright__ = """ Copyright (c) 2012-2013 Torsten Schmits

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

import os
import re

import requests

from tek.config import lazy_configurable

from tek_utils.sharehoster.common import Downloader

@lazy_configurable(uploaded=['cookies'])
class UploadedDownloader(Downloader):

    def _setup_request(self, url):
        self.url = url
        self._setup_params()
        self._reset_request()

    def _setup_params(self):
        def trim(filename):
            return re.sub('\.html?$', '', filename)
        def split(url):
            return url.rsplit('/')[-2:]
        fileid, filename = split(self.url)
        self.file_path = os.path.join(self._download_dir, trim(filename))

    def _reset_request(self):
        self._request = requests.get(self.url, cookies=self._cookies,
                                     stream=True)

__all__ = ['UploadedDownloader']
