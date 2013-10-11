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
``tailbone.forms.fields`` -- FormAlchemy Fields
"""

from formalchemy import Field


__all__ = ['AssociationProxyField']


def AssociationProxyField(name, **kwargs):
    """
    Returns a ``Field`` class which is aware of SQLAlchemy association proxies.
    """

    class ProxyField(Field):

        def sync(self):
            if not self.is_readonly():
                setattr(self.parent.model, self.name,
                        self.renderer.deserialize())

    def value(model):
        try:
            return getattr(model, name)
        except AttributeError:
            return None

    kwargs.setdefault('value', value)
    return ProxyField(name, **kwargs)
