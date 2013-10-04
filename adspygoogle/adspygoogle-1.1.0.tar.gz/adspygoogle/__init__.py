#!/usr/bin/python
#
# Copyright 2010 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Contains common constants for PyPI release scripts."""
__author__ = 'api.msaniscalchi@gmail.com (Mark Saniscalchi)'

from adspygoogle.common import GenerateLibSig
from adspygoogle.adwords.AdWordsClient import AdWordsClient
from adspygoogle.dfa.DfaClient import DfaClient
from adspygoogle.dfp.DfpClient import DfpClient

LIB_PYPI_VERSION = '1.1.0'
LIB_PYPI_NAME = 'Google Ads Python Client Library'
LIB_PYPI_SHORT_NAME = 'adspygoogle'
LIB_PYPI_URL = 'http://code.google.com/p/google-api-ads-python'
LIB_PYPI_AUTHOR = 'Joseph DiLallo'
LIB_PYPI_AUTHOR_EMAIL = 'api.jdilallo@gmail.com'
LIB_PYPI_SIG = GenerateLibSig(LIB_PYPI_SHORT_NAME, LIB_PYPI_VERSION)
