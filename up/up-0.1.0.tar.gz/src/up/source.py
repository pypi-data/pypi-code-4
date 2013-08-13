from up.util import NAME_SEPARATOR
from urllib.request import build_opener, Request
from urllib.error import HTTPError, URLError
from http.client import BadStatusLine, IncompleteRead
import io
import gzip
import json
import time
import threading

UP = 1
DOWN = 0


class InvalidNameError(Exception):
    pass


class StatusSource(object):
    def __init__(self, name):
        super(StatusSource, self).__init__()

        if NAME_SEPARATOR in name:
            raise InvalidNameError('name contains invalid character "' + NAME_SEPARATOR + '"')

        self.name = name
        self.status = UP
        self.date = None
        self.duration = 0

    def timed_prepare(self):
        self.date = time.time()
        self.prepare()
        self.duration = time.time() - self.date

    def prepare(self):
        raise NotImplemented


class StatusTreeSource(StatusSource):
    def __init__(self, name, children=None):
        super(StatusTreeSource, self).__init__(name)

        # default arguments are evaulated a compile time and are references
        if not children:
            children = list()

        self.children = children

    def calculate(self):
        total = 0

        for child in self.children:
            total += child.status

        if len(self.children) > 0:
            return total / len(self.children)

        return 0

    def prepare(self):

        for child in self.children:
            child.timed_prepare()

        self.status = self.calculate()


class ThreadedTreeSource(StatusTreeSource):

    def __threaded_prepare(self, source):
        source.timed_prepare()

    def prepare(self):
        threads = []

        for child in self.children:
            status_thread = threading.Thread(target=self.__threaded_prepare, args=(child,))
            status_thread.start()
            threads.append(status_thread)

        for thread in threads:
            thread.join()

        self.status = self.calculate()


class HTTPStatusSource(StatusSource):
    def __init__(self, name, url):
        super(HTTPStatusSource, self).__init__(name)

        self.url = url
        self.request = Request(self.url)
        self.result = None

        self.request.add_header('Accept-encoding', 'gzip')

    def _get_result(self):
        # for thread safety
        opener = build_opener()
        status_connection = opener.open(self.request)
        data = status_connection.read()

        if status_connection.info().get('Content-Encoding') == 'gzip':
            buf = io.BytesIO(data)
            file_obj = gzip.GzipFile(fileobj=buf)
            data = file_obj.read()

        return data.decode('utf-8')

    def prepare(self):
        if not self.result:
            self.status = UP

            try:
                self.result = self._get_result()
            except (HTTPError, URLError, BadStatusLine, IncompleteRead):
                self.status = DOWN


class GitHubStatusSource(HTTPStatusSource):
    def __init__(self, name='GitHub', url='https://status.github.com/api/status.json'):
        super(GitHubStatusSource, self).__init__(name, url)

    def prepare(self):
        super(GitHubStatusSource, self).prepare()

        self.status = DOWN

        self.result = json.loads(self.result)
        # TODO: Find something to do with 'minor' and 'major' statuses.
        # TODO: Find something to do with 'last_updated' date.
        if self.result['status'] == 'good':
            self.status = UP
        elif self.result['status'] == 'minor':
            self.status = 0.5
