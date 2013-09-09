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
"""cubicweb-processing ui configuration"""


from cubicweb.web import uicfg as cw_uicfg
from cubes.wireit.views import uicfg as wireit_uicfg

_cw_abaa = cw_uicfg.actionbox_appearsin_addmenu
_cw_pvs = cw_uicfg.primaryview_section

_cw_pvs.tag_subject_of(('RunChain', 'wlang', 'WiringLanguage'), 'hidden')
_cw_pvs.tag_subject_of(('RunChain', 'wiring', 'Wiring'), 'hidden')

_cw_pvs.tag_object_of(('ParameterDefinition', 'parameter_of', 'Executable'),
                      'attributes')
_cw_pvs.tag_object_of(('*', 'value_of_run', 'Run'), 'attributes')

_cw_abaa.tag_object_of(('*', 'parameter_of', 'Executable'), False)
_cw_abaa.tag_object_of(('*', 'value_of_run', 'Run'), False)
_cw_abaa.tag_subject_of(('RunChain', 'has_runs', 'Run'), False)

# Wiring uicfg customization
wireit_uicfg.wireit_pvs.tag_object_of(('RunChain', 'wiring', 'Wiring'), 'attributes')
wireit_uicfg.wireit_afs.tag_object_of(('RunChain', 'wiring', 'Wiring'), 'main', 'hidden')

