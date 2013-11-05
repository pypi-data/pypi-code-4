from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from ims_lti_py.request_validator import RequestValidatorMixin 
from ims_lti_py import ToolProvider, ToolConfig
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.lti import ltiMessageFactory as _


from collective.lti.interfaces import ILTITransformable


class PloneRequestValidatorMixin(RequestValidatorMixin):
    '''
    A mixin class for OAUTH request validation using Plone (for ims_lti_py)
    '''
    def parse_request(self, request, parameters=None, fake_method=None):
        '''
        Parse Plone request
        '''

        # This just gets the parameters from the LTI launch request
        # from a Plone form and returns them
        return (request.method,
                request.getURL(),
                request.environ,
                request.form)
    
     
class PloneToolProvider(PloneRequestValidatorMixin, ToolProvider):
    '''
    OAUTH ToolProvider that works with Plone (for ims_lti_py)
    '''
    pass
                

class LTIToolConfig(BrowserView):
    '''
    Get LTI tool configuraiton in XML format as requested with the 
    correct paramters.
    '''
    
    def __call__(self):
        '''
        Return a valid LTI config in XML
        '''
        lurl = urljoin(self.request.getURL(), 'ltilaunch')
        # Pass the launch URL as the secure launch url for now
        slurl = lurl
        tc = ToolConfig(title=self.context.Title(),
                        description=self.context.Description(),
                        launch_url=lurl,
                        secure_launch_url=slurl)
        # Set public privacy level for canvas
        tc.set_ext_param('canvas.instructure.net', 'privacy_level', 'public')
        self.request.response.setHeader('Content-type', 'text/xml')
        return tc.to_xml()


class LTILaunch(BrowserView):
    '''
    Handle the LTI launch request. Redirect to LTI view of the content
    if successful, or provide an error.
    '''

    error_page = ViewPageTemplateFile('ltierror.pt')


    def __call__(self):
        '''
        Get Content from the object 
        '''

        ckey = self.request.form['oauth_consumer_key']
        secret = self.getSecret(ckey)
        tp = PloneToolProvider(ckey, secret, self.request.form)
        if tp.is_valid_request(self.request):
            return self.request.response.redirect(urljoin(self.request.getURL(), 'lti'))
        else:
            self.errors = [_(u'LTI authentication request failed.')]
            if not secret:
                self.errors.append(_(u'LTI Secret not provided'))
            return self.error_page()


    def getSecret(self, ckey):
        '''
        Get the secret from the LTI launch params with ckey
        '''
        pstate = getMultiAdapter((self.context, self.request), 
                                 name=u'plone_portal_state')
        site = pstate.portal()
        lpath = site.getPhysicalPath() + ('lticonfigs', ckey)
        lp = site.unrestrictedTraverse(lpath)
        if lp:
            return lp.getSecret()

        return ''


class LTIView(BrowserView):
    '''
    View Class for LTI that converts all internal links to LTI
    compatible views on LTI compatible content. Used for viewing 
    content after the tool comsumer and tool producer have 
    authenticated.
    '''

    def getContent(self):
        '''
        Get the contents for the LTI view of the object
        '''
        body =  self.context.getText()
        contents = self.transformText(body)
        return contents


    def transformText(self, body):
        '''
        Transform links to point to LTI view
        '''
        soup = BeautifulSoup(body)
        links = soup.findAll('a')
        for x in links:
            if x.has_key('href') and self.request.base in x['href']:
                if self._lookupLink(x['href']):
                    x['href'] = urljoin(x['href']+'/', 'lti')
        return soup.renderContents()


    def _lookupLink(self, link):
        '''
        Return the type of the object linked to
        '''
        pstate = getMultiAdapter((self.context, self.request), 
                                 name=u'plone_portal_state')
        site = pstate.portal()
        lpath = self.request.physicalPathFromURL(link)
        obj = site.restrictedTraverse(lpath)
        return ILTITransformable.providedBy(obj)
        
