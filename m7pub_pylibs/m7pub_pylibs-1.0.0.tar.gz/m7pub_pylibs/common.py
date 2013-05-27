#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009, MARIMORE Inc Tokyo, Japan.
# Contributed by 
#       Iqbal Abdullah <iqbal@marimore.co.jp>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#   *   Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#   *   Redistributions in binary form must reproduce the above copyright notice, 
#       this list of conditions and the following disclaimer in the documentation 
#       and/or other materials provided with the distribution.
#   *   Neither the name of the MARIMORE Inc nor the names of its contributors 
#       may be used to endorse or promote products derived from this software 
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Commonly used code which does not belong to any of the other packages
"""

__author__      = "Iqbal Abdullah <iqbal@marimore.co.jp>"
__date__        = "$LastChangedDate$"
__version__     = "$LastChangedRevision$"

import re

class BaseClass(object):
    """

    .. warning:: This function is DEPRECATED and is not maintained.

    This class was intended to be the parent class for all classes in MARIMORE
    projects. What this class allows you to do is to get the class name of the
    object as a string via a property call.

    You can do the same easily using the __class__ member, as demonstrated
    here_ without having to use this class.

    .. _here: http://stackoverflow.com/questions/510972/getting-the-class-name-of-an-instance-in-python

    """

    def read_only_property(self):
        raise (AttributeError), "Read-only attribute"

    def _prop_set_classname(self, value):
        self.read_only_property()

    def _prop_get_classname(self):
        compiled_re = re.compile("'.*'")
        clsname = compiled_re.search("%s" % (self.__class__)).group()
        clsname = clsname.replace("'","")
        clsname = clsname.replace("%s" % (self.__module__), "")
        clsname = clsname.replace(".","")
        return clsname

    myclassname = property(_prop_get_classname, _prop_set_classname, 
                           doc="Returns the name of the class as a string")
