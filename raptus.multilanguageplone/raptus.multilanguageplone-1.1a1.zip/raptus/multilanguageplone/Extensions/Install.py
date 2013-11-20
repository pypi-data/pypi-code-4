from Products.CMFCore.utils import getToolByName

from raptus.multilanguageplone.setuphandlers import indexes, _extra, text_extra

def uninstall(portal, reinstall=False):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-raptus.multilanguageplone:uninstall')
    
    if not reinstall:
        catalog = getToolByName(portal, 'portal_catalog')
        for id, new, new_field_name, orig, orig_field_name in indexes:
            if id in catalog.indexes():
                index = catalog._catalog.getIndex(id)
                if not index.__class__.__name__ == orig:
                    catalog.delIndex(id)
            if not id in catalog.indexes():
                extra = _extra()
                if new == 'MultilanguageZCTextIndex':
                    extra = text_extra
                setattr(extra, 'field_name', new_field_name)
                catalog.addIndex(id, orig, extra)
                catalog.reindexIndex(id, portal.REQUEST)
