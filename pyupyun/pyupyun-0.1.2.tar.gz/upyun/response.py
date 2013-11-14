from collections import namedtuple
from datetime import datetime
import os.path
import urllib
import urlparse

import requests

from upyun import const


class ResponseBase(object):
    """A response of successfully uploading image, contains extra info
    of the uploaded image

    :param response: Response from UpYun
    :type response: :class:`requests.Response`
    :param str url: URL of the file on the UpYun
    """
    def __init__(self, response, url):
        #: Raw :class:`requests.Response` from UpYun
        self.response = response

        #: URL of the file on the UpYun
        self.url = url

        #: Error of the request, a :class:`tuple` in the form of
        #: ``(<status code>, <error message>)``
        self.error = self._populate_error()

    def _get_header_with_prefix(self, name):
        return self.response.headers.get(const.HEADER_UPYUN_PREFIX + name)

    def _populate_error(self):
        if not self.success:
            return (self.response.status_code, self.response.content.strip())

    @property
    def success(self):
        """Whether the API request is successful"""
        return self.response.status_code == requests.codes.ok


class ImageInfoMixin(object):
    @property
    def width(self):
        """
        Width of the image

        :rtype: :class:`int` or :class:`None`
        """
        w = self._get_header_with_prefix('width')
        return int(w) if w else None

    @property
    def height(self):
        """
        Height of the image

        :rtype: :class:`int` or :class:`None`
        """
        h = self._get_header_with_prefix('height')
        return int(h) if h else None

    @property
    def frames(self):
        """
        Frames of the image

        :rtype: :class:`int` or :class:`None`
        """
        f = self._get_header_with_prefix('frames')
        return int(f) if f else None


class FileInfoMixin(object):
    @property
    def date(self):
        """File created date

        :rtype: :class:`datetime.datetime` or :class:`None`
        """
        d = self._get_header_with_prefix('file-date')
        return datetime.utcfromtimestamp(int(d)) if d else None

    @property
    def size(self):
        """File size

        :rtype: :class:`int` or :class:`None`
        """
        s = self._get_header_with_prefix('file-size')
        return int(s) if s else None


class UsageMixin(object):
    @property
    def usage(self):
        """Usage of the space in bytes

        :rtype: :class:`int` or :class:`None`
        """
        return int(self.response.text) if self.response.text else None


class FileTypeMixin(object):
    @property
    def type(self):
        """File type of the queried path

        :const:`~upyun.const.FILE_TYPE_FILE` or
        :const:`~upyun.const.FILE_TYPE_FOLDER`
        """
        ft = self._get_header_with_prefix('file-type')
        if ft:
            ft = ft.lower()
            if ft == 'file':
                return const.FILE_TYPE_FILE
            elif ft == 'folder':
                return const.FILE_TYPE_FOLDER


class GetMixin(object):
    @property
    def data(self):
        """Data of the downloaded file"""
        return self.response.content


class LsMixin(object):
    TYPE_FILE_STR = 'N'
    TYPE_FOLDER_STR = 'F'

    FileInfo = namedtuple('FileInfo',
            ['name', 'path', 'url', 'type', 'size', 'mtime'])

    def _parse_response(self):
        self._files = {}
        self._folders = {}

        for l in self.response.content.strip().split("\n"):
            name, type, size, mtime = l.strip().split("\t")

            name = unicode(name, 'utf-8')
            type = type.upper()
            url_parsed = urlparse.urlparse(self.url)
            folder_path = url_parsed.path

            path = urlparse.urljoin(folder_path, name)
            url = urlparse.urljoin(
                    (url_parsed.scheme + '://' + url_parsed.netloc), path)
            mtime = datetime.utcfromtimestamp(float(mtime))

            if type == self.TYPE_FILE_STR:
                f = self.FileInfo(name=name, path=path, url=url,
                        type=const.FILE_TYPE_FILE, size=int(size), mtime=mtime)
                self._files[name] = f
            elif type == self.TYPE_FOLDER_STR:
                f = self.FileInfo(name=name, path=path, url=url,
                        type=const.FILE_TYPE_FOLDER, size=int(size), mtime=mtime)
                self._folders[name] = f

    @property
    def files(self):
        """Files in the directory

        Key is the file name, value is
        :class:`~upyun.response.LsMixin.FileInfo`

        :rtype: :class:`dict`
        """
        if not hasattr(self, '_files'):
            self._parse_response()
        return self._files

    @property
    def folders(self):
        """Folders in the directory

        Key is the folder name, value is
        :class:`~upyun.response.LsMixin.FileInfo`

        :rtype: :class:`dict`
        """
        if not hasattr(self, '_folders'):
            self._parse_response()
        return self._folders

    @property
    def stuffs(self):
        """All the stuffs in the directory

        Key is file or folder name, value is
        :class:`~upyun.response.LsMixin.FileInfo`

        :rtype: :class:`dict`
        """
        stuffs = {}
        stuffs.update(self.files)
        stuffs.update(self.folders)
        return stuffs


class PutImageResponse(ResponseBase, ImageInfoMixin, FileTypeMixin):
    pass


class InfoResponse(ResponseBase, FileInfoMixin, FileTypeMixin):
    pass


class UsageResponse(ResponseBase, UsageMixin):
    pass


class GetResponse(ResponseBase, GetMixin):
    pass


class LsResponse(ResponseBase, LsMixin):
    pass


class Response(ResponseBase):
    pass
