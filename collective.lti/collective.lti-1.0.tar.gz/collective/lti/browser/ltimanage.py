from zope.interface import Interface
from zope.schema import Text, TextLine
from plone.app.form.base import AddForm
from zope.formlib.form import FormFields, action
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.lti import ltiMessageFactory as _

from urlparse import urljoin
import string
import random
import time


secret_chars = string.ascii_uppercase + string.digits


class ILtiManageForm(Interface):
    '''
    LTI management form
    '''

    launchKey = TextLine(title=_(u'Domain'),
                         description=_(u'Enter the domain of the site that '
                                       'you will launch from that can be used '
                                       'to make a unique launch key.'),
                         required=True)

    contactName = TextLine(title=_(u'Contact Name'),
                           description=_(u'Tell us who you are, in case we '
                                         'need to contact you about the '
                                         'launch point.'),
                           required=False)

    contactEmail = TextLine(title=_(u'Contact Email'),
                            description=_(u'Tell us how we can get in '
                                          'contact with you.'),
                            required=False)

    description = Text(title=_(u'Description'),
                       description=_(u'Tell us how you plan to use the '
                                     'LTI launch point in your application.'),
                       required=False)
                       

class LtiManageForm(AddForm):
    '''
    Form for managing LTI Launch configurations
    '''

    form_fields = FormFields(ILtiManageForm)
    label = _(u'LTI Export')
    description = _(u'Create or manage your LTI launch configurations')
    results = ViewPageTemplateFile('ltimanageresults.pt')

    @action(_(u'Create Launch Parameters'),
            name=u'Create Launch Parameters')
    def createLaunch(self, action, data):
        '''
        Create an LTI launch point with configuration
        '''
        purl = getToolByName(self.context, 'portal_url')
        site = purl.getPortalObject()
        cfgs = site.lticonfigs

        # Get configuration settings
        self.launchKey = data['launchKey'] + '.' + str(time.time())
        self.secret = self.createSecret()
        self.ltiLaunchUrl = urljoin(self.request.getURL(), 'ltilaunch')
        self.ltiConfigUrl = urljoin(self.request.getURL(), 'lticonfig')
        cname = data.get('contactName')
        cemail = data.get('contactEmail')
        descr = data.get('description')

        # Create the launch params
        _createObjectByType('LtiLaunchParams', 
                            cfgs, 
                            id=self.launchKey)
        lp = getattr(cfgs, self.launchKey)
        lp.setTitle(self.launchKey)
        lp.setSecret(self.secret)
        lp.setLtiLaunchUrl(self.ltiLaunchUrl)
        lp.setLtiConfigUrl(self.ltiConfigUrl)
        if cname:
            lp.setLtiContactName(cname)
        if cemail:
            lp.setLtiContactEmail(cemail)
        if descr:
            lp.setDescription(descr)

        # Create status message
        IStatusMessage(self.request).addStatusMessage(
            _(u'LTI Launch Parameters Created.'), type='info')

        # Redirect to launch params view
        return self.results()


    def createSecret(self, size=16):
        '''
        Create a random secret
        '''
        return ''.join(random.choice(secret_chars) for x in range(size))
