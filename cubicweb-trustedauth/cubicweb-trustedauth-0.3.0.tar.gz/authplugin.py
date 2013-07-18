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

"""plugin authentication retriever

:organization: Logilab
:copyright: 2010-2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

__docformat__ = "restructuredtext en"

import os.path as osp
import base64

from cubicweb import AuthenticationError
from cubicweb.server.sources import native

from cubes.trustedauth.cryptutils import build_cypher

class XRemoteUserAuthentifier(native.BaseAuthentifier):
    """ a source authentifier plugin
    login comes encrypted + base64 encoded
    we decrypt it with a special key to identify
    the trustfulness of the `client` (pyro, web)
    """
    auth_rql = ('Any X WHERE X is CWUser, X login %(login)s')

    def authenticate(self, session, login, **kwargs):
        """return CWUser eid for the given login (coming from x-remote-user
        http headers) if this account is defined in this source,
        else raise `AuthenticationError`
        """
        session.debug('authentication by %s', self.__class__.__name__)
        try:
            _secret = session.vreg.config._secret
            cyphr = build_cypher(_secret)
            clearlogin = cyphr.decrypt(base64.decodestring(kwargs.get('secret'))).strip()
            if clearlogin != login:
                raise AuthenticationError('wrong user secret')
            rset = session.execute(self.auth_rql, {'login': clearlogin})
            return rset[0][0]
        except Exception, exc:
            session.debug('authentication failure (%s)', exc)
            pass
        raise AuthenticationError('user is not registered')
