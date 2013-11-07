'''
MAP Client, a program to generate detailed musculoskeletal models for OpenSim.
    Copyright (C) 2012  University of Auckland
    
This file is part of MAP Client. (http://launchpad.net/mapclient)

    MAP Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MAP Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MAP Client.  If not, see <http://www.gnu.org/licenses/>..
'''
from PySide import QtCore

VERSION_MAJOR = 0
VERSION_MINOR = 10
VERSION_PATCH = 1
VERSION_STRING = str(VERSION_MAJOR) + "." + str(VERSION_MINOR) + "." + str(VERSION_PATCH)
GPL_VERSION = '3'
APPLICATION_NAME = 'MAP Client'
ORGANISATION_NAME = 'Musculo Skeletal'
ORGANISATION_DOMAIN = 'musculoskeletal.org'

DEFAULT_PMR_IPADDRESS = 'teaching.physiomeproject.org'
DEFAULT_CONSUMER_PUBLIC_TOKEN = 'ghRsy25tpMnt36Aj7R_LsxUS'
DEFAULT_CONSUMER_SECRET_TOKEN = '41IgdRjQS1HsO_mq8VN2M2Dg'

# Contributors list
HS = {'name': 'Hugh Sorby', 'email': 'h.sorby@auckland.ac.nz'}

CREDITS = {
           'programming'  : [HS],
           'artwork'      : [HS],
           'documentation': [HS]
           }

ABOUT = {
         'name'       : APPLICATION_NAME,
         'version'    : VERSION_STRING,
         'license'    : 'GNU GPL v.' + GPL_VERSION,
         'description': 'Create and manage detailed musculoskeletal models for OpenSim.'
         }

# APPLICATION
DEFAULT_WORKFLOW_PROJECT_FILENAME = '.workflow.conf'
DEFAULT_WORKFLOW_ANNOTATION_FILENAME = '.workflow.rdf'

class PMRInfo(object):

    def __init__(self):
        self.readSettings()

    def readSettings(self):
        settings = QtCore.QSettings()
        settings.beginGroup('PMR')
        self._ipaddress = settings.value('pmr-website', DEFAULT_PMR_IPADDRESS)
        self._consumer_public_token = settings.value('consumer-public-token', DEFAULT_CONSUMER_PUBLIC_TOKEN)
        self._consumer_secret_token = settings.value('consumer-secret-token', DEFAULT_CONSUMER_SECRET_TOKEN)
        self._user_public_token = settings.value('user-public-token', '')
        self._user_secret_token = settings.value('user-secret-token', '')
        if not self._user_public_token:
            self._user_public_token = None
        if not self._user_secret_token:
            self._user_secret_token = None
        settings.endGroup()

    def writeSettings(self):
        settings = QtCore.QSettings()
        settings.beginGroup('PMR')
        temp_public = ''
        if self._user_public_token:
            temp_public = self._user_public_token
        temp_secret = ''
        if self._user_secret_token:
            temp_secret = self._user_secret_token
        settings.setValue('user-public-token', temp_public)
        settings.setValue('user-secret-token', temp_secret)
        settings.endGroup()

    def ipAddress(self):
        return self._ipaddress

    def consumerPublicToken(self):
        return self._consumer_public_token

    def consumerSecretToken(self):
        return self._consumer_secret_token

    def userPublicToken(self):
        return self._user_public_token

    def userSecretToken(self):
        return self._user_secret_token

    def setUserPublicToken(self, token):
        self._user_public_token = token

    def setUserSecretToken(self, token):
        self._user_secret_token = token




