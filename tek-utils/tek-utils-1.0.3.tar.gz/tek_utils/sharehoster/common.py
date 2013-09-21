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
import os
import time
import threading
import datetime
import json

import requests

from tek.io.terminal import terminal
from tek.tools import sizeof_fmt, free_space_in_dir, resolve_redirect
from tek.run import SignalManager
from tek.config import lazy_configurable
from tek.errors import NotEnoughDiskSpace
from tek import logger

from tek_utils.sharehoster.errors import InvalidURLError
from tek_utils.sharehoster.models.link_status import LinkStatus
from tek_utils.sharehoster.models.array import Array

@lazy_configurable(common=['progress_update_interval'])
class ProgressPrinter(threading.Thread):
    """ Background thread that updates a line of output every time add()
    is called. The output consists of the percentage, bytes received and
    transfer rate of a running file transfer operation.
    """

    _format = '{: >7.2%} || {: >9} of {: <9} || at {: >10}/s'.format

    def __init__(self, file_size, _terminal=None):
        self._file_size = round(file_size, 2)
        self._terminal = _terminal or terminal
        self._progress = 0.
        self._percent = 0.
        self._chunk_progress = []
        self._last_rate = 0.
        self._running = False
        self._start_time = datetime.datetime.now()
        self._stop_time = datetime.datetime.now()
        threading.Thread.__init__(self)

    def run(self):
        self._init()
        while self._running:
            self._step()

    def _init(self):
        self._running = True
        self._start_time = datetime.datetime.now()

    def _step(self):
        self._print_progress()
        time.sleep(self._progress_update_interval)
        self._log_rate()

    def _print_progress(self):
        text = self._format(self._percent, sizeof_fmt(self._progress),
                            self._size_string, self._rate_string)
        self._terminal.pop()
        self._terminal.push(text)
        self._terminal.flush()

    def add(self, bytes):
        self._progress += bytes
        if self._have_size:
            self._percent = self._progress / self._file_size

    def finish(self):
        self.stop()
        self._stop_time = datetime.datetime.now()
        self._print_progress()

    def stop(self, *a, **kw):
        self._started.wait()
        self._running = False
        if self.is_alive():
            self.join()

    def _log_rate(self):
        self._chunk_progress.append(Array(datetime.datetime.now(),
                                          self._progress))

    @property
    def _rate(self):
        prog = self._chunk_progress 
        if self._percent >= 1.:
            time = (self._stop_time - self._start_time).total_seconds()
            self._last_rate = self._file_size / time
        if len(prog) > 1:
            diff = prog[-1] - prog[-2]
            rate = diff[1] / diff[0].total_seconds()
            self._last_rate = .8 * rate + .2 * self._last_rate
        return max(self._last_rate, 0.)


    @property
    def _have_size(self):
        return self._file_size > 0

    @property
    def _size_string(self):
        return sizeof_fmt(self._file_size) if self._have_size else '??'

    @property
    def _rate_string(self):
        return sizeof_fmt(self._rate, prec=2) if self._have_size else '??'

class Progress(object):
    def __init__(self, url, path, file_size):
        self._url = url
        self._path = path
        self._printer = ProgressPrinter(file_size)

    def __enter__(self):
        SignalManager.instance.sigint(self._printer.stop)
        terminal.lock()
        terminal.write_lines('Downloading {} to {}'.format(self._url,
                                                            self._path))
        terminal.flush()
        terminal.push_lock()
        self._printer.start()
        return self._printer

    def __exit__(self, exc_type, exc_value, traceback):
        self._printer.finish()
        terminal.pop_lock()
        SignalManager.instance.remove(self._printer.stop)

@lazy_configurable(common=['out_dir', 'link_checker_url'])
class Downloader(object):

    def __init__(self, url, download_dir=None):
        self._download_dir = download_dir or self._out_dir
        self.file_path = None
        self._progress = None
        self._check_status(url)
        self._setup_request(url)
        self._setup_filename()

    def check_link(self, url):
        data = dict(response_format='json', link=url)
        response = {}
        try:
            request = requests.post(self._link_checker_url, data=data,
                                    timeout=5)
        except requests.RequestException as e:
            logger.error(e)
        else:
            response = dict(json.loads(request.content))
        finally:
            return LinkStatus(response)

    def _check_status(self, url):
        if self._link_checker_url:
            try:
                self.status = self.check_link(url)
                if not self.status.success:
                    url = resolve_redirect(url)
                    self.status = self.check_link(url)
            except ValueError as e:
                logger.error(e)
            else:
                if not self.status.success or self.status.error:
                    raise InvalidURLError(url, self.status.status)

    def _setup_request(self, url):
        self.url = url
        self._reset_request()

    def _reset_request(self):
        self._request = requests.get(self.url, stream=True)

    def _setup_filename(self):
        cont_disp = self._request.headers.get('content-disposition', '')
        match = re.search('filename="?([^"]+)"?', cont_disp)
        if match:
            name = match.group(1).rsplit('/')[-1]
        else:
            name = self.url.rsplit('/')[-1]
        self.file_path = os.path.join(self._download_dir, name)

    def retrieve(self):
        self._reset_request()
        self._check_size()
        rel = os.path.relpath(self.file_path)
        if rel.startswith('..'):
            rel = self.file_path
        with open(self.file_path, 'wb') as out_file:
            with Progress(self.url, rel, self.file_size) as progress:
                for chunk in self._request.iter_content(chunk_size=10240):
                    out_file.write(chunk)
                    progress.add(len(chunk))

    @property
    def file_size(self):
        return int(self._request.headers.get('content-length', -1))

    @property
    def file_size_str(self):
        return sizeof_fmt(self.file_size)

    def _check_size(self):
        available = free_space_in_dir(self._download_dir)
        if self.file_size > available:
            raise NotEnoughDiskSpace(self._download_dir, self.file_size,
                                     available)

__all__ = ['Downloader']
