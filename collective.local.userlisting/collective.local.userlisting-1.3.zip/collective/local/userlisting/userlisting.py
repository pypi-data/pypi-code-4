from zope.i18nmessageid import MessageFactory

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.local.userlisting.interfaces import IUserListingAvailable
from collective.local.userlisting import listed_users_with_local_role


PMF = MessageFactory('plone')

class Expressions(BrowserView):

    def userlisting_available(self):
        return IUserListingAvailable.providedBy(self.context)


class View(BrowserView):

    def users_by_role(self):
        """a list of dictionnaries
            {'role': message,
             'users': list of users}
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        site_properties = getToolByName(self.context, 'portal_properties').site_properties
        site_url = portal.absolute_url()
        infos = []

        for role in site_properties.userlisting_roles:
            users = listed_users_with_local_role(self.context, role,
                                                 include_global_role=False)
            if len(users) == 0:
                continue

            role_infos = {'role': PMF(role)}
            role_infos['users'] = []
            for user in users:
                user_id = user.getUserName()
                user_infos = {'id': user_id,
                              'fullname': user.getProperty('fullname') or user_id,
                              'home': "%s/author/%s" % (site_url, user_id),
                              'email': user.getProperty('email'),
                              }
                role_infos['users'].append(user_infos)

            infos.append(role_infos)

        return infos