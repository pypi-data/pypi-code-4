from Products.PloneTestCase import PloneTestCase
from zope.configuration import xmlconfig
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionCategory

#PloneTestCase.installProduct('SomeProduct')
PloneTestCase.setupPloneSite()

class TestSomething(PloneTestCase.PloneTestCase):

    def _setup_actions(self):
        """ """
        context=self.portal
        self.loginAsPortalOwner()
        tool=context.getAdapter('pa')()

        tool._setObject('root_level', ActionCategory('root_level'))

        root_level=getattr(tool,'root_level')
        root_level._setObject('action_category_level1', ActionCategory('action_category_level1'))
        action_category_level1=getattr(root_level,'action_category_level1')
        action_category_level1.title=u'Action category level1'

        kwargs={}
        kwargs['title']='Action root'
        kwargs['description']='Such an root action'
        kwargs['i18n_domain']='plone'
        kwargs['url_expr']='string:${here/portal_url}/action_root'
        kwargs['link_target']='_self'
        kwargs['available_expr']='python:True'
        kwargs['permissions']='View'
        kwargs['visible']=True

        root_level._setObject('action_root', Action('action_root',**kwargs))
        action_root=getattr(root_level,'action_root')
        action_root.manage_addProperty(id='class_',value='my-class-root',type='string')

        kwargs={}
        kwargs['title']='Action level 1'
        kwargs['description']='Such an level 1 action'
        kwargs['i18n_domain']='plone'
        kwargs['url_expr']='string:${here/portal_url}/action_level1'
        kwargs['link_target']='_blank'
        kwargs['available_expr']='python:True'
        kwargs['permissions']='View'
        kwargs['visible']=True


        action_category_level1._setObject('action_level1', Action('action_level1',**kwargs))
        action_level1=getattr(action_category_level1,'action_level1')

        root_level._setObject('action_category_empty', ActionCategory('action_category_empty'))
        action_category_empty=getattr(root_level,'action_category_empty')
        action_category_empty.title=u'Action category empty'

    def test_actions(self):
        self._setup_actions()
        list_=self.portal.getBrowser('tcbnavbar').get(['root_level'])

        self.assertEqual(len(list_),1)