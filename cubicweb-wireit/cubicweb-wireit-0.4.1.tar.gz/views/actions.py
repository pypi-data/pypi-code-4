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
"""cubicweb-wireit actions"""

from cubicweb.predicates import match_user_groups, is_instance
from cubicweb.web.action import Action

class WiringAdminViewSourceJson(Action):
    """action for admins who want to see the json source code of a wiring"""

    __regid__ = 'processing.wiring_admin_view'
    __select__ = (Action.__select__ & match_user_groups('managers')
                  & is_instance('Wiring'))

    title = _('view source code')
    category = 'mainactions'

    def url(self):
        wiring = self.cw_rset.get_entity(0, 0)
        return wiring.absolute_url(__nowireit='')
