#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
Core Data Stuff
"""

from sqlalchemy import Column, String
from ..core import get_uuid


__all__ = ['uuid_column']


def uuid_column(*args, **kwargs):
    """
    Returns a UUID column for use as a table's primary key.
    """

    kwargs.setdefault('primary_key', True)
    kwargs.setdefault('nullable', False)
    kwargs.setdefault('default', get_uuid)
    return Column(String(length=32), *args, **kwargs)
