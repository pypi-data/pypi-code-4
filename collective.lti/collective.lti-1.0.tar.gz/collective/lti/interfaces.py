from zope.interface import Interface


class ILTIBrowserLayer(Interface):
    '''
    Marker interface for browser layer
    '''


class ILaunchFolder(Interface):
    '''
    Marker interface for Folder that contains launch information for LTI
    '''


class ILtiLaunchParams(Interface):
    '''
    Marker interface for LtiLaunchParams content object
    '''


class ILTITransformable(Interface):
    '''
    Marker interface that indicates that a link to an object must use
    the LTI view and not the normal Plone view.
    '''
