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
Data Dumps
"""

from ..csvutil import DictWriter
from sqlalchemy.orm import class_mapper


def dump_data(session, model, outfile, order_by=None, progress=None):
    """
    Dump data for a model in CSV format.

    :param session: A SQLAlchemy session instance.

    :param model: A model class whose table data will be dumped.

    :param outfile: A file-like object to which the data will be written.

    :param order_by: Optional "ORDER BY" clause element for the query.  If none
       is specified, the model's ``uuid`` attribute will be used.

    :returns: Number of data records written.
    """

    query = session.query(model)
    if order_by is not None:
        query = query.order_by(order_by)
    elif hasattr(model, 'uuid'):
        query = query.order_by(model.uuid)
    count = query.count()
    if not count:
        return 0

    prog = None
    if progress:
        prog = progress("Dumping {0} data".format(model.__name__), count)

    keys = class_mapper(model).columns.keys()
    writer = DictWriter(outfile, keys)
    writer.writeheader()

    for i, obj in enumerate(query, 1):
        data = {}
        for key in keys:
            data[key] = getattr(obj, key)
        writer.writerow(data)
        if prog:
            prog.update(i)
    if prog:
        prog.destroy()
