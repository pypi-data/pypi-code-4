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
``rattail.db.batches.util`` -- Batch Utilities
"""

import re

from sqlalchemy import MetaData

import edbob
from edbob.time import local_time

import rattail
from rattail.db.extension.model import Batch


def purge_batches(session, effective_date=None, purge_everything=False):
    """
    Purge old batches from the database.

    :param session: Active database session.

    :param effective_date: Date against which comparisons should be made when
      determining if a batch is "old" (based on its ``purge_date`` attribute).
      The current date is assumed if none is specified.

    :param purge_everything: Boolean indicating whether the purge should be
      complete and indiscriminate, as opposed to honoring batch purge dates.
      (Use with caution!)

    :returns: Number of batches purged.
    :rtype: int
    """

    if effective_date is None:
        edbob.init_modules(['edbob.time'])
        effective_date = local_time().date()

    purged = 0

    q = session.query(Batch)
    if not purge_everything:
        q = q.filter(Batch.purge != None)
        q = q.filter(Batch.purge < effective_date)
    for batch in q:
        batch.drop_table()
        session.delete(batch)
        session.flush()
        purged += 1

    # This should theoretically not be necessary, if/when the batch processing
    # is cleaning up after itself properly.  For now though, it seems that
    # orphaned data tables are sometimes being left behind.

    batch_pattern = re.compile(r'^batch\.[0-9a-f]{32}$')

    current_batches = []
    for batch in session.query(Batch):
        current_batches.append('batch.%s' % batch.uuid)

    def orphaned_batches(name, metadata):
        if batch_pattern.match(name):
            if name not in current_batches:
                return True
        return False

    metadata = MetaData(session.bind)
    metadata.reflect(only=orphaned_batches)
    for table in reversed(metadata.sorted_tables):
        table.drop()

    return purged
