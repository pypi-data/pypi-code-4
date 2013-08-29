from zope.i18nmessageid import MessageFactory
from Products.CMFCore.permissions import setDefaultRoles

# import monkeys
#from collective.blogging import patch

## LinguaPlone addon?
try:
    from Products.LinguaPlone.public import registerType
except ImportError:
    HAS_LINGUA_PLONE = False
else:
    HAS_LINGUA_PLONE = True
    del registerType

_ = MessageFactory("collective.blogging")

BLOG_PERMISSION = 'collective.blogging: Blog'

SHARING_PROVIDERS = {
    'Del.icio.us'     : {
        'url':'http://del.icio.us/post?url=$url&amp;title=$title',
        'logo':'++resource++collective.blogging.static/delicious.png'
    },
    'Facebook'        : {
        'url':'http://www.facebook.com/share.php?u=$url',
        'logo':'++resource++collective.blogging.static/facebook.png'
    },
    'Google Bookmarks': {
        'url':'http://www.google.com/bookmarks/mark?op=add&bkmk=$url&title=$title',
        'logo':'++resource++collective.blogging.static/google.png'
    },
    'Yahoo Bookmarks' : {
        'url':'http://bookmarks.yahoo.com/toolbar/savebm?opener=tb&amp;u=$url&amp;t=$title',
        'logo':'++resource++collective.blogging.static/yahoo.png'
    },
    'Twitter'         : {
        'url':'http://twitter.com/home?status=$url',
        'logo':'++resource++collective.blogging.static/twitter.png'
    },
    'MySpace'         : {
        'url':'http://www.myspace.com/Modules/PostTo/Pages/?c=$url&amp;t=$title',
        'logo':'++resource++collective.blogging.static/myspace.png'
    },
    'Digg'            : {
        'url':'http://digg.com/submit?phase=2&amp;url=$url&amp;title=$title',
        'logo':'++resource++collective.blogging.static/digg.png'
    },
    'Slashdot'        : {
        'url':'http://slashdot.org/bookmark.pl?title=$title&amp;url=$url',
        'logo':'++resource++collective.blogging.static/slashdot.png'
    },
    'Live'            : {
        'url':'https://favorites.live.com/quickadd.aspx?marklet=1&amp;mkt=en-us&amp;url=$url&amp;title=$title&amp;top=1',
        'logo':'++resource++collective.blogging.static/live.png'
    },
    'LinkedIn'        : {
        'url':'http://www.linkedin.com/shareArticle?mini=true&amp;url=$url&amp;title=$title',
        'logo':'++resource++collective.blogging.static/linkedin.png'
    },
}

def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    setDefaultRoles(BLOG_PERMISSION, ())
