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

"""cubicweb-wireit schema"""

from yams.buildobjs import EntityType, SubjectRelation, String


class WiringLanguage(EntityType):
    name = String(required=True, maxsize=128, description=_('name of the wiring language'))
    json = String(description=_('json description of the wiring language as used by WireIt itself'))


class Wiring(EntityType):
    name = String(required=True, maxsize=128, description=_('name of the Wiring'))
    language = SubjectRelation('WiringLanguage', cardinality='1*', inlined=True, composite='object',
                               description=_('Wiring language used to define this wiring'))
    json = String(description=_('json description of the wiring as serialized by WireIt itself'))
