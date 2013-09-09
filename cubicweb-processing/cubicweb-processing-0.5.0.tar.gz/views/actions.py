# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-processing actions"""

from cubicweb.predicates import one_line_rset, is_instance
from cubicweb.web.action import Action

class ExecutableCreateRunAction(Action):
    __regid__ = 'processing.executable_create_run'

    __select__ = one_line_rset() & is_instance('Executable')

    title = _('create a run from this executable')
    category = 'mainactions'

    def url(self):
        linkto = 'executable:%s:subject' % self.cw_rset.get_entity(0, 0).eid
        return self._cw.vreg["etypes"].etype_class(
            'Run').cw_create_url(self._cw, __linkto=linkto)

