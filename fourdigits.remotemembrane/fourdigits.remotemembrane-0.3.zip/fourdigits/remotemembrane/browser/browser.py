from Products.Five import BrowserView
from fourdigits.remotemembrane.plugins.usermanager import \
                                RemoteMembraneUserManager

from fourdigits.remotemembrane.plugins.groupmanager import \
                                RemoteMembraneGroupManager

from fourdigits.remotemembrane.plugins.rolemanager import \
                                RemoteMembraneRoleManager

from fourdigits.remotemembrane.plugins.propertymanager import \
                                RemoteMembranePropertyManager

from fourdigits.remotemembrane.plugins.userfactory import \
                                RemoteMembraneUserFactory


class RemoteMembraneUserManagerAddView(BrowserView):
    def __call__(self, add_input_name='', portal_id='', submit_add=''):
        if submit_add:
            obj = RemoteMembraneUserManager(add_input_name, portal_id)
            self.context.add(obj)
            self.request.response.redirect(self.context.nextURL())
            return ''
        return self.index()


class RemoteMembraneGroupManagerAddView(BrowserView):
    def __call__(self, add_input_name='', portal_id='', submit_add=''):
        if submit_add:
            obj = RemoteMembraneGroupManager(add_input_name, portal_id)
            self.context.add(obj)
            self.request.response.redirect(self.context.nextURL())
            return ''
        return self.index()


class RemoteMembraneRoleManagerAddView(BrowserView):
    def __call__(self, add_input_name='', portal_id='', submit_add=''):
        if submit_add:
            obj = RemoteMembraneRoleManager(add_input_name, portal_id)
            self.context.add(obj)
            self.request.response.redirect(self.context.nextURL())
            return ''
        return self.index()


class RemoteMembranePropertyManagerAddView(BrowserView):
    def __call__(self, add_input_name='', portal_id='', submit_add=''):
        if submit_add:
            obj = RemoteMembranePropertyManager(add_input_name, portal_id)
            self.context.add(obj)
            self.request.response.redirect(self.context.nextURL())
            return ''
        return self.index()


class RemoteMembraneUserFactoryAddView(BrowserView):
    def __call__(self, add_input_name='', portal_id='', submit_add=''):
        if submit_add:
            obj = RemoteMembraneUserFactory(add_input_name, portal_id)
            self.context.add(obj)
            self.request.response.redirect(self.context.nextURL())
            return ''
        return self.index()
