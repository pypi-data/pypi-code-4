from plone.app.iterate.browser.checkin import Checkin as BaseCheckin
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class Checkin(BaseCheckin):
    """ This seems to be the only way to override the template 
        because its set in the base class and so the zcml template directive
        is unusable
    """
    template = ViewPageTemplateFile('checkin.pt')


