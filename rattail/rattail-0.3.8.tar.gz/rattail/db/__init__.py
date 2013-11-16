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
Database Stuff
"""

from edbob.db import Session

from .core import *
from .changes import *


def init(config):
    """
    Initialize the Rattail database framework.
    """

    import edbob
    import rattail

    # Pretend all ``edbob`` models come from Rattail, until that is true.
    from edbob.db import Base
    names = []
    for name in edbob.__all__:
        obj = getattr(edbob, name)
        if isinstance(obj, type) and issubclass(obj, Base):
            names.append(name)
    edbob.graft(rattail, edbob, names)

    # Pretend all ``edbob`` enumerations come from Rattail.
    from edbob import enum
    edbob.graft(rattail, enum)

    from rattail.db.extension import model
    edbob.graft(rattail, model)

    ignore_role_changes = config.getboolean(
        'rattail.db', 'changes.ignore_roles', default=True)

    if config.getboolean('rattail.db', 'changes.record'):
        record_changes(Session, ignore_role_changes)

    elif config.getboolean('rattail.db', 'record_changes'):
        import warnings
        warnings.warn("Config setting 'record_changes' in section [rattail.db] "
                      "is deprecated; please use 'changes.record' instead.",
                      DeprecationWarning)
        record_changes(Session, ignore_role_changes)
