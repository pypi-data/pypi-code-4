#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# <LICENSE=ISC>
#

__all__ = ['HTTPException', 'HTTPClientError', 'HTTPServerError']

class HTTPException(BaseException):
    pass

class HTTPClientError(HTTPException):
    pass

class HTTPServerError(HTTPException):
    pass

