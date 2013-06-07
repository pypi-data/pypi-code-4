#!/usr/bin/env python
#-*- coding:utf-8 -*-


class LoginFailError(Exception):
    """Login Fail Error.

    The exception will be raised if all auto login attempts fail.
    """
    def __init__(self, message="auto login fails, please check your info"):
        super(LoginFailError, self).__init__(message)
