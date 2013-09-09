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

from logilab.common.registry import objectify_predicate

from cubicweb.predicates import (is_instance, match_form_params,
                                 specified_etype_implements)
from cubicweb.web import stdmsgs
from cubicweb.web.formwidgets import Button, SubmitButton
from cubicweb.web.views.editforms import EditionFormView, CreationFormView

from cubes.wireit.views.mixins import WiringViewMixin


class WiringFormViewMixin(WiringViewMixin):

    def form_title(self, ent):
        """use h1 instead of more sophisticated css-driven design
        that would required cw.form.css"""
        ptitle = self._cw._(self.title)
        self.w(u'<h1>%s %s</h1>' % (ent.dc_type(), ptitle and '(%s)' % ptitle))

    def wiring_descr_html(self, wiring, wlang, editable):
        form = self._cw.vreg['forms'].select(self.form_id, self._cw,
                                             entity=wiring,
                                             submitmsg=self.submited_message())
        form.form_buttons = [SubmitButton(),
                             Button(stdmsgs.BUTTON_CANCEL, cwaction='cancel')]
        return form.render(w=None)


class WiringEditionFormView(WiringFormViewMixin, EditionFormView):
    __select__ = (EditionFormView.__select__ & is_instance('Wiring')
                  & ~ match_form_params('__nowireit'))

    def render_form(self, entity):
        self.form_title(entity)
        self.setup_editor(entity, entity.language[0],
                          editable=True, cancel_url=entity.absolute_url())


def _wlang_linkto_eid(req):
    wlang_eid = None
    for linkto in req.list_form_param('__linkto'):
        rtype, linkto_eid, role = linkto.split(':')
        if rtype == 'language':
            wlang_eid = linkto_eid
            break
    return wlang_eid


@objectify_predicate
def has_link_to_wlang(self, req, **kwargs):
    return _wlang_linkto_eid(req) is not None


class WiringCreationFormView(WiringFormViewMixin, CreationFormView):
    __select__ = (CreationFormView.__select__ & specified_etype_implements('Wiring')
                  & ~match_form_params('__nowireit') & has_link_to_wlang())

    def render_form(self, wiring):
        self.form_title(wiring)
        wlang_eid = _wlang_linkto_eid(self._cw)
        wlang = self._cw.entity_from_eid(int(wlang_eid))
        assert wlang.e_schema.type == 'WiringLanguage'
        self.setup_editor(wiring, wlang, editable=True)
