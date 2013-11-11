# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.publisher.interfaces import IRequest
from zope.pluggableauth.interfaces import (
    IPrincipalInfo, IAuthenticatedPrincipalFactory, IAuthenticatorPlugin)
from zope.principalregistry.principalregistry import principalRegistry


class IPrincipalFromGlobalRegistry(IPrincipalInfo):
    pass


class PrincipalRegistryInfo(object):
    grok.implements(IPrincipalFromGlobalRegistry)

    credentialsPlugin = None
    authenticatorPlugin = None

    def __repr__(self):
        return '<GlobalRegistryPrincipal "%s">' % self.id

    def __init__(self, principal):
        self.id = unicode(principal.id)
        self.title = principal.title
        self.description = principal.description
        self.principal = principal


class PrincipalRegistryFactory(grok.MultiAdapter):
    grok.adapts(IPrincipalFromGlobalRegistry, IRequest)
    grok.provides(IAuthenticatedPrincipalFactory)

    def __init__(self, info, request):
        self.info = info

    def __call__(self, authentication):
        return self.info.principal


class GlobalRegistryAuth(grok.GlobalUtility):
    """An authenticator plugin, that authenticates principals against
    the global principal registry.

    This authenticator does not support own prefixes, because the
    prefix of its principals is already defined in another place
    (site.zcml). Therefore we get and give back IDs as they are.
    """
    grok.name("globalregistry")
    grok.implements(IAuthenticatorPlugin)

    __parent__ = None

    def authenticateCredentials(self, credentials):
        """Return principal info if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        principal = None
        login, password = credentials['login'], credentials['password']
        try:
            principal = principalRegistry.getPrincipalByLogin(login)
        except KeyError:
            return
        if principal and principal.validate(password):
            return PrincipalRegistryInfo(principal)
        return

    def principalInfo(self, id):
        return None
