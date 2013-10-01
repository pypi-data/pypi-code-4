# -*- coding: utf-8 -*-
#
# copyright 2013 Unlish (Montpellier, FRANCE), all rights reserved.
# contact http://www.unlish.com -- mailto:contact@unlish.com
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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-oauth specific hooks and operations."""

from cubicweb.server import hook

from cubes.oauth.authplugin import DirectAuthentifier


class ServerStartupHook(hook.Hook):
    """register authentifier at startup."""

    __regid__ = 'oauth-authentifier-register'
    events = ('server_startup',)
    _negociation_timeout = 300

    def __call__(self):
        self.debug('registering externalauth authentifier')
        self.repo.system_source.add_authentifier(DirectAuthentifier())


        def cleanup_negostates():
            import cubes.oauth.views as oviews

            for negoid in oviews.COLLECT_LIST:
                self.debug('collecting negostate', negoid)
                oviews.NEGOSTATE.pop(negoid, None)
            oviews.COLLECT_LIST[:] = []

            for negoid in oviews.NEGOSTATE:
                oviews.COLLECT_LIST.append(negoid)

        self.repo.looping_task(self._negociation_timeout,
                               cleanup_negostates)
