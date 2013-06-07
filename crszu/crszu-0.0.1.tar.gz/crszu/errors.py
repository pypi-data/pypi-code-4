#!/usr/bin/env python
#-*- coding:utf-8 -*-


class InvalidSizeError(ValueError):
    """Invalid Size Error.

    The exception will be raised while filter size is not applicable.
    """
    def __init__(self, size, message=" is not an valid filter size"):
        message = str(size) + message
        super(InvalidSizeError, self).__init__(message)


class SizeTypeError(TypeError):
    """Size Type Error Error.

    The exception will be raised wihle filter size is not integer.
    """
    def __init__(self, size, message="integer argument expected, got "):
        message += str(type(size))[7:-2]
        super(SizeTypeError, self).__init__(message)
