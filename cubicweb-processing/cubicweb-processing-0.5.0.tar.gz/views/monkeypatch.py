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
"""cubicweb-processing monkeypatch"""

from logilab.common.decorators import monkeypatch

from cubicweb.web.views.autoform import AutomaticEntityForm

@monkeypatch(AutomaticEntityForm)
def inlined_form_views(self):
    """compute and return list of inlined form views (hosting the inlined
    form object)

    """
    allformviews = []
    entity = self.edited_entity
    for rschema, ttypes, role in self.inlined_relations():
        # show inline forms only if there's one possible target type
        # for rschema
        if len(ttypes) != 1:
            self.warning('entity related by the %s relation should have '
                         'inlined form but there is multiple target types, '
                         'dunno what to do', rschema)
            continue
        tschema = ttypes[0]
        ttype = tschema.type
        formviews = list(self.inline_edition_form_view(rschema, ttype, role))
        card = rschema.role_rdef(entity.e_schema, ttype, role).role_cardinality(role)
        # there is no related entity and we need at least one: we need to
        # display one explicit inline-creation view
        if self.should_display_inline_creation_form(rschema, formviews, card):
            formviews += self.inline_creation_form_view(rschema, ttype, role)
        # we can create more than one related entity, we thus display a link
        # to add new related entities
        if self.must_display_add_new_relation_link(rschema, role, tschema,
                                                   ttype, formviews, card):
            addnewlink = self._cw.vreg['views'].select(
                'inline-addnew-link', self._cw,
                etype=ttype, rtype=rschema, role=role, card=card,
                peid=self.edited_entity.eid,
                petype=self.edited_entity.e_schema, pform=self)
            formviews.append(addnewlink)
        allformviews += formviews
    return allformviews

@monkeypatch(AutomaticEntityForm)
def must_display_add_new_relation_link(self, rschema, role, tschema,
                                       ttype, existant, card):
    """return true if we must add a link to add a new creation form
    (through ajax call)

    by default true if there is no related entity or if the relation has
    multiple cardinality and it is permitted to add the inlined object and
    relation.
    """
    return (self.should_display_add_new_relation_link(
                rschema, existant, card) and
            self.check_inlined_rdef_permissions(
                rschema, role, tschema, ttype))

@monkeypatch(AutomaticEntityForm)
def check_inlined_rdef_permissions(self, rschema, role, tschema, ttype):
    """return true if permissions are granted on the inlined object and
    relation"""
    entity = self.edited_entity
    rdef = entity.e_schema.rdef(rschema, role, ttype)
    if entity.has_eid():
        if role == 'subject':
            rdefkwargs = {'fromeid': entity.eid}
        else:
            rdefkwargs = {'toeid': entity.eid}
    else:
        rdefkwargs = {}
    return (tschema.has_perm(self._cw, 'add')
            and rdef.has_perm(self._cw, 'add', **rdefkwargs))

