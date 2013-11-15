#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

class Invalid(Exception):
    def __init__(self, message, value, errors=None):
        Exception.__init__(self, message, value, errors)
        self.message = message
        self.value = value
        self.errors = errors