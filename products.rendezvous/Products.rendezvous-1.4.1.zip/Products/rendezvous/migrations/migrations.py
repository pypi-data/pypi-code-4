from Products.CMFCore.utils import getToolByName

def v120(context):
    tool = getToolByName(context, "portal_setup")
    tool.runAllImportStepsFromProfile(
                "profile-Products.rendezvous.migrations:v120",
                purge_old=False)
