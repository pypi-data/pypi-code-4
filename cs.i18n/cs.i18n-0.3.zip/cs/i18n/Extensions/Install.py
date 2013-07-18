import transaction
from Products.CMFCore.utils import getToolByName

PRODUCT_DEPENDENCIES = ('plone.browserlayer'
                        #'LinguaPlone',
                        )
EXTENSION_PROFILES = ('plone.browserlayer:default',
                      'cs.i18n:default',
                      #'Products.LinguaPlone:LinguaPlone',
                      )


def install(self, reinstall=False):
    qi = getToolByName(self, 'portal_quickinstaller')
    ps = getToolByName(self, 'portal_setup')
    
    for product in PRODUCT_DEPENDENCIES:
        if reinstall and q.isProductInstalled(product):
            qi.reinstallProducts([product])
            transaction.savepoint()
        elif not qi.isProductInstalled(product):
            qi.installProducts([product])
            transaction.savepoint()

    for extension_id in EXTENSION_PROFILES:
        ps.runAllImportStepsFromProfile('profile-%s' % extension_id,
                                        purge_old=False)
        product_name = extension_id.split(':')[0]
        qi.notifyInstalled(product_name)
        transaction.savepoint()
