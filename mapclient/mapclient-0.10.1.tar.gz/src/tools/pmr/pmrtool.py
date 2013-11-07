'''
Created on Jun 20, 2013

@author: hsorby
'''
import webbrowser

from settings.info import PMRInfo
from tools.pmr.jsonclient.client import Client
from tools.pmr.authoriseapplicationdialog import AuthoriseApplicationDialog

class PMRTool(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._pmrInfo = PMRInfo()
        self._client = Client(self._pmrInfo.ipAddress(),
                              (self._pmrInfo.consumerPublicToken(), self._pmrInfo.consumerSecretToken()),
                              (self._pmrInfo.userPublicToken(), self._pmrInfo.userSecretToken()))
        

    def updateAccess(self):
        user_keys = self._client.access()
        self._pmrInfo.setUserPublicToken(user_keys[0])
        self._pmrInfo.setUserSecretToken(user_keys[1])
        self._pmrInfo.writeSettings()
        
    def hasAccess(self):
        return self._client.hasAccess()
    
    def clearAccess(self):
        self._client.clearAccess()
    
    def search(self, text):
        return self._client.search(text)
        
    def requestTemporaryCredential(self):
        return self._client.requestTemporaryCredential()
    
    def authorizationUrl(self, key):
        return self._client.authorizationUrl(key)
    
    def setPermanentCredential(self, verifier):
        self._client.setPermanentCredential(verifier)
        
    def getDashboard(self):
        return self._client.getDashboard()
        
    def addWorkspace(self, title, description):
        return self._client.addWorkspace(title, description)
        
    def registerWithPMR(self, parent=None):
        oauth_token = self.requestTemporaryCredential()
        url = self.authorizationUrl(oauth_token)
        webbrowser.open(url)
        dlg = AuthoriseApplicationDialog(parent)
        dlg.setModal(True)
        if dlg.exec_():
            if dlg.token():
                self.setPermanentCredential(dlg.token())
                if self.hasAccess():
                    self.updateAccess()
    
    def deregisterWithPMR(self):
        self.clearAccess()
        self.updateAccess()


