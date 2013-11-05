import transaction
from collective.lti import ltiMessageFactory as _                               
from Products.CMFPlone.utils import _createObjectByType


def setupDefaultContent(context):
    '''
    Setup default folder for LTI integrations
    '''
    site = context.getSite()

    if context.readDataFile('collective_lti_setup.txt') is None:
        return

    existing = site.objectIds()

    if 'lticonfigs' not in existing:
        title = _(u'lti_config_folder_title', default=u"LTI Configuration")
        ttitle = site.translate(title)
        descr = _(u'help_lti_config_folder', 
                  default=u"A folder for containing LTI configurations")
        tdescr = site.translate(descr)

        _createObjectByType('LaunchFolder',
                            site,
                            id='lticonfigs',
                            title=ttitle,
                            description=tdescr)
        lf = site.get('lticonfigs')
        lf.exclude_from_nav = True
        lf.reindexObject()

    
        

