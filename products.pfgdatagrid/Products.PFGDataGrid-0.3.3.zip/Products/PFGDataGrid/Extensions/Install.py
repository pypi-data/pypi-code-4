# We install our product by running a GS profile.  We use the old-style
# Install.py module so that our product works w/ the Quick Installer
# in Plone 2.5.x

try:
    from Products.CMFPlone.migrations import v3_0
except ImportError:
    HAS_PLONE30 = False
else:
    HAS_PLONE30 = True

try:
    from plone.app.upgrade import v40
    HAS_PLONE4 = True
except:
    HAS_PLONE4 = False

from Products.CMFCore.utils import getToolByName

from StringIO import StringIO


def install(self):
    """ BBB: Make for a pleasant installation experience in 2.5.x.
        To be removed when eliminating support for < 3.x.
    """
    out = StringIO()

    print >> out, "Installing PFGDataGrid"
    setup_tool = getToolByName(self, 'portal_setup')

    if HAS_PLONE30 or HAS_PLONE4:
        setup_tool.runAllImportStepsFromProfile(
            "profile-Products.PFGDataGrid:default",
            purge_old=False)
    else:
        old_context = setup_tool.getImportContextID()

        # run the standard install process
        setup_tool.setImportContext('profile-Products.PFGDataGrid:default')
        setup_tool.runAllImportSteps()

        setup_tool.setImportContext(old_context)
