from zope.annotation.interfaces import IAnnotations
from BTrees.OIBTree import OIBTree
from Products.CMFCore.utils import getToolByName


# The name of the annotation fields, namespaces so
# we can avoid conflicts
dusers = 'c2.app.downloaduser.dusers'


def setupAnnotations(context):
    """
    set up the annotations if they haven't been set up
    already. The rest of the functions in here assume that
    this has already been set up
    """
    annotations = IAnnotations(context)

    if not dusers in annotations:
        annotations[dusers] = OIBTree()

    return annotations


def downloadIt(context, userid=None):
    """
    Download an item (context). If no user id is passed in, the logged in User
    will be used. If the user has already downloaded the item, remove the record.
    """
    # annotations = IAnnotations(context)
    annotations = setupAnnotations(context)
    action = None

    if not userid:
        mtool = getToolByName(context, 'portal_membership')
        userid = mtool.getAuthenticatedMember().id

    if userid in annotations[dusers]:
        action = "already"
    else:
        annotations[dusers][userid] = 1
        action = "download"

    return action


def getTally(context):
    """
    Return a dictionary of total download
    """
    setupAnnotations(context)
    annotations = IAnnotations(context)
    return {
            'count': len(annotations[dusers]),
            'mine': getMyDownload(context),
            'download_users' : get_download_users(context),
            }


def getMyDownload(context, userid=None):
    """
    If the user download this item, then return 1.
    If they didn't download: 0.

    If no user is passed in, the logged in user will be returned
    """
    annotations = IAnnotations(context)

    if not userid:
        mtool = getToolByName(context, 'portal_membership')
        userid = mtool.getAuthenticatedMember().id

    if userid in annotations[dusers]:
        return 1

    return 0


def get_download_users(context):
    annotations = IAnnotations(context)
    if dusers in annotations:
        return list(annotations[dusers].keys())
    return []

