# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from rest_framework.exceptions import APIException

class NodeTreeError(Exception):
    pass

class AlreadyRegistered(NodeTreeError):
    pass

class NotRegistered(NodeTreeError):
    pass

class QueryParamError(APIException):

    detail = 'Invalid query parameter'
    status_code = status.HTTP_400_BAD_REQUEST

class URLParamError(APIException):

    detail = 'Invalid search URL parameter'
    status_code = status.HTTP_400_BAD_REQUEST