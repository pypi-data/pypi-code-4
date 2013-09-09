# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-wireit entity's classes"""
from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity
from cubicweb.view import EntityAdapter

from json import loads

class Wiring(AnyEntity):
    __regid__ = 'Wiring'

    @property
    def wlang(self):
        return self.language[0]

    @property
    def module_names(self):
        if self.json:
            return frozenset(m['name'] for m in loads(self.json).get('modules'))
        return ()

class WiringLanguage(AnyEntity):
    __regid__ = 'WiringLanguage'

    @property
    def module_names(self):
        if self.json:
            return frozenset(m['name'] for m in loads(self.json).get('modules'))
        return ()

class WireitJson(EntityAdapter):
    __regid__ = 'wireit.json'
    __select__ = is_instance('Wiring', 'WiringLanguage')

    @property
    def json(self):
        return self.entity.json
