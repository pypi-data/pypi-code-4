# -*- coding: utf-8 -*-

# imports
import cherrypy
from vispa.controller import AbstractController
from vispa.models.preference import ExtensionPreference
import vispa.rpc
import logging
import collections
import ast
import os


#from vispa.extensions.offline.remote import listOfModules

class AugerOfflineController(AbstractController):

    def __init__(self):
        AbstractController.__init__(self)
        
        self.__logger = logging.getLogger("vispa.extensions.offline")
        print "__init__"
        print __name__
        self.__logger.debug("test")
        
        self.__rpcPool = {} # rpc connection pool
        
        #=======================================================================
        # definition of default preference db values
        #=======================================================================
        
        self.__db_default_config = {
            "moduleConfigObj": {
                "Radio Modules": "standardRdModuleConfig.xml",
                "SD Reconstruction Modules": "standardSdRecModuleConfig.xml",
                "Hybrid Reconstruction Modules": "standardHdRecModuleConfig.xml",
                "SdHAS Modules": "standardSdHASRecModuleConfig.xml",
                "Fd Modules": "standardFdRecModuleConfig.xml"
            },
            "detectorConfigObj": {
                "standardSdRealDetConfig": "standardSdRealDetConfig.xml",
                "standardFdRealDetConfig": "standardFdRealDetConfig.xml",
                "standardRdRealDetConfig": "standardRdRealDetConfig.xml"
           }
        }
      
      
    

    def __getOfflineRpc(self, user, workspace_id):
        workspace_id = int(workspace_id)
        key = (user.id,workspace_id)
        self.__logger.debug("getOfflineRPC(): key = "+str(key))
        print "getOfflineRPC(): key = "+str(key)
        if(self.__rpcPool.has_key(key)):
            self.__logger.debug("key in rpc pool")
            r = self.__rpcPool.get(key)
        else:
            self.__logger.debug("key in not contained in pool... creating new connection")
            workspace = self.get("workspace", workspace_id)
            service = vispa.rpc.get(user, workspace, None)
            r = service.getmodule("vispa.extensions.augeroffline.remote").AugerOfflineRpc(self.__db_default_config)
            self.__rpcPool.update({key:r})
          
        return r
    
    
    ''' converts a unicode dictionary into string dictionary '''
    def __convert_unicode_to_string(self, data):
        if isinstance(data, unicode):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self.__convert_unicode_to_string, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.__convert_unicode_to_string, data))
        else:
            return data
    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def initialize(self):
        self.__logger.debug("initialize()")
        
        json = cherrypy.request.json
        moduleConfig = json[u'moduleConfig']
        detectorConfig = json[u'detectorConfig']
        workspace_id = json[u'workspace_id']
        moduleConfig = self.__convert_unicode_to_string(moduleConfig)
        detectorConfig = self.__convert_unicode_to_string(detectorConfig)
        
        self.__logger.debug("initialize(): "+str(moduleConfig))
        self.__logger.debug("type = "+str(type(moduleConfig)))
        
        # db test
        #db = self.get('db')
        #profile_id = self.get('profile_id')
        #preferences = ExtensionPreference.get_data_by_profile_id(db, profile_id, key='offline-full', parse_json=True)
        #default_preferences = {"foo": "bar"}
        #preferences = preferences or default_preferences
        #print preferences, "\n\n\n"
        # test end
        
        
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        return r.initialize(str(moduleConfig),str(detectorConfig))
    
    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    @cherrypy.tools.json_out()
    def resetAllModuleOptions(self, workspace_id):
        workspace_id = int(workspace_id)
        self.__logger.debug("resetAllModuleOptions")
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        return r.resetAllModuleOptions()
    
    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    @cherrypy.tools.json_out()
    def setAllInfoLevelTo(self, workspace_id, infolevel):
        workspace_id = int(workspace_id)
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        self.__logger.debug("setAllInfoLevelTo "+ infolevel)
        return r.setAllInfoLevelTo(int(infolevel))
    
    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def get_auger_offline_path(self, workspace_id):
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        path = r.get_auger_offline_path()
        self.__logger.debug("offline path = "+ str(path))
        return path
    
    
    #deprecated
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()    
    def getListOfModules(self, workspace_id, category):
        self.__logger.debug("getListOfModule(): category = "+category)
        self.__logger.debug("userid = "+str(cherrypy.request.user.id))
        #      self.__logger.debug("workspace id = ", cherrypy.request.workspace.id)
        
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        self.__logger.debug("rpc connection established")
        
        listOfModules = r.getListOfModules(category)
        
        self.__logger.debug("getListOfRadioModules for category "+ category +"\n"+str(listOfModules))
        
        return self.success({"listOfModules": listOfModules})
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()    
    def get_available_modules(self, workspace_id):
        self.__logger.debug("userid = "+str(cherrypy.request.user.id))
        #      self.__logger.debug("workspace id = ", cherrypy.request.workspace.id)
        
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        self.__logger.debug("rpc connection established")
        
        listOfModules = r.get_available_modules()
        
        
        return self.success({"listOfModules": listOfModules})


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def getModuleOptions(self, workspace_id, moduleName):
        self.__logger.info("getModuleOptions()")
        moduleName = moduleName.strip()
        self.__logger.debug(moduleName)
        
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        
        dictOfOptions = r.getModuleOptions(moduleName)
        
        # catch error codes
        if(type(dictOfOptions) == int):
            return self.success({"dictOfOptions": dictOfOptions})

                      
        dictOfOptions = ast.literal_eval(dictOfOptions)
        return self.success({"dictOfOptions": dictOfOptions})
    
    
    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.json_out()
    @cherrypy.tools.workspace()
    def openBootstrapXML(self, workspace_id, path):
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        object =  r.openBootstrapXML(path)
        
        return self.success(object)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def setModuleOptions(self):
        self.__logger.info("setModuleOptions")
        
        json = cherrypy.request.json
        moduleName = json[u'moduleName'].strip()
        moduleOptions = json[u'moduleOptions']
        workspace_id = json[u'workspace_id']
        self.__logger.debug("moduleName: "+moduleName)
        for moduleOption in moduleOptions:
            self.__logger.debug(moduleOption[0]+" = " + moduleOption[1] +"[" + str(moduleOption[2])+"]")
          
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        
        result = r.setModuleOptions(moduleName, moduleOptions)
        return self.success({"result": result})
      
      
      
        
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def saveModuleSequence(self):
        json = cherrypy.request.json
        moduleSequence = json[u'moduleSequence']
        filepath = json[u'filepath']
        workspace_id = json[u'workspace_id']
        
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        r.setModuleSequence(moduleSequence)
        
        r.saveModuleSequence(filepath)
        
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def setModuleSequence(self):
        json = cherrypy.request.json
        moduleSequence = json[u'moduleSequence']
        workspace_id = json[u'workspace_id']
        
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        r.setModuleSequence(moduleSequence)

        
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def saveBootstrap(self):
        json = cherrypy.request.json
        filepath = json[u'filepath']
        workspace_id = json[u'workspace_id']
        
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        
        r.saveBootstrap(filepath)
        
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def saveXMLFiles(self):
        json = cherrypy.request.json
        workspace_id = json[u'workspace_id']
        input_files = json[u'input_files'].split(",")
        self.__logger.debug("input files: "+str(input_files))
        input_file_type = json[u'input_file_type']
        output_folder = json[u'output_folder']
        filename_bootstrap = json[u'filename_bootstrap']
        filename_modulesequence = json[u'filename_modulesequence']
        filename_eventfilereader = json[u'filename_eventfilereader']
        path_relative = bool(json[u'path_relative'])
        module_sequence = json[u'module_sequence']
        
        filename_bootstrap = os.path.join(output_folder,filename_bootstrap)
        filename_modulesequence = os.path.join(output_folder,filename_modulesequence)
        filename_eventfilereader = os.path.join(output_folder,filename_eventfilereader)
        if(path_relative):
            bootstrap_dirname = os.path.dirname(filename_bootstrap) 
            filename_modulesequence = os.path.relpath(filename_modulesequence,bootstrap_dirname)
            filename_eventfilereader = os.path.relpath(filename_eventfilereader,bootstrap_dirname)
        
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        
        tmp_return = r.saveBootstrap(output_folder, filename_bootstrap, filename_modulesequence, filename_eventfilereader)
        print "return = ", tmp_return
        if(tmp_return != 0):
            if(tmp_return == 1):
                return self.fail("The specified folder(s) does not exist!")
            else:
                return self.fail("An error occurred during saving XML the files!")
        else:
            return self.success("XML files saved correctly.")
            
        r.setModuleSequence(module_sequence)
        r.saveModuleSequence(os.path.join(output_folder, filename_modulesequence))
        r.saveEventFileReader(os.path.join(output_folder, filename_eventfilereader), input_files, input_file_type)
        
        
    @cherrypy.expose
#    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def loadModuleSequence(self, workspace_id, path):
      
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        r.openModuleSequenceXML(path)
        moduleSequence = r.returnModuleSequence()
        
        self.__logger.debug("moduleSequence: "+ str(moduleSequence))
        # catch error codes
        if(type(moduleSequence) == int):
            return moduleSequence
        
              
        return self.success({"moduleSequence": moduleSequence})
      
#    def openModuleSequenceXML(self, path):
#      self.__logger.info("openModuleSequenceXML()")
#      self.__logger.debug("path to modulesquence file: ", path)
#      
#      if(moduleName[0:2] == "Rd"):
#        for child in self.__RdModuleConfigRoot:
#          name = child.attrib.get('id')
#    
#          if(name == moduleName):
#            modulePath = child.attrib.items()[2][1]
#            self.__logger.debug("found module "+ moduleName + " at " + modulePath)
#      
#            moduleOptionsTree = ET.parse(modulePath, self.__parser)
#            moduleOptionsRoot = moduleOptionsTree.getroot()
#      
#            #load validation schema
#            #xmlschema_path = ModuleOptionsRoot.items()[0][1]
#            #xmlschema_doc = ET.parse(xmlschema_path)
#            #print "reading in XSD Schema from ", xmlschema_path
#            #xmlschema = ET.XMLSchema(xmlschema_doc)
#            #xmlschema.validate(ModuleOptionsTree)
#            
#            listOfOptions = [];
#            self.__logger.debug(moduleOptionsRoot)
#            for option in moduleOptionsRoot:
#              option = [option.tag,option.text,option.get('unit')]
#              listOfOptions.append(option)
##              self.__logger.debug(option.tag + ": "+ option.text +"["+  option.get('unit')+"]");
#            return self.success({"data": listOfOptions})
#      
#      
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.user()
    @cherrypy.tools.workspace()
    def loadModuleOptions(self):
        json = cherrypy.request.json
        pathToBootstrap = json[u'pathToBootstrap']
        workspace_id = json[u'workspace_id']
        
        r = self.__getOfflineRpc(cherrypy.request.user, workspace_id)
        r.loadModuleOptions(pathToBootstrap)
      
      
      
      
      
      
      
      
      

