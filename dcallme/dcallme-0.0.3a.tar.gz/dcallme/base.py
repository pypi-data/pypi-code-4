# -*- coding: utf-8 -*-
import requests

from .errors import DataTypeError, UidFormatError


class _base:

    base_url_format = '{protocol}://{host}:{port}/{namespace}'

    def _request(self, method, url_format='/', data=None):
        url_format = self.base_url_format + url_format
        url_data = {'protocol': 'https' if self.is_secure else 'http',
                    'host': self.host,
                    'port': self.port,
                    'namespace': self.namespace,
                    'uid': getattr(self, 'uid', None)}
        resp = getattr(requests, method)(url=url_format.format(**url_data), headers=self.headers, data=data)
        resp.raise_for_status()
        return resp.json()

    def all(self):
        return self._request('get')

    def get(self, uid):
        if not (type(uid) is int or str(uid).isdigit()):
            raise UidFormatError(uid)
        self.uid = uid
        return self._request('get', '/{uid}/')

    def create(self, data):
        if not type(data) is dict:
            raise DataTypeError(type(data))
        return self._request('post', '/add/', data)

    def update(self, uid, data):
        if not (type(uid) is int or str(uid).isdigit()):
            raise UidFormatError(uid)
        if not type(data) is dict:
            raise DataTypeError(type(data))
        self.uid = uid
        return self._request('put', '/{uid}/', data)

    def delete(self, uid):
        if not (type(uid) is int or str(uid).isdigit()):
            raise UidFormatError(uid)
        self.uid = uid
        return self._request('delete', '/{uid}/')
