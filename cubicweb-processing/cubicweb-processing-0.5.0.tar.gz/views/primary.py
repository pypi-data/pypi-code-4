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

from cubicweb.predicates import is_instance, one_line_rset
from cubicweb.web.views.primary import PrimaryView

from cubes.wireit.views.mixins import WiringViewMixin


class RunChainPrimaryView(WiringViewMixin, PrimaryView):
    __select__ = PrimaryView.__select__ & is_instance('RunChain') & one_line_rset()

    def render_entity_attributes(self, entity):
        if entity.wiring and '__nowireit' not in self._cw.form:
            wiring = entity.wiring[0]
            self.setup_editor(wiring, wiring.language[0])
        else:
            super(RunChainPrimaryView, self).render_entity_attributes(entity)
