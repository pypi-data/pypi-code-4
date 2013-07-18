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

import base64

from logilab.common.registry import objectify_predicate

from cubicweb.web.views import authentication, actions, basecontrollers

from cubes.trustedauth.cryptutils import build_cypher

# web authentication info retreiver ############################################

class XRemoteUserRetriever(authentication.WebAuthInfoRetreiver):
    """ authenticate by the x-remote-user http header """
    __regid__ = 'x-remote-user'
    order = 0

    def authentication_information(self, req):
        """retrieve authentication information from the given request, raise
        NoAuthInfo if expected information is not found
        return login crypted with secret shared key
        """
        self.debug('web authenticator building auth info')
        try:
            login = req.get_header('x-remote-user', None)
            self.debug('encoding info for %s', login)
            _secret = self._cw.config._secret
            cyphr = build_cypher(_secret)
            # need a multiple of 16 in length
            secret = cyphr.encrypt('%128s' % login)
            return login, {'secret': base64.encodestring(secret)}
        except Exception, exc:
            self.debug('web authenticator failed (%s)', exc)
            raise authentication.NoAuthInfo()

    def authenticated(self, retriever, req, cnx, login, authinfo):
        """callback when return authentication information have opened a
        repository connection successfully. Take care req has no session
        attached yet, hence req.execute isn't available.

        Here we set a flag on the request to indicate that the user is
        _only_ kerberos authenticated (since cookie login can kick in
        if needed)
        """
        self.debug('web authenticator running post authentication callback')
        cnx.trusted_cwuser = 'password' not in authinfo

    def request_has_auth_info(self, req):
        try:
            login, realm = req.get_header('x-remote-user', None)
        except Exception:
            return False
        return True

    def revalidate_login(self, req):
        try:
            login, realm = req.get_header('x-remote-user', None)
        except Exception:
            return None
        return login

@objectify_predicate
def trust_authenticated(cls, req, rset=None, **kwargs):
    return int(getattr(req.cnx, 'trusted_cwuser', False))


class LogoutController(basecontrollers.LogoutController):

    def goto_url(self):
        """ do NOT redirect to an http:// url """
        msg = self._cw.__('you have been logged out')
        return self._cw.build_url('view', vid='index', __message=msg)

def registration_callback(vreg):
    actions.LogoutAction.__select__ = actions.LogoutAction.__select__ & ~trust_authenticated()
    vreg.register_and_replace(LogoutController, basecontrollers.LogoutController)
    vreg.register(XRemoteUserRetriever)
