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

import re
import itertools

from tek.user_input import UserInput, SpecifiedChoice
from tek.tools import (filter_index, sizeof_fmt, maxlen, join_lists,
                       resolve_redirect)
from tek import ConfigClient, Configurations, logger

from tek_utils.sharehoster.common import Downloader
from tek_utils.sharehoster.rapidshare import RapidshareDownloader
from tek_utils.sharehoster.netload import NetloadDownloader
from tek_utils.sharehoster.uploaded import UploadedDownloader
from tek_utils.sharehoster.zevera import ZeveraDownloader
from tek_utils.sharehoster.errors import InvalidURLError
import tek_utils.sharehoster.config

providers = dict(rapidshare=['com', RapidshareDownloader],
                 netload=['in', NetloadDownloader],
                 uploaded=['to', UploadedDownloader])
proxy_providers = dict(zevera=ZeveraDownloader)
_domain_matcher = re.compile(r'https?://(?:www\.)?([^/]+)\.[^/]+')


def accepted_domains():
    _providers = ConfigClient('search')('providers')
    proxy_domains = [ConfigClient(provider)('providers') for provider in
                     proxy_providers]
    return set(_providers + join_lists(proxy_domains))


class DownloaderFactory(object):

    def download_via_proxy(url, domain, *a, **kw):
        for provider, downloader in proxy_providers.items():
            domains = ConfigClient(provider)('providers')
            if domain in domains:
                return downloader(url, *a, **kw)
        raise InvalidURLError(url, 'No matching provider')

    def __call__(self, url, *a, **kw):
        url = resolve_redirect(url)
        _providers = ConfigClient('search')('providers')
        domain = _domain_matcher.match(url)
        if not domain:
            raise InvalidURLError(url, 'Couldn\'t parse URL')
        domain = domain.group(1)
        if not domain in _providers:
            return self.download_via_proxy(url, domain, *a, **kw)
        else:
            return providers[domain][1](url, *a, **kw)

def downloader(*a, **kw):
    return DownloaderFactory()(*a, **kw)


class DownloadChoice(object):

    def __init__(self, downloads):
        self._create_downloaders(downloads)
        self._init_choice()

    def _create_downloaders(self, downloads):
        def create_if(d):
            return (d if isinstance(d, Downloader) else
                    downloader(d))
        self._downloaders = map(create_if, downloads)

    def _init_choice(self):
        urls = [d.url for d in self._downloaders]
        sizes = [d.file_size_str for d in self._downloaders]
        format = '{u: <{ua}} | {s: >{sa}}'
        max_url = maxlen(*urls)
        max_size = maxlen(*sizes)
        lines = [format.format(u=u, s=s, ua=max_url, sa=max_size) for u, s in
                 itertools.izip(urls, sizes)]
        total_size = sum([d.file_size for d in self._downloaders])
        text = ['Total: {}'.format(sizeof_fmt(total_size)),
                'Download [a]ll, [m]ultiple, [n]one, a single file or [q]uit?']
        self._choice = SpecifiedChoice(lines, simple=['a', 'n', 'm', 'q'],
                                       enter='a', text_post=text,
                                       values=self._downloaders)

    def run(self):
        val = self._choice.read()
        if val == 'a':
            self._download(self._downloaders)
        elif val == 'm':
            return self._download_multi()
        elif val == 'n':
            return False
        elif val == 'q':
            return True
        else:
            self._download([val])
        return True

    def _download_multi(self):
        numbers = map(unicode, xrange(1, len(self._downloaders)+1))
        single = '|'.join(numbers)
        regex = re.compile(r'^(({0}) )*({0})$'.format(single))
        input = UserInput(['Enter link numbers:'], validator=regex)
        choice = [int(i)-1 for i in input.read().split()]
        self._download(filter_index(self._downloaders, choice))

    def _download(self, urls):
        for url in urls:
            url.retrieve()

def downloader_cli():
    Configurations.parse_cli(positional=('urls', '+'))
    urls = ConfigClient('shget')('urls')
    for url in urls:
        try:
            downloader(url).retrieve()
        except InvalidURLError as e:
            logger.error(e)

__all__ = ['providers', 'DownloadChoice', 'DownloaderFactory']
