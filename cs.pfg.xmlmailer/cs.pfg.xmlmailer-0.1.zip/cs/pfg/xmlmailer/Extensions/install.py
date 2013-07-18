from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple

def install(self):
    out = StringIO()

    print >>out, 'Installing XMLMailerAdapter'

    tool=getToolByName(self, "portal_setup")

    if getFSVersionTuple()[:3]>=(3,0,0):
        tool.runAllImportStepsFromProfile(
            "profile-cs.pfg.xmlmailer:default",
            purge_old=False)
    else:
        plone_base_profileid = "profile-CMFPlone:plone"
        tool.setImportContext(plone_base_profileid)
        tool.setImportContext("profile-cs.pfg.xmlmailer:default")
        tool.runAllImportSteps(purge_old=False)
        tool.setImportContext(plone_base_profileid)

    print >> out, "Successfully installed XMLMailerAdapter" 

    return out.getvalue()
    
