# copyright 2012-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from cubicweb.predicates import is_instance, match_form_params
from cubicweb.web.views.primary import PrimaryView

from cubes.wireit.views.mixins import WiringViewMixin


class WiringPrimaryView(WiringViewMixin, PrimaryView):
    __select__ = (PrimaryView.__select__ & is_instance('Wiring')
                  & ~ match_form_params('__nowireit'))

    def render_entity(self, entity):
        self.render_entity_title(entity)
        self.setup_editor(entity, entity.language[0])

    def wiring_descr_html(self, wiring, wlang, editable):
        w, html = self.w, []
        self.w = html.append
        self.render_entity_attributes(wiring)
        self.w = w
        return u''.join(html)

