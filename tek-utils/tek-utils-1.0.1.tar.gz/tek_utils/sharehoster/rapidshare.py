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

import os

import requests

from tek.tools import resolve_redirect
from tek.config import lazy_configurable

from tek_utils.sharehoster.common import Downloader
from tek_utils.sharehoster.errors import RapidshareError, IllegalFile

@lazy_configurable(rapidshare=['login', 'password'], common=['out_dir'])
class RapidshareDownloader(Downloader):
    _api_url = 'https://api.rapidshare.com/cgi-bin/rsapi.cgi'
    _server_url_templ = 'https://{}/cgi-bin/rsapi.cgi'

    def _setup_request(self, url):
        try:
            self.url = resolve_redirect(url)
        except requests.RequestException as e:
            raise RapidshareError(str(e))
        self._setup_params()
        self._resolve_server()
        self._reset_request()

    def _setup_params(self):
        def trim(filename):
            return filename[:-5] if filename.endswith('.html') else filename
        def split(url):
            return url.rsplit('/')[-4:][2:]
        fileid, filename = split(self.url)
        self._params = dict(sub='download', fileid=fileid, filename=filename,
                            login=self._login, password=self._password)
        self.file_path = os.path.join(self._download_dir, trim(filename))

    def _resolve_server(self):
        params = dict(self._params)
        params.update({'try': '1', 'withmd5hex': '0'})
        data = requests.get(self._api_url, params=params).content
        self._check_error(data)
        try:
            key, value = data.split(':')
            server, dlauth, countdown, remote_md5sum = value.split(',')
        except ValueError as e:
            raise RapidshareError('malformed rapidshare request: {}'.format(e))
        self._server_url = self._server_url_templ.format(server)

    def _check_error(self, data):
        if data.startswith('ERROR:'):
            if 'illegal' in data:
                fname = data.split('|')[3]
                raise IllegalFile(fname)
            else:
                raise RapidshareError(data)

    def _reset_request(self):
        self._request = requests.get(self._server_url, params=self._params,
                                     stream=True)

__all__ = ['RapidshareDownloader']
