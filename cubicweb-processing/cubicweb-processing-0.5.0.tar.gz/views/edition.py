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

"""cubicweb-processing forms"""

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance, match_form_params
from cubicweb.web.views.editforms import EditionFormView

from cubes.wireit.views.edition import WiringCreationFormView

from cubes.processing.views.predicates import (has_link_to_runchain,
                                               _runchain_linkto_eid)


class RunChainEditionFormView(EditionFormView):
    "RunChain edition view that displays the create or edition view of its wiring"
    __select__ = (EditionFormView.__select__ & is_instance('RunChain')
                  & ~ match_form_params('__nowireit'))

    def render_form(self, entity):
        if entity.wiring:
            self._cw.form.setdefault('__redirectpath', entity.rest_path())
            self.wview('edition', rset=entity.wiring[0].as_rset())
        else:
            linkto = ['wiring:%s:object' % entity.eid,
                      'language:%s:subject' % entity.wlang[0].eid]
            self._cw.form.setdefault('__linkto', linkto)
            self._cw.form.setdefault('__redirectpath', entity.rest_path())
            self._cw.form.setdefault('__redirectvid', '')
            self.wview('creation', etype='Wiring')


class _WiringForRunChainCreationFormView(WiringCreationFormView):
    __select__ = WiringCreationFormView.__select__ & has_link_to_runchain()
    __abstract__ = True

    def form_title(self, entity):
        runchain = self._cw.entity_from_eid(_runchain_linkto_eid(self._cw))
        assert runchain.e_schema.type == 'RunChain'
        title = (xml_escape(self._cw._('Creating Wiring for RunChain %s'))
                 % self._cw.view('oneline', rset=runchain.as_rset()))
        self.w(u'<h1>%s</h1>' % title)
