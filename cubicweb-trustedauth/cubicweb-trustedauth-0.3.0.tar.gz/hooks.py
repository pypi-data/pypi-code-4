# copyright 2010-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

__docformat__ = "restructuredtext en"
import os.path as osp

from cubicweb.server import hook

from cubes.trustedauth.authplugin import XRemoteUserAuthentifier

class ServerStartupHook(hook.Hook):
    """register authentifier at startup"""
    __regid__ = 'trustedauth.xremoteuserinit'
    events = ('server_startup',)

    def __call__(self):
        # XXX use named args and inner functions to avoid referencing globals
        # which may cause reloading pb
        self.debug('registering trusted authentifier')
        self.repo.system_source.add_authentifier(XRemoteUserAuthentifier())
