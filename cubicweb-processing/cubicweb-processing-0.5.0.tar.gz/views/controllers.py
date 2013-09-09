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

"""controllers for the cubicweb-processing cube"""


from cubicweb.predicates import match_edited_type
from cubicweb.web import Redirect
from cubicweb.web.views.editcontroller import EditController


class RunChainEditController(EditController):
    __select__ = EditController.__select__ & match_edited_type('RunChain')
    
    def _return_to_original_view(self, newparams):
        'go to Wiring edition view for the runchain when just created'
        if (not 'rql' in self._cw.form and
            not '__redirectpath' in self._cw.form and
            any(eid == self._edited_entity.eid
                for eid in self._cw.data.get('eidmap', {}).values())):
            url = self._edited_entity.absolute_url(vid='edition')
            raise Redirect(url)
        super(RunChainEditController, self)._return_to_original_view(newparams)
