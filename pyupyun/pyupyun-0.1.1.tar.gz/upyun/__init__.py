import hashlib
import os.path
from urllib import pathname2url
from urlparse import urljoin

import requests
from requests.auth import AuthBase

from . import const, response
from .auth import UpYunDigestAuthentication

__title__ = 'pyupyun'
__version__ = '0.1.1'
__author__ = 'Kane Dou'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013 Kane Dou'


class UpYun(object):
    """Feature complete UpYun REST client

    :param str bucket: Your bucket
    :param auth: ``(username, passwd)`` pair or any object derived from
                 :class:`requests.auth.AuthBase`
    :param stype: The space type, :const:`~const.SPACE_TYPE_FILE` or
                  :const:`~const.SPACE_TYPE_IMAGE`
    :param api_host: API host to use, see :ref:`API Hosts <api-hosts>`
    :param str domain: Your custom domain
    :param bool ssl: Whether to use SSL

    Usage::

        client = UpYun('test', ('user', 'pass'), const.SPACE_TYPE_FILE)
        client.put('/test.txt', open('/tmp/test.txt'))
    """
    def __init__(self, bucket, auth, stype, api_host=const.API_HOST_AUTO,
            domain=None, ssl=False):
        self.bucket = bucket
        self.stype = stype
        self.api_host = api_host
        proto = 'https://' if ssl else 'http://'
        self._base_url = proto + const.UPAIYUN_API_HOSTS[self.api_host]
        self.domain = domain or (const.BUCKET_DOMAIN % bucket)
        self._bucket_base_url = proto + self.domain

        #: The :class:`requests.Session` object to use for the API requests
        self.session = self._prepare_session(auth, ssl)

    @property
    def api_host(self):
        return self._api_host

    @api_host.setter
    def api_host(self, api_host):
        if api_host in const.UPAIYUN_API_HOSTS:
            self._api_host = api_host
        else:
            raise Exception('api_host: invalid api host')

    @property
    def stype(self):
        return self._stype

    @stype.setter
    def stype(self, stype):
        if stype in [const.SPACE_TYPE_FILE, const.SPACE_TYPE_IMAGE]:
            self._stype = stype
        else:
            raise Exception('stype: invalid space type')

    def _prepare_session(self, auth, ssl):
        if isinstance(auth, AuthBase):
            self._auth = auth
        else:
            self._auth = auth if ssl else UpYunDigestAuthentication(*auth)
        s = requests.Session()
        s.auth = self._auth
        return s

    def _get_file_url(self, path):
        return urljoin(self._bucket_base_url, path)

    def _get_url(self, path):
        return urljoin(self._base_url,
                pathname2url(os.path.join(self.bucket, path.lstrip('/'))))

    def _get_data(self, fileo):
        try:
            data = fileo.read()
        except AttributeError:
            data = fileo
        return data

    def _digest(self, data):
        return hashlib.md5(data).hexdigest()

    def _prepare_put_request(self, path, fileo, mkdir, mimetype, secret,
            verify, headers=None):
        """Prepaer the put request"""
        url = self._get_url(path)
        data = self._get_data(fileo)
        headers = headers or {}
        req_headers = {}

        if mkdir:
            req_headers[const.HEADER_MKDIR] = 'true'
        if verify:
            req_headers[const.HEADER_MD5] = self._digest(data)
        if mimetype:
            req_headers['Content-Type'] = mimetype
        if secret:
            req_headers[const.HEADER_SECRET] = secret

        req_headers.update(headers)
        return url, data, req_headers

    def put(self, path, fileo, mkdir=True, mimetype=None, secret=None,
            verify=True, headers=None):
        """Put an file onto the server

        :param path: File path on the server
        :param fileo: File like object of the file to upload
        :param mkdir: Whether to make the parent folder if not existed
        :param mimetype: Mime-type of the file, used by server to determine
                         the extension of the file
        :param secret: Secret for user to later access the file uploaded
        :param verify: Whether to verify the file integrity using md5 hashing
        :param headers: Additional headers
        :rtype: :class:`~response.Response` or
                :class:`~response.PutImageResponse`
        """
        url, data, headers = self._prepare_put_request(path, fileo, mkdir,
                mimetype, secret, verify, headers or {})
        resp = self.session.put(url=url, data=data, headers=headers)
        if self.stype == const.SPACE_TYPE_IMAGE:
            return response.PutImageResponse(resp, self._get_file_url(path))
        return response.Response(resp, self._get_file_url(path))

    def put_thumbnail(self, path, fileo, version=None, ttype=None, res=None,
            quality=None, sharpen=None, **kwargs):
        """Put an image as a thumbnail on the server, the original image
        will not be uploaded

        :param path: Thumbnail path on the server
        :param fileo: File like object of the image
        :param version: Predefined thumbnail version name
        :param ttype: Thumbnail type, see :const:`~const.THUMB_TYPES`
        :param res: Image resolution, format: (width, height)
        :param quality: Image quality, default: 90
        :param sharpen: Whether to sharpen the image
        :type res: tuple
        :type sharpen: bool
        :rtype: :class:`~response.PutImageResponse`
        """
        if not (version or (ttype and res)):
            raise Exception(
                    'put: needs either version or thumbnail type, or both')
        headers = {}
        if version:
            if self.stype != const.SPACE_TYPE_IMAGE:
                raise Exception('put: need space type image')
            headers[const.HEADER_THUMB_VERSION] = version
        if ttype:
            if ttype not in const.THUMB_TYPES:
                raise Exception('put: invalid thumbnail type')
            headers[const.HEADER_THUMB_TYPE] = const.THUMB_TYPES[ttype]
            if res:
                if ttype in (const.THUMB_TYPE_FIX_BOTH,
                        const.THUMB_TYPE_FIX_WIDTH_OR_HEIGHT):
                    res_val = res[0] + 'x' + res[1]
                else:
                    res_val = res[0]
                headers[const.HEADER_THUMB_VALUE] = res_val
        if quality:
            headers[const.HEADER_THUMB_QUALITY] = int(quality)
        if sharpen is not None:
            headers[const.HEADER_THUMB_UNSHARP] = str(not sharpen).lower()

        uheaders = kwargs.pop('headers', {})
        headers.update(uheaders)

        return self.put(path, fileo, headers=headers, **kwargs)

    def get(self, path):
        """Get a file

        :param path: Path of the file to retrieve
        :rtype: :class:`~response.GetResponse`
        """
        resp = self.session.get(self._get_url(path))
        return response.GetResponse(resp, self._get_file_url(path))

    def delete(self, path):
        """Delete a file or an empty folder

        :param path: Path of the file or folder to delete
        :rtype: :class:`~response.Response`
        """
        resp = self.session.delete(self._get_url(path))
        return response.Response(resp, None)

    def mkdir(self, path, mk_parent=True):
        """Create a folder on server

        :param path: Folder path
        :param mk_parent: Whether to create the parent folder if not existed
        :rtype: :class:`~response.Response`
        """
        url = self._get_url(path)
        headers = {}
        headers[const.HEADER_FOLDER] = 'create'
        if mk_parent:
            headers[const.HEADER_MKDIR] = 'true'
        resp = self.session.post(url, headers=headers)
        return response.Response(resp, self._get_file_url(path))

    def ls(self, path):
        """List contents of a folder

        :param path: Path to the folder
        :rtype: :class:`~response.LsResponse`
        """
        resp = self.session.get(self._get_url(path))
        return response.LsResponse(resp, self._get_file_url(path))

    def usage(self):
        """Retrieve the space usage info

        :rtype: :class:`~response.UsageResponse`
        """
        resp = self.session.get(self._get_url(''), params='usage')
        return response.UsageResponse(resp, None)

    def info(self, path):
        """Retrieve file info

        :rtype: :class:`~response.InfoResponse`
        """
        resp = self.session.head(self._get_url(path))
        return response.InfoResponse(resp, self._get_file_url(path))
