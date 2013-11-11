# -*- coding: utf-8 -*-

import grokcore.component as grok
from grokcore.content import Container
from dolmen.authentication import (
    IPrincipalFolder, IPasswordChecker, IAccountStatus)
from zope.pluggableauth.interfaces import IAuthenticatorPlugin, IPrincipalInfo


class PrincipalFolderPlugin(Container):
    grok.implements(IAuthenticatorPlugin, IPrincipalFolder)

    title = u""
    
    def getPrincipal(self, id):
        return self.get(id)

    def hasPrincipal(self, id):
        return id in self

    def getAccount(self, id):
        return self.getPrincipal(id)

    def getValidPrincipal(self, login, passwd):
        """Retrieves a principal account and returns a IPrincipalInfo object.
        If no user matches the login or if the password check doesn't work,
        None is returned instead.
        """
        # Retrieving the user
        account = self.getAccount(login)
        if account is None:
            return None

        # Checking the status of the account
        status = IAccountStatus(account, None)
        if status is not None and not status.check():
            return None

        # Checking credentials.
        checker = IPasswordChecker(account, None)
        if checker is None or checker.checkPassword(passwd) is not True:
            return None

        return IPrincipalInfo(account)

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None

        login = credentials.get('login')
        passwd = credentials.get('password')
        if not login or not passwd:
            return None

        # We do not check the validity for known core users.
        if login in ['zope.Anybody', 'zope.Everybody']:
            return None

        return self.getValidPrincipal(login, passwd)

    def principalInfo(self, id):
        account = self.getAccount(id)
        if account is not None:
            return IPrincipalInfo(account)
        return None
