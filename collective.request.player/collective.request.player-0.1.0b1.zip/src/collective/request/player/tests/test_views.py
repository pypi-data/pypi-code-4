""" It tests views.py """

import os
import unittest2 as unittest

from plone.app.testing import login, logout

import transaction
from Products.CMFCore.utils import getToolByName
from Products.Five.utilities.marker import mark
from zope.component import getMultiAdapter


from collective.request.player.utils import load
from collective.request.player.interfaces import ICollectiveRequestPlayer
from collective.request.player.testing import\
    COLLECTIVE_REQUEST_PLAYER_FUNCTIONAL


# If you want to write one more request log for testing, you have to add extra info
# to request:
# 1.) "checked_request":true
# 2.) "user":"ploneuser"
# See examples in the 'logs' folder.
LOGS_PATH = os.path.join(os.path.dirname(__file__), 'logs')

# If you want to change USER_NAME, you have to change it in the logs too.
USER_NAME = 'ploneuser'


def open_log_file(logfile):
    return open(os.path.join(LOGS_PATH, logfile))


class TestRequestsPlayer(unittest.TestCase):

    layer = COLLECTIVE_REQUEST_PLAYER_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.request = self.layer['request']
        # create user
        acl_users = getToolByName(self.portal, 'acl_users')
        acl_users.userFolderAddUser('ploneuser', 'secret', ['Manager'], [])
        # apply changes
        transaction.commit()
        # this marking is not temporary
        # details: http://developer.plone.org/components/interfaces.html#id13
        mark(self.request, ICollectiveRequestPlayer)

    def replay(self, logname):
        """ Replay the log file and store changes """
        logs = load(open_log_file(logname))
        self.request.form['requests'] = logs
        # replay the request
        player = getMultiAdapter((self.portal, self.request), name='requests_player')
        response = player.playRequests()
        # apply request
        transaction.commit()
        return response

    def test_createPage(self):
        """ Create document (POST request) """
        self.replay('create_page.json')
        # a player had to create the document ('page')
        self.assertTrue('page' in self.portal)
        # check the owner
        owner_info = self.portal['page'].owner_info()
        self.assertEqual(owner_info['id'], USER_NAME)

    def test_deleteFolder(self):
        """ Delete the plone folder (POST request) """
        # create folder
        login(self.portal, USER_NAME)
        folder_id = self.portal.invokeFactory('Folder', 'folder1', title=u"Folder1")
        transaction.commit()
        logout()

        # replay the request
        self.replay('delete_folder.json')
        # a player had to delete the folder (folder1)
        self.assertFalse(folder_id in self.portal)

    def test_welcomePage(self):
        """ Test the GET request """
        logs = load(open_log_file('welcom_page.json'))
        self.request.form['requests'] = logs
        # replay the request
        player = getMultiAdapter((self.portal, self.request), name='requests_player')
        response = player.playRequests()
        self.assertTrue("There are currently no active content rules" in response)
