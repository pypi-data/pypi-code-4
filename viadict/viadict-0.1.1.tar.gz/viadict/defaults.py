from Foundation import *
from PyObjCTools.Conversion import *

colFromObjC = lambda x: pythonCollectionFromPropertyList(x)
colToObjC = lambda x: propertyListFromPythonCollection(x)

def GetUserDefaults():
  return NSUserDefaults.standardUserDefaults()

def GetGlobalDomain():
   gd = GetUserDefaults().persistentDomainForName_('Apple Global Domain')
   return NSMutableDictionary(gd)

def GetUserDictPreferences():
  return NSMutableDictionary(GetGlobalDomain()['com.apple.DictionaryServices'])

def SetUserDictPreferences(array):
  '''Well this is referentially transparent /s'''
  pref = GetUserDictPreferences()
  pref['DCSActiveDictionaries'] = array
  pref = NSDictionary(pref)
  g = GetGlobalDomain()
  g.setObject_forKey_(pref, 'com.apple.DictionaryServices')
  GetUserDefaults().setPersistentDomain_forName_(g, 'Apple Global Domain') 

def SwapUserDictPreferences(array):
  previous = colFromObjC(GetUserDictPreferences()['DCSActiveDictionaries'])
  new = SetUserDictPreferences(array)
  return previous
