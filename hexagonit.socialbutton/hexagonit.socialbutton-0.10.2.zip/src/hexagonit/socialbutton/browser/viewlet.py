from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import SpecialUser
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from hexagonit.socialbutton.data import SocialButtonConfig
from hexagonit.socialbutton.interfaces import ISocialButtonHidden
from plone.app.layout.viewlets.common import ViewletBase
from plone.registry.interfaces import IRegistry
from plone.stringinterp.interfaces import IStringInterpolator
from zope.component import getUtility


class anonymous_access(object):
    """ Context anonymous to use like this:
    with anonymous_access(request):
        do_something()
    """

    def __init__(self, request, roles=('Anonymous', )):
        self.request = request
        self._roles = roles

    def __enter__(self):
        self.real_sm = getSecurityManager()
        newSecurityManager(
            self.request,
            SpecialUser('Anonymous User', '', self._roles, [])
        )
        return self.real_sm

    def __exit__(self, exc_type, exc_value, traceback):
        setSecurityManager(self.real_sm)


class SocialButtonsViewlet(ViewletBase):

    index = ViewPageTemplateFile('viewlets/social-buttons.pt')

    def _normalize(self, value):
        """Normalize and make it list."""
        if value:
            return [l.strip() for l in value.strip().splitlines() if l.strip()]

    def manager_name(self):
        return self.manager.__name__.replace('.', '-')

    def buttons(self):
        keys = []
        if ISocialButtonHidden.providedBy(self.context):
            return keys
        registry = getUtility(IRegistry)
        items = registry['hexagonit.socialbutton.config']
        types = getToolByName(self.context, 'portal_types')
        for key in items:
            data = SocialButtonConfig(str(key), **items[key])
            typeinfo = types.getTypeInfo(self.context)
            if typeinfo and u'*' not in data.content_types and typeinfo.id not in data.content_types:
                continue
            if not data.enabled:
                continue
            if u'*' not in self._normalize(data.view_models) and self.context.getLayout() not in self._normalize(data.view_models):
                continue
            if self.manager.__name__ not in self._normalize(data.viewlet_manager):
                continue
            with anonymous_access(self.request):
                if data.view_permission_only and not getSecurityManager().checkPermission('View', self):
                    continue
            keys.append(key)
        return keys

    def items(self):
        registry = getUtility(IRegistry)
        items = registry['hexagonit.socialbutton.codes']
        res = []
        for key in self.buttons():
            item = {'code_id': key}
            code_text = items[key]['code_text']
            item['code_text'] = IStringInterpolator(self.context)(code_text)
            res.append(item)
        return res
