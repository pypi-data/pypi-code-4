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

"""cubicweb-wireit forms"""

from cubicweb.predicates import is_instance, match_form_params
from cubicweb.schema import META_RTYPES
from cubicweb.web import uicfg as cw_uicfg, formwidgets as fwdgs

from cubicweb.predicates import is_instance, match_form_params
from cubicweb.web.views import uicfg


# custom uicfg

class WireItWiringCustomUicfgMixin(object):
    __select__ = is_instance('Wiring') & ~match_form_params('__nowireit')

class WireItWiringAfs(WireItWiringCustomUicfgMixin, uicfg.AutoformSectionRelationTags):
    pass

class WireItWiringAffk(WireItWiringCustomUicfgMixin, uicfg.AutoformFieldKwargsTags):
    pass

class WireItWiringPvs(WireItWiringCustomUicfgMixin, uicfg.PrimaryViewSectionRelationTags):
    pass

wireit_afs = WireItWiringAfs()
wireit_affk = WireItWiringAffk()
wireit_pvs = WireItWiringPvs()

# default uicfg

_abaam = cw_uicfg.actionbox_appearsin_addmenu
_abaam.tag_object_of(('Wiring', 'language', 'WiringLanguage'), True)

# custom uicfg


wireit_affk.tag_attribute(('Wiring', 'name'),
                          {'widget': fwdgs.TextInput(attrs=dict(size=25))})
wireit_affk.tag_attribute(('Wiring', 'json'),
                          {'widget': fwdgs.HiddenInput})
wireit_affk.tag_subject_of(('Wiring', 'language', 'WiringLanguage'),
                           {'widget': fwdgs.HiddenInput})


wireit_pvs.tag_attribute(('Wiring', 'json'), 'hidden')
for rtype in META_RTYPES:
    wireit_pvs.tag_subject_of(('*', rtype, '*'), 'hidden')
    wireit_pvs.tag_object_of(('*', rtype, '*'), 'hidden')
