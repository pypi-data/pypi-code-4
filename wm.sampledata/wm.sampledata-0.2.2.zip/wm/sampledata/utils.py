from zExceptions import BadRequest
from DateTime.DateTime import DateTime
from zope.component._api import getUtility, getMultiAdapter, queryMultiAdapter
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping,\
    ILocalPortletAssignmentManager, IPortletAssignmentSettings
from zope.container.interfaces import INameChooser
from Products.CMFPlone.utils import safe_unicode, _createObjectByType
import datetime
import os
from zope import event
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from types import ListType
from images import _getImage, _getRandomImage
from plone.portlets.constants import GROUP_CATEGORY, CONTENT_TYPE_CATEGORY,\
    CONTEXT_CATEGORY

getImage = _getImage 
getRandomImage = _getRandomImage

IPSUM_LINE = "Lorem ipsum mel augue antiopam te. Invidunt constituto accommodare ius cu. Et cum solum liber doming, mel eu quem modus, sea probo putant ex."

IPSUM_PARAGRAPH = "<p>" + 10*IPSUM_LINE + "</p>"




def getFile(module, *path):
    """return the file located in module.
    if module is None, treat path as absolut path
    path can be ['directories','and','file.txt'] or just 'file.txt'
    """
    modPath = ''
    if module:
        modPath = os.path.dirname(module.__file__)

    if type(path)==str:
        path = [path]
    filePath = os.path.join(modPath, *path)
    return file(filePath)

def getFileContent(module, *path):
    f = getFile(module, *path)
    data =  safe_unicode(f.read())
    f.close()
    return data



def deleteItems(folder, *ids):
    """delete items in a folder and don't complain if they do not exist.
    """
    for itemId in ids:
        try:
            folder.manage_delObjects([itemId])
        except BadRequest:
            pass
        except AttributeError:
            pass

def todayPlusDays(nrDays = 0, zopeDateTime=False):
    today = datetime.date.today()
    date =  today + datetime.timedelta(days = nrDays)
    if zopeDateTime:
        return DateTime(date.isoformat())
    else:
        return date


def eventAndReindex(*objects):
    """fires an objectinitialized event and
    reindexes the object(s) after creation so it can be found in the catalog
    """
    for obj in objects:
        event.notify(ObjectInitializedEvent(obj))
        obj.reindexObject()



def workflowAds(home, wfdefs):
    """
    do workflow transitions and set enddate to datetime if set.

    sample format
    wfdefs = [('plone-dev', ['publish'], None),
              ('minimal-job', ['submit'], datetime),
              ('plone-dev', ['publish']),
              ]
    """


    wft = getToolByName(home, 'portal_workflow')

    for id, actions, date in wfdefs:
        ad = home.unrestrictedTraverse(id)
        for action in actions:
            wft.doActionFor(ad, action)
        if date:
            ad.expirationDate = date
        ad.reindexObject(idxs=['end', 'review_state'])


def addPortlet(context, columnName='plone.leftcolumn', assignment=None):
    if not assignment:
        return
    column = getUtility(IPortletManager, columnName)
    manager = getMultiAdapter((context, column),IPortletAssignmentMapping)
    chooser = INameChooser(manager)
    manager[chooser.chooseName(None, assignment)] = assignment

def removePortlet(context, portletName, columnName='plone.leftcolumn'):
    manager = getUtility(IPortletManager, columnName)
    assignmentMapping = getMultiAdapter((context, manager),IPortletAssignmentMapping)
    # throws a keyerror if the portlet does not exist
    del assignmentMapping[portletName]

def blockPortlets(context, columnName='plone.leftcolumn', inherited=None, group=None, contenttype=None):
    """True will block portlets, False will show them, None will skip settings.
    """

    manager = getUtility(IPortletManager, name=columnName)
    assignable = getMultiAdapter((context, manager), ILocalPortletAssignmentManager)
    
    if group is not None:
        assignable.setBlacklistStatus(GROUP_CATEGORY, group)
    if contenttype is not None:
        assignable.setBlacklistStatus(CONTENT_TYPE_CATEGORY, contenttype)
    if inherited is not None:
        assignable.setBlacklistStatus(CONTEXT_CATEGORY, inherited)
        
    
def hidePortlet(context, portletName, columnName='plone.leftcolumn'):
    manager = getUtility(IPortletManager, columnName)
    assignmentMapping = getMultiAdapter((context, manager),IPortletAssignmentMapping)
    settings = IPortletAssignmentSettings(assignmentMapping[portletName])
    settings['visible'] = False



def hasPortlet(context, portletName, columnName='plone.leftcolumn'):
    manager = getUtility(IPortletManager, columnName)
    assignmentMapping = getMultiAdapter((context, manager),IPortletAssignmentMapping)
    return assignmentMapping.has_key(portletName)

def setPortletWeight(portlet, weight):
    """if collective weightedportlets can be imported
    we do set the weight, and do not do anything otherwise
    """
    try:
        from collective.weightedportlets import ATTR
        from persistent.dict import PersistentDict
        if not hasattr(portlet, ATTR):
            setattr(portlet, ATTR, PersistentDict())
        getattr(portlet, ATTR)['weight'] = weight
    except ImportError:
        #simply don't do anything in here
        pass






def createImage(context, id, file, title='', description=''):
    """create an image and return the object
    """
    _createObjectByType('Image', context, id, title=title,
                        description=description)
    context[id].setImage(file)
    return context[id]

def excludeFromNavigation(obj, exclude=True):
    """excludes the given obj from navigation
    make sure to reindex the object afterwards to make the
    navigation portlet notice the change
    """

    obj._md['excludeFromNav'] = exclude

def getRelativePortalPath(context):
    """return the path of the plonesite
    """
    url = getToolByName(context, 'portal_url')
    return url.getPortalPath()

def getRelativeContentPath(obj):
    """return the path of the object
    """
    url = getToolByName(obj, 'portal_url')
    return '/'.join(url.getRelativeContentPath(obj))


def doWorkflowTransition(obj, transition):
    """to the workflow transition on the specified object
    """
    wft = getToolByName(obj, 'portal_workflow')
    wft.doActionFor(obj, transition)

def doWorkflowTransitions(objects=[], transition='publish', includeChildren=False):
    """use this to publish a/some folder(s) optionally including their child elements
    """

    if not objects:
        return
    if type(objects) != ListType:
        objects = [objects,]

    utils = getToolByName(objects[0], 'plone_utils')
    for obj in objects:
        path='/'.join(obj.getPhysicalPath())
        utils.transitionObjectsByPaths(workflow_action=transition, paths=[path], include_children=includeChildren)


def constrainTypes(obj, allowed=[], notImmediate=[]):
    """sets allowed and immediately addable types for obj.

    to only allow news and images and make both immediately addable use::

       constrainTypes(portal.newsfolder, ['News Item', 'Image'])

    if images should not be immediately addable you would use::

       constrainTypes(portal.newsfolder, ['News Item', 'Image'], notImmediate=['Image'])
    """

    obj.setConstrainTypesMode(1)
    obj.setLocallyAllowedTypes(allowed)

    if notImmediate:
        immediate = [type for type in allowed if type not in notImmediate]
    else:
        immediate = allowed
    obj.setImmediatelyAddableTypes(immediate)

