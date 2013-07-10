
from OFS.interfaces import IFolder
from zope.interface import implements, alsoProvides
from zope.component import adapts
from redturtle.custommenu.factories.interfaces import ICustomFactoryMenuProvider
from redturtle.custommenu.factories.adapters.adapters import MenuCoreAdapter

class ISpecialFolder(IFolder):
    pass

class SpecialFolderFactoryMenuAdapter(MenuCoreAdapter):
    implements(ICustomFactoryMenuProvider)
    adapts(ISpecialFolder)
    
    def getMenuCustomization(self, data, results):
        return [{'title'       : 'Hello!',
                 'description' : 'Whatever data you enter, you will always see this',
                 'action'      : self.context.absolute_url(),
                 'selected'    : False,
                 'icon'        : '',
                 'submenu'     : None,
                 'extra'       : {'separator': None, 'id': 'dummy', 'class': ''},
                }]

