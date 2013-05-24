from Products.CMFCore.utils import getToolByName
from ftw.topics.behavior import ITopicSupportSchema
from ftw.topics.testing import EXAMPLE_CONTENT_DEFAULT_FUNCTIONAL
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.dexterity.fti import DexterityFTI
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
import transaction


class TestTopicSupportBehavior(TestCase):

    layer = EXAMPLE_CONTENT_DEFAULT_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        portal_types = getToolByName(self.portal, 'portal_types')

        fti = DexterityFTI('DxTopicSupport')
        fti.behaviors = (
            'plone.app.dexterity.behaviors.metadata.IBasic',
            'plone.app.content.interfaces.INameFromTitle',
            'ftw.topics.behavior.ITopicSupportSchema',)
        portal_types._setObject('DxTopicSupport', fti)
        fti.lookupSchema()

        transaction.commit()

        self.browser = Browser(self.layer['app'])
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
                TEST_USER_NAME, TEST_USER_PASSWORD,))
        self.browser.handleErrors = False

    def test_behavior(self):
        self.browser.open(self.portal.portal_url() + '/++add++DxTopicSupport')
        query_field_name = 'form.widgets.ITopicSupportSchema.topics.widgets.query'
        search_name = 'form.widgets.ITopicSupportSchema.topics.buttons.search'

        self.browser.getControl(label='Title').value = 'My Object'
        self.browser.getControl(name=query_field_name).value = 'qualit'
        self.browser.getControl(name=search_name).click()
        self.browser.getControl(label='Quality').selected = True
        self.browser.getControl(label='Save').click()

        obj = self.portal.get('my-object')
        topic_support = ITopicSupportSchema(obj)

        agile = self.portal.get('topics').get('manufacturing').get(
            'quality')

        self.assertEqual(topic_support.topics, [IUUID(agile)])
