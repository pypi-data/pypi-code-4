#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# file pyroots/__init__.py
#
#############################################################################
# Copyright (c) 2013 by Panagiotis Mavrogiorgos
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name(s) of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AS IS AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#############################################################################
#
# @license: http://opensource.org/licenses/BSD-3-Clause
# @authors: see AUTHORS.txt

"""
A python-only implementation of single-variable root finding methods.

Currently the following methods have been implemented:

    # brent
    # bisect
    # ridder

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

# Version
__major__ = 0       # for major interface/format changes
__minor__ = 1       # for minor interface/format changes
__release__ = 0     # for tweaks, bug-fixes, or development

# package information
__package_name__ = "pyroots"
__version__ = "%d.%d.%d" % (__major__, __minor__, __release__)
__license__ = "BSD"
__description__ = "A python-only implementation of single-variable root finding methods."
__url__ = "http://bitbucket.org/pmav99/%s" % __package_name__
__download_url__ = "http://bitbucket.org/pmav99/%s/downloads" % __package_name__
__author__ = "Panagiotis Mavrogiorgos"
__author_email__ = "gmail pmav99"

# Package imports
__all__ = ["brent", "bisect", "ridder", "ConvergenceError", "Result"]

from pyroots.brent import brent
from pyroots.bisect import bisect
from pyroots.ridder import ridder
from pyroots.utils import ConvergenceError, Result
