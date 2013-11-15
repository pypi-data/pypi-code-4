#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import inspect
from tests.validators.base import Test as base
from tests.validators.chained import Test as chained
from tests.validators.compound import Test as compound
from tests.validators.dates import Test as dates
from tests.validators.encoders import Test as encoders
from tests.validators.files import Test as files
from tests.validators.geographic import Test as geographic
from tests.validators.network import Test as network
from tests.validators.numbers import Test as numbers
from tests.validators.schema import Test as schema
from tests.validators.signers import Test as signers
from tests.validators.strings import Test as strings
__all__ = sorted(name for name, obj in locals().items()
                 if not (name.startswith('_') or inspect.ismodule(obj))) 
del inspect