def setupVarious(context):
    """ Install plone.app.iterate if its not installed already """

    if context.readDataFile('ilrt.formalworkflow_various.txt') is None:
        return

    from Products.CMFCore.utils import getToolByName
    portal = context.getSite()
    qi_tool = getToolByName(portal, 'portal_quickinstaller')
    if not qi_tool.isProductInstalled('plone.app.iterate'):
        qi_tool.installProduct('plone.app.iterate', swallowExceptions=1)

        # Need to reinstall the formalworkflow zcml so that its
        # browser/configure.zcml overrides iterates one ... 
        from Products.Five import zcml
        import ilrt.formalworkflow
        zcml.load_config('configure.zcml', ilrt.formalworkflow)
        # Now need to rerun the generic setup steps overridden by iterate
        gsetup = getToolByName(portal, 'portal_setup')
        gsetup.manage_importSelectedSteps(context_id='profile-ilrt.formalworkflow:formalworkflow',
                                              ids=['actions','workflow'],
                                              run_dependencies=True)

    

