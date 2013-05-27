from Products.CMFCore.utils import getToolByName


def cleanup_old_release(context):
    #remove addthis.js and the external javascript from portal_javascript
    jstool = getToolByName(context, 'portal_javascripts')
    jstool.unregisterResource('http://s7.addthis.com/js/250/addthis_widget.js#username=xa-4b7fc6a9319846fd')
    jstool.unregisterResource('http://s7.addthis.com/js/250/addthis_widget.js')
    jstool.unregisterResource('++resource++addthis.js')
    jstool.cookResources()
