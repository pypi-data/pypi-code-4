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

"""cubicweb-wireit specific hooks and operations"""

from json import loads

from cubicweb import ValidationError
from cubicweb.predicates import is_instance
from cubicweb.server.hook import Hook, Operation, DataOperationMixIn


class BeforeAddWiringHook(Hook):
    __regid__ = 'wireit.before_add_wiring'
    __select__ = Hook.__select__ & is_instance('Wiring')
    events = ('before_add_entity',)

    def __call__(self):
        self.entity.cw_edited.setdefault('name', (
            self._cw._(u'wiring %s') % self.entity.eid))


class WiringValidityCheckOp(DataOperationMixIn, Operation):
    'Checks the validity of all wirings attached to a (e.g. edited) language'

    def module_def(self, module_name, wlang_json):
        '''
        Return module of name `module_name` definition in the definition of
        the wiring language definition `wlang_def`, or None if not found.
        '''
        for module in loads(wlang_json)['modules']:
            if module['name'] == module_name:
                return module

    def precommit_event(self):
        '''
        Minimal semi-incremental check for the validity of all wirings of
        a wiring language:

        * check the modules of a wiring are present in the language definition
        * suppose the wirings were valid for the old version of the language and
          check the new version does not change the module definitions used by
          the wirings.
        '''
        for wlang, old_json in self.get_data():
            for wiring in wlang.reverse_language:
                used_modules = wiring.module_names
                if not used_modules.issubset(wlang.module_names):
                    msg = wiring._cw._('Invalid WiringLanguage change')
                    raise ValidationError(wlang.eid, {'json': msg})
                for module in used_modules:
                    if (self.module_def(module, wlang.json)
                        != self.module_def(module, old_json)):
                        msg = wiring._cw._('Invalid WiringLanguage change')
                        raise ValidationError(wlang.eid, {'json': msg})


class BeforeUpdateWiringLanguageHook(Hook):
    __regid__ = 'wireit.before_update_language'
    __select__ = Hook.__select__ & is_instance('WiringLanguage')
    events = ('before_update_entity',)

    def __call__(self):
        wl = self.entity
        if 'json' in wl.cw_edited:
            old, new = wl.cw_edited.oldnewvalue('json')
            if not old is None:
                WiringValidityCheckOp.get_instance(self._cw).add_data((wl, old))
