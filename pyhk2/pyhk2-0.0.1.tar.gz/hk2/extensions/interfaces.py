from hk2.types import interface, enum

#===========================================================

@interface
class IPluginManager(object):
    """ Plugin management system """
    
    def plugins(self):
        """ Plug-in dict by name """
    
    def extensionPoints(self):
        """ Extension point dict by name """
    
    def createInstance(self, extension):
        """ Creates extension class instance """
    
    def start(self):
        """ Fires up the hk2::start_listeners extension point """

#===========================================================

class IPlugin(object):
    """ Base interface for all plug-ins """
    
    def init(self, plugin_manager, shadow):
        """ Initializes the plugin """

#===========================================================

@interface
class IExtensionPoint(object):
    """ Extension point all plug-ins can extend """
    
    def plugin(self):
        """ Returns plug-in shadow of provider """
    
    def name(self):
        """ Returns name of this extension point """
    
    def fullName(self):
        """ Full name in format plugin_name::ep_name """
    
    def interfaceName(self):
        """ Returns name of interface type that all extenders should implement """
    
    def parameters(self):
        """ Returns dictionary of parameters expected by EP """
    
    def extensions(self):
        """ Returns the list of extensions """

#===========================================================

@interface
class IExtension(object):
    """ Extension objects binds extension point
    that is being extended, plug-in that provides an
    extension, and a class that implements point's interface """
    
    def plugin(self):
        """ Plug-in shadow that provides extension """
    
    def extensionPoint(self):
        """ Extension point that is being extended """
    
    def className(self):
        """ Name of the implementation class """
    
    def parameters(self):
        """ Parameter dictionary """

#===========================================================

@interface
class IPluginShadow(object):
    """ Plugin shadow is a proxy object
        it holds all meta-info about plug-in, exported classes,
        extension points it extends and provides """
    
    def name(self):
        """ Returns name of the plug-in """
    
    def path(self):
        """ Package path or URL of plugin """
    
    def description(self):
        """ Short description of plug-in """
    
    def author(self):
        """ Plug-in author name """
    
    def version(self):
        """ Returns plug-in version """
    
    def getExtensionPoint(self, shortName):
        """ Searches extension point by short name """
    
    def extensionPoints(self):
        """ Returns list of extension points it provides """
    
    def extensions(self):
        """ List of provided extensions """

#===========================================================

@enum
class ExtParamConstraint:
    (Optional, Mandatory) = range(2)

#===========================================================

@interface
class IPluginScanner(object):
    def scan(self):
        """ Should return list of found plugin shadows """
    
    def getType(self, shadow, typeName):
        """ Should load related module and return specified (module, type) tuple """

#===========================================================

@interface
class IServiceRegistry(object):
    ''' Simplifies operations on service plugins '''
    
    def GetService(self, interface):
        ''' Returns service instance '''

#===========================================================

class PluginBase(IPlugin):
    """ Basic implementation of IPlugin interface """
    
    def init(self, shadow, plugin_manager):
        self.shadow = shadow
        self.manager = plugin_manager

#===========================================================
# Extension points
#===========================================================

@interface
class IStartListener(object):
    """ Interface for 'hk2::start_listeners' EP """
    
    def start(self, args=None):
        """ Signals execution start """

#===========================================================

