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

import os.path as osp
from json import loads, dumps

from cubicweb import ValidationError
from cubicweb.web import RemoteCallFailed
from cubicweb.devtools.testlib import CubicWebTC

HERE = osp.dirname(__file__)


class WiringTCMixin(object):

    def setup_database(self):
        super(WiringTCMixin, self).setup_database()
        self.wl = self.request().create_entity('WiringLanguage', name=u'wl')
        self.commit()


class WiringAddHookTC(WiringTCMixin, CubicWebTC):

    def test_name(self):
        'creating a wiring with no name should not crash but set it'
        ce = self.request().create_entity
        wiring = ce('Wiring', language=self.wl, json=u'')
        self.commit()
        self.assertTrue(wiring.name)


class UpdateWiringLanguageHookTC(WiringTCMixin, CubicWebTC):

    def setup_database(self):
        super(UpdateWiringLanguageHookTC, self).setup_database()
        self.wl.cw_set(json=self._json_content('wlan.json'))
        ce = self.request().create_entity
        self.wiring = ce('Wiring', json=self._json_content('wiring.json'),
                         language=self.wl)
        self.commit()

    def _json_content(self, fname):
        json = loads(open(osp.join(HERE, 'data', fname)).read())
        return unicode(dumps(json))

    def test_valid(self):
        'check a valid definition does not raise ValidationError'
        new_def = loads(self.wiring.json)
        new_def['toto'] = u'titi'
        self.wiring.cw_set(json=unicode(dumps(new_def)))
        self.commit()

    def test_invalid_module_list(self):
        'remove a module used by the wiring def and check ValidationError'
        wldef = loads(self.wl.json)
        del wldef['modules'][0]
        with self.assertRaises(ValidationError) as cm:
            self.wl.cw_set(json=unicode(dumps(wldef)))
            self.commit()
        self.rollback()
        self.assertTrue('Invalid WiringLanguage change' in str(cm.exception))

    def test_invalid_module_definition(self):
        'change a container def used by the wiring and check ValidationError'
        wldef = loads(self.wl.json)
        wldef['modules'][0]['container']['title'] = u'changed_title'
        with self.assertRaises(ValidationError) as cm:
            self.wl.cw_set(json=unicode(dumps(wldef)))
            self.commit()
        self.rollback()
        self.assertTrue('Invalid WiringLanguage change' in str(cm.exception))

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
