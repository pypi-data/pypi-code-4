#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

from zope.interface import Interface

class IConversionView(Interface):
    """ Interface to be used through a named utility
        for providing additional conversion views
        to Produce & Publish.
    """

    def __call__():
        """ returns a dict(
                'tab_title' : <title of tab>,
                'tab_content' : <html tab snippet>
            )
        """
